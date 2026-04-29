import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

directorio_actual = os.path.dirname(os.path.abspath(__file__))
directorio_padre = os.path.dirname(directorio_actual)
sys.path.append(directorio_padre)

from Planta import Planta
from fuzzy_ctrl_pronostico_2 import fuzzy_ctrl
from pronostico_tiempo import PronosticoTiempo



def graficar_membresia_manual(variable_difusa, ax, titulo):
    for label, term in variable_difusa.terms.items():
        ax.plot(variable_difusa.universe, term.mf, label=label, linewidth=2)
        ax.fill_between(variable_difusa.universe, 0, term.mf, alpha=0.2)
    ax.set_title(titulo, fontweight='bold', fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(True, linestyle=':', alpha=0.6)


if __name__ == "__main__":
    # --- Configuración Inicial ---
    n_puntos = 48
    horizonte_pred_horas = 12.0

    # ---- Pronosticador ----
    pt = PronosticoTiempo(temp_media=20.0,
                          amp_anual=12.0,
                          amp_diaria=7.0,
                          dia_pico_verano=15,
                          hora_pico_diario=16.0)
    
    dia_inicial_simulacion = 15
    mes_simulacion = 3
    dias_simulacion = 7

    R = 1728
    Rv_max = 15552
    C = 1

    dt_segundos = 3600 * 24 / n_puntos
    dt_horas = dt_segundos / 3600
    pasos_pred = max(1, int(round(horizonte_pred_horas / dt_horas)))

    # Generar vector extendido: Días de simulación + 1 día extra para el horizonte del último día
    temperaturas_ext = []
    for dia in range(dia_inicial_simulacion, dia_inicial_simulacion + dias_simulacion + 1):
        temps_dia = pt.obtener_temperaturas_dia(dia, mes_simulacion, n_puntos)
        temperaturas_ext.extend(temps_dia)
    
    temperaturas_ext = np.array(temperaturas_ext)
    
    # Cortar los vectores estrictamente para la ventana de simulación (7 días)
    total_puntos = n_puntos * dias_simulacion
    temperaturas_simulacion = temperaturas_ext[:total_puntos]
    
    # Vectores de tiempo
    tiempo_horas_continuas = np.array([i * dt_horas for i in range(total_puntos)])
    tiempo_dias = tiempo_horas_continuas / 24

    # Vector de predicción a horizonte fijo
    temperaturas_predichas = np.empty_like(temperaturas_simulacion)
    for i in range(total_puntos):
        idx = i + pasos_pred
        # Gracias al día extra descargado, idx nunca se sale de rango
        temperaturas_predichas[i] = temperaturas_ext[idx]

    V_obj = 25
    V_actual_inicial = 22

    print("=== CONTROL DIFUSO CON PRONÓSTICO ===")
    print(f"Horizonte de predicción: {horizonte_pred_horas:.1f} h")
    print(f"Días simulados         : {dias_simulacion}")

    # --- 2. Simulación ---
    planta = Planta(R, Rv_max, C, dt_segundos)
    
    ctrl = fuzzy_ctrl(
        V_obj,
        temperaturas_simulacion[0],
        V_actual_inicial,
        estrategia="pronostico",
        hora=0.0, # Arrancamos a la hora 0
        T_predicha=temperaturas_predichas[0],
    )

    V_actual = V_actual_inicial
    T_controlada = []
    aperturas = []
    z_hist = []

    for i in range(total_puntos):
        Ve = temperaturas_simulacion[i]
        T_pred = temperaturas_predichas[i]
        
        # Extraemos la hora del día (0-24) usando el módulo para el modelo difuso
        hora_del_dia = tiempo_horas_continuas[i] % 24
        
        ctrl.set_Ve(Ve)
        ctrl.set_V(V_actual)
        ctrl.set_hora(hora_del_dia)
        ctrl.set_T_predicha(T_pred)

        apertura = ctrl.control()
        
        # Guardado de variables
        aperturas.append(apertura)
        T_controlada.append(V_actual)
        z_hist.append((V_actual - V_obj) * (Ve - V_actual))

        # Dinámica de la planta
        V_sig = planta.paso(V_actual, apertura, Ve)
        V_actual = V_sig

    T_controlada = np.array(T_controlada)
    aperturas = np.array(aperturas)
    z_hist = np.array(z_hist)

    # --- 3. Métricas ---
    error_array = T_controlada - V_obj
    rms_error = np.sqrt(np.mean(np.square(error_array)))

    # Métrica J: Ahora sumamos de forma discreta para evitar "trapecios fantasma" entre días
    vector_horas_del_dia = tiempo_horas_continuas % 24
    mask_confort = (vector_horas_del_dia >= 8) & (vector_horas_del_dia <= 20)
    
    # Sumatoria del error ponderada por el paso temporal dividido por las horas totales de confort
    horas_confort_totales = (20 - 8) * dias_simulacion
    J = np.sum(error_array[mask_confort] * dt_horas) / horas_confort_totales

    esfuerzo = np.sum(np.abs(np.diff(aperturas)))

    print(f"Error RMS            : {rms_error:.3f} °C")
    print(f"Métrica J (8-20 hs)  : {J:.3f} °C")
    print(f"Esfuerzo mecánico    : {esfuerzo:.1f} %")

    # --- 4. Visualización ---
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle(
        f"Control Difuso Predictivo ({dias_simulacion} Días) | RMS: {rms_error:.2f} °C | J: {J:.2f} °C",
        fontsize=16,
        fontweight='bold',
    )

    gs = GridSpec(2, 4, height_ratios=[1, 1.6], figure=fig)

    ax_z = fig.add_subplot(gs[0, 0])
    ax_hora = fig.add_subplot(gs[0, 1])
    ax_tpred = fig.add_subplot(gs[0, 2])
    ax_ap = fig.add_subplot(gs[0, 3])

    graficar_membresia_manual(ctrl.z, ax_z, "Antecedente: Z")
    graficar_membresia_manual(ctrl.hora, ax_hora, "Antecedente: Hora (0-24)")
    graficar_membresia_manual(ctrl.t_pred, ax_tpred, "Antecedente: T predicha")
    graficar_membresia_manual(ctrl.apertura, ax_ap, "Consecuente: Apertura (%)")

    ax_sim = fig.add_subplot(gs[1, :])
    ax_sim_ap = ax_sim.twinx()

    c_text = "#1f77b4"
    c_tpred = "#9467bd"
    c_tint = "#d62728"
    c_tobj = "#2ca02c"
    c_aper = "#ff7f0e"

    # Ploteamos usando tiempo_dias en el eje X
    ax_sim.plot(tiempo_dias, temperaturas_simulacion, '*', color=c_text, alpha=0.55, label='T exterior')
    ax_sim.plot(tiempo_dias, temperaturas_predichas, '--', color=c_tpred, linewidth=1.8, label='T predicha')
    ax_sim.plot(tiempo_dias, T_controlada, linewidth=2.6, color=c_tint, label='T interior')
    ax_sim.axhline(V_obj, color=c_tobj, linestyle='--', linewidth=2, label='Confort 25 °C')
    
    # Dibujar la franja de confort gris para cada día individual
    for d in range(dias_simulacion):
        inicio_confort = d + (8 / 24)
        fin_confort = d + (20 / 24)
        # Solo le ponemos label al primer recuadro para no ensuciar la leyenda
        lbl = 'Ventana J (8-20h)' if d == 0 else None
        ax_sim.axvspan(inicio_confort, fin_confort, color='gray', alpha=0.08, label=lbl)

    ax_sim_ap.fill_between(tiempo_dias, 0, aperturas, color=c_aper, alpha=0.16, label='Apertura %')
    ax_sim_ap.plot(tiempo_dias, aperturas, color=c_aper, linewidth=1.5, alpha=0.85)

    temp_min = min(np.min(temperaturas_simulacion), np.min(temperaturas_predichas), np.min(T_controlada), V_obj)
    temp_max = max(np.max(temperaturas_simulacion), np.max(temperaturas_predichas), np.max(T_controlada), V_obj)
    ax_sim.set_ylim(temp_min - 2, temp_max + 2)
    ax_sim_ap.set_ylim(0, 105)

    ax_sim.set_ylabel('Temperatura (°C)', fontsize=12, fontweight='bold')
    ax_sim_ap.set_ylabel('Apertura (%)', fontsize=12, color=c_aper, fontweight='bold')
    ax_sim.set_xlabel('Tiempo (Días de simulación)', fontsize=12, fontweight='bold')
    
    # Grilla del eje X alineada a los días
    ax_sim.set_xticks(np.arange(0, dias_simulacion + 1, 1))
    for d in range(1, dias_simulacion):
        ax_sim.axvline(x=d, color='gray', linestyle=':', alpha=0.5, linewidth=1.5)
        
    ax_sim.grid(True, linestyle='--', alpha=0.7)

    lines_1, labels_1 = ax_sim.get_legend_handles_labels()
    lines_2, labels_2 = ax_sim_ap.get_legend_handles_labels()
    ax_sim.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', ncol=3, fontsize=9)

    plt.tight_layout()
    plt.show()