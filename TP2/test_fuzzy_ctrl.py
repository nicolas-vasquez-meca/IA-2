import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from Planta import Planta
from fuzzy_ctrl import fuzzy_ctrl
from pronostico_tiempo import PronosticoTiempo
import numpy as np

if __name__ == "__main__":

    # --- 1. Configuración Inicial ---
    n_puntos = 48
    pt = PronosticoTiempo()
    temperaturas = np.array(pt.obtener_temperaturas_dia(1, 2, n_puntos))

    R = 1728
    Rv_min = 0
    Rv_max = 15552
    C = 1
    
    dt_segundos = 3600 * 24 / n_puntos
    tiempo_horas = np.array([i * dt_segundos / 3600 for i in range(n_puntos)])

    V_obj = 25
    V_actual_inicial = 22

    estrategias = ["base", "gaussiana", "banda_muerta"]
    resultados = {}
    controladores = {} # Guardamos los objetos para plotear sus funciones luego

    print("=== ANÁLISIS DE RENDIMIENTO DEL CONTROLADOR DIFUSO ===")
    print(f"{'Estrategia':<15} | {'Error RMS (°C)':<15} | {'Esfuerzo Mecánico (%)':<20}")
    print("-" * 55)

    # --- 2. Bucle de Simulación ---
    for est in estrategias:
        planta = Planta(R, Rv_max, C, dt_segundos)
        ctrl = fuzzy_ctrl(V_obj, temperaturas[0], V_actual_inicial, estrategia=est)
        controladores[est] = ctrl  # Guardar referencia para graficar después
        
        V_actual = V_actual_inicial
        T_controlada = [V_actual]
        aperturas = [0]
        
        for i in range(n_puntos - 1):
            ctrl.set_Ve(temperaturas[i])
            ctrl.set_V(V_actual)
            apertura = ctrl.control()
            aperturas.append(apertura)

            V_sig = planta.paso(V_actual, apertura, temperaturas[i])
            V_actual = V_sig
            T_controlada.append(V_sig)
            
        error_array = np.array(T_controlada) - V_obj
        rms_error = np.sqrt(np.mean(np.square(error_array)))
        esfuerzo = np.sum(np.abs(np.diff(aperturas)))
        
        resultados[est] = {
            "T_controlada": T_controlada,
            "aperturas": aperturas,
            "rms": rms_error,
            "esfuerzo": esfuerzo
        }
        
        print(f"{est.capitalize():<15} | {rms_error:<15.3f} | {esfuerzo:<20.1f}")

    # --- 3. Visualización Gráfica (3 Figuras Separadas) ---
    c_text = "#1f77b4" # Azul
    c_tint = "#d62728" # Rojo
    c_tobj = "#2ca02c" # Verde
    c_aper = "#ff7f0e" # Naranja

    for est in estrategias:
        # Creamos una figura grande por cada estrategia
        fig = plt.figure(figsize=(14, 10))
        fig.suptitle(f"Estrategia: {est.capitalize()} | Error RMS: {resultados[est]['rms']:.2f} °C", fontsize=16, fontweight='bold')

        # Definimos la grilla: 2 filas, 3 columnas. La fila inferior es un poco más alta (1.5)
        gs = GridSpec(2, 3, height_ratios=[1, 1.5], figure=fig)

        # -- Fila Superior: Funciones de Pertenencia --
        ax_err = fig.add_subplot(gs[0, 0])
        ax_dt  = fig.add_subplot(gs[0, 1])
        ax_ap_mf = fig.add_subplot(gs[0, 2])

        ctrl = controladores[est]

        # 1. Graficar Error
        for label, term in ctrl.err.terms.items():
            ax_err.plot(ctrl.err.universe, term.mf, label=label, linewidth=2)
            ax_err.fill_between(ctrl.err.universe, 0, term.mf, alpha=0.2)
        ax_err.set_title("Membresías: Error (V - Vobj)")
        ax_err.legend(fontsize=8)

        # 2. Graficar Delta T
        for label, term in ctrl.dT.terms.items():
            ax_dt.plot(ctrl.dT.universe, term.mf, label=label, linewidth=2)
            ax_dt.fill_between(ctrl.dT.universe, 0, term.mf, alpha=0.2)
        ax_dt.set_title("Membresías: Delta T (Ve - V)")
        ax_dt.legend(fontsize=8)

        # 3. Graficar Apertura
        for label, term in ctrl.apertura.terms.items():
            ax_ap_mf.plot(ctrl.apertura.universe, term.mf, label=label, linewidth=2)
            ax_ap_mf.fill_between(ctrl.apertura.universe, 0, term.mf, alpha=0.2)
        ax_ap_mf.set_title("Membresías: Apertura")
        ax_ap_mf.legend(fontsize=8)

        # Sobrescribimos los títulos por defecto para mayor claridad
        ax_err.set_title("Membresías: Error (V - Vobj)")
        ax_dt.set_title("Membresías: Delta T (Ve - V)")
        ax_ap_mf.set_title("Membresías: Apertura")

        # -- Fila Inferior: Simulación de Temperaturas --
        ax_sim = fig.add_subplot(gs[1, :]) # El ':' le indica que ocupe las 3 columnas
        ax_sim_ap = ax_sim.twinx()

        # Ploteo de Temperaturas
        ax_sim.plot(tiempo_horas, temperaturas, '*', color=c_text, alpha=0.5, label='T Exterior')
        ax_sim.plot(tiempo_horas, resultados[est]["T_controlada"], linewidth=2.5, color=c_tint, label='T Interior')
        ax_sim.axhline(V_obj, color=c_tobj, linestyle='--', linewidth=2, label='Confort (25°C)')
        
        # Ploteo de Apertura
        ax_sim_ap.fill_between(tiempo_horas, 0, resultados[est]["aperturas"], color=c_aper, alpha=0.15, label='Apertura %')
        ax_sim_ap.plot(tiempo_horas, resultados[est]["aperturas"], color=c_aper, linewidth=1.5, alpha=0.8)
        
        # Ajustes de Ejes
        ax_sim.set_ylim(15, 35)      
        ax_sim_ap.set_ylim(0, 105)   
        
        ax_sim.set_ylabel("Temperatura (°C)", fontsize=11)
        ax_sim_ap.set_ylabel("Apertura (%)", fontsize=11, color=c_aper)
        ax_sim.set_xlabel("Tiempo (Horas del día)", fontsize=12)
        ax_sim.grid(True, linestyle=':', alpha=0.7)
        
        # Unificación de Leyenda
        lines_1, labels_1 = ax_sim.get_legend_handles_labels()
        lines_2, labels_2 = ax_sim_ap.get_legend_handles_labels()
        ax_sim.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', ncol=4, fontsize=9)

        plt.tight_layout()

    # Mostramos las 3 ventanas al mismo tiempo
    plt.show()