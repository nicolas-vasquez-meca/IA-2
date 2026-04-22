import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from Planta import Planta
from fuzzy_ctrl_pronostico_2 import fuzzy_ctrl
from pronostico_tiempo import PronosticoTiempo
import numpy as np


def graficar_membresia_manual(variable_difusa, ax, titulo):
    for label, term in variable_difusa.terms.items():
        ax.plot(variable_difusa.universe, term.mf, label=label, linewidth=2)
        ax.fill_between(variable_difusa.universe, 0, term.mf, alpha=0.2)
    ax.set_title(titulo, fontweight='bold', fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(True, linestyle=':', alpha=0.6)


if __name__ == "__main__":
    # --- 1. Configuración Inicial ---
    n_puntos = 48
    horizonte_pred_horas = 4.0

    pt = PronosticoTiempo()
    temperaturas = np.array(pt.obtener_temperaturas_dia(1, 2, n_puntos))

    R = 1728
    Rv_max = 15552
    C = 1

    dt_segundos = 3600 * 24 / n_puntos
    tiempo_horas = np.array([i * dt_segundos / 3600 for i in range(n_puntos)])

    pasos_pred = max(1, int(round(horizonte_pred_horas / (dt_segundos / 3600))))
    temperaturas_predichas = np.empty_like(temperaturas)
    for i in range(n_puntos):
        idx = min(i + pasos_pred, n_puntos - 1)
        temperaturas_predichas[i] = temperaturas[idx]

    V_obj = 25
    V_actual_inicial = 30

    print("=== CONTROL DIFUSO CON PRONÓSTICO ===")
    print(f"Horizonte de predicción: {horizonte_pred_horas:.1f} h")

    # --- 2. Simulación ---
    planta = Planta(R, Rv_max, C, dt_segundos)
    ctrl = fuzzy_ctrl(
        V_obj,
        temperaturas[0],
        V_actual_inicial,
        estrategia="pronostico",
        hora=tiempo_horas[0],
        T_predicha=temperaturas_predichas[0],
    )

    V_actual = V_actual_inicial
    T_controlada = [V_actual]
    aperturas = [0.0]
    z_hist = [(V_actual - V_obj) * (temperaturas[0] - V_actual)]

    for i in range(n_puntos - 1):
        ctrl.set_Ve(temperaturas[i])
        ctrl.set_V(V_actual)
        ctrl.set_hora(tiempo_horas[i])
        ctrl.set_T_predicha(temperaturas_predichas[i])

        apertura = ctrl.control()
        aperturas.append(apertura)

        V_sig = planta.paso(V_actual, apertura, temperaturas[i])
        V_actual = V_sig
        T_controlada.append(V_sig)
        z_hist.append((V_actual - V_obj) * (temperaturas[i] - V_actual))

    # --- 3. Métricas ---
    error_array = np.array(T_controlada) - V_obj
    rms_error = np.sqrt(np.mean(np.square(error_array)))

    mask_confort = (tiempo_horas >= 8) & (tiempo_horas <= 20)
    J = np.trapezoid(error_array[mask_confort], tiempo_horas[mask_confort]) / (20 - 8)

    esfuerzo = np.sum(np.abs(np.diff(aperturas)))

    print(f"Error RMS            : {rms_error:.3f} °C")
    print(f"Métrica J (8-20 hs)  : {J:.3f} °C")
    print(f"Esfuerzo mecánico    : {esfuerzo:.1f} %")

    # --- 4. Visualización ---
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle(
        f"Control Difuso con Pronóstico | RMS: {rms_error:.2f} °C | J: {J:.2f} °C",
        fontsize=16,
        fontweight='bold',
    )

    gs = GridSpec(2, 4, height_ratios=[1, 1.6], figure=fig)

    ax_z = fig.add_subplot(gs[0, 0])
    ax_hora = fig.add_subplot(gs[0, 1])
    ax_tpred = fig.add_subplot(gs[0, 2])
    ax_ap = fig.add_subplot(gs[0, 3])

    graficar_membresia_manual(ctrl.z, ax_z, "Antecedente: Z")
    graficar_membresia_manual(ctrl.hora, ax_hora, "Antecedente: Hora")
    graficar_membresia_manual(ctrl.t_pred, ax_tpred, "Antecedente: T predicha")
    graficar_membresia_manual(ctrl.apertura, ax_ap, "Consecuente: Apertura (%)")

    ax_sim = fig.add_subplot(gs[1, :])
    ax_sim_ap = ax_sim.twinx()

    c_text = "#1f77b4"
    c_tpred = "#9467bd"
    c_tint = "#d62728"
    c_tobj = "#2ca02c"
    c_aper = "#ff7f0e"

    ax_sim.plot(tiempo_horas, temperaturas, '*', color=c_text, alpha=0.55, label='T exterior')
    ax_sim.plot(tiempo_horas, temperaturas_predichas, '--', color=c_tpred, linewidth=1.8, label='T predicha')
    ax_sim.plot(tiempo_horas, T_controlada, linewidth=2.6, color=c_tint, label='T interior')
    ax_sim.axhline(V_obj, color=c_tobj, linestyle='--', linewidth=2, label='Confort 25 °C')
    ax_sim.axvspan(8, 20, color='gray', alpha=0.08, label='Ventana J')

    ax_sim_ap.fill_between(tiempo_horas, 0, aperturas, color=c_aper, alpha=0.16, label='Apertura %')
    ax_sim_ap.plot(tiempo_horas, aperturas, color=c_aper, linewidth=1.5, alpha=0.85)

    temp_min = min(np.min(temperaturas), np.min(temperaturas_predichas), np.min(T_controlada), V_obj)
    temp_max = max(np.max(temperaturas), np.max(temperaturas_predichas), np.max(T_controlada), V_obj)
    ax_sim.set_ylim(temp_min - 2, temp_max + 2)
    ax_sim_ap.set_ylim(0, 105)

    ax_sim.set_ylabel('Temperatura (°C)', fontsize=12, fontweight='bold')
    ax_sim_ap.set_ylabel('Apertura (%)', fontsize=12, color=c_aper, fontweight='bold')
    ax_sim.set_xlabel('Hora del día', fontsize=12, fontweight='bold')
    ax_sim.grid(True, linestyle='--', alpha=0.7)

    lines_1, labels_1 = ax_sim.get_legend_handles_labels()
    lines_2, labels_2 = ax_sim_ap.get_legend_handles_labels()
    ax_sim.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', ncol=3, fontsize=9)

    plt.tight_layout()
    plt.show()
