import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from Planta import Planta
from fuzzy_ctrl import fuzzy_ctrl
from pronostico_tiempo import PronosticoTiempo


if __name__ == "__main__":
    # ==== CONFIGURACION DE SIMULACION ==== 
    # ---- Pronosticador ----
    pt = PronosticoTiempo(temp_media = 20.0,
                          amp_anual = 12.0,
                          amp_diaria = 7.0,
                          dia_pico_verano = 15,
                          hora_pico_diario = 16.0)
    
    # ---- Planta ----
    R = 1728           # Resistencia térmica mínima (Ventana 100% abierta)
    Rv_min = 0         # R adicional mínima
    Rv_max = 15552     # R adicional máxima (Ventana 0% abierta / sellada)
    C = 1              # Capacitancia térmica de la habitación

    n_puntos = 48       # Puntos por dia
    dt_segundos = 3600 * 24 / n_puntos  # dt en segundos
    tiempo_horas = np.array([i * dt_segundos / 3600 for i in range(n_puntos)])  # Tiempo en horas

    planta = Planta(R, Rv_max, C, dt_segundos)
    
    # ---- Controlador Difuso ----
    # Condiciones del sistema
    V_obj = 25              # Setpoint: Temperatura de confort (°C)
    V_actual_inicial = 22   # Condición inicial de la habitación (°C)

    # ---- Condiciones de Simulacion ----
    mes_simulacion = 3              # 1 = Enero (verano), 7 = Julio (invierno)
    dia_inicial_simulacion = 15     # Dia que empezamos
    dias_simulacion = 7             # Simulamos una semana
    
    # Contiene temperaturas del primer dia (condiciones iniciales)
    temperaturas_exteriores = np.array(pt.obtener_temperaturas_dia(dia_inicial_simulacion, mes_simulacion, n_puntos))

    ctrl = fuzzy_ctrl(V_obj, temperaturas_exteriores[0], V_actual_inicial, estrategia="base")

    # ==== SIMULACIÓN (CONTROL DINÁMICO) ====
    print("Iniciando simulación del sistema térmico...")

    # Vectores de almacenamiento para el historial de simulación
    V_actual = V_actual_inicial # Temperatura actual
    T_controlada = [V_actual]   # Vector con temperaturas controladas
    aperturas = [0]             # Vector con aperturas

    for dia in range(dias_simulacion - 1):
        # Cambiar vector de temperaturas exteriores
        temperaturas_exteriores = np.array(pt.obtener_temperaturas_dia(dia, mes_simulacion, n_puntos))

        for i in range(n_puntos - 1):
            # Lectura de sensores (Actualización del controlador)
            ctrl.set_Ve(temperaturas_exteriores[i])
            ctrl.set_V(V_actual)
            
            # Cálculo de la acción de control (Inferencia Difusa)
            apertura = ctrl.control()
            aperturas.append(apertura)

            # Dinámica de la planta (Aplicar apertura y calcular siguiente estado)
            V_sig = planta.paso(V_actual, apertura, temperaturas_exteriores[i])
            
            # Actualización de estado
            V_actual = V_sig
            T_controlada.append(V_sig)

    # ==========================================
    # 4. CÁLCULO DE MÉTRICAS DE RENDIMIENTO (KPIs)
    # ==========================================
    
    # Error RMS: Mide la desviación global respecto a la temperatura de confort
    error_array = np.array(T_controlada) - V_obj
    rms_error = np.sqrt(np.mean(np.square(error_array)))
    
    print("\n=== RESULTADOS DE LA SIMULACIÓN ===")
    print(f"Estrategia utilizada : Base")
    print(f"Error RMS            : {rms_error:.3f} °C")
    print("===================================\n")

    # ==========================================
    # 5. VISUALIZACIÓN DE RESULTADOS (DASHBOARD)
    # ==========================================
    fig = plt.figure(figsize=(14, 10))

    gs = GridSpec(2, 3, height_ratios=[1, 1.5], figure=fig)

    # --- 5.1 Fila Superior: Visualización del Modelo Matemático Difuso ---
    ax_err = fig.add_subplot(gs[0, 0])
    ax_dt  = fig.add_subplot(gs[0, 1])
    ax_ap  = fig.add_subplot(gs[0, 2])

    # Se extraen los vectores manualmente para evitar el bug de figuras múltiples de skfuzzy
    def graficar_membresia_manual(variable_difusa, ax, titulo):
        for label, term in variable_difusa.terms.items():
            ax.plot(variable_difusa.universe, term.mf, label=label, linewidth=2)
            ax.fill_between(variable_difusa.universe, 0, term.mf, alpha=0.2)
        ax.set_title(titulo, fontweight='bold', fontsize=10)
        ax.legend(fontsize=8)
        ax.grid(True, linestyle=':', alpha=0.6)

    graficar_membresia_manual(ctrl.err, ax_err, "Antecedente: Error (V - Vobj)")
    graficar_membresia_manual(ctrl.dT, ax_dt, "Antecedente: Delta T (Ve - V)")
    graficar_membresia_manual(ctrl.apertura, ax_ap, "Consecuente: Apertura (%)")

    # --- 5.2 Fila Inferior: Simulación Temporal ---
    ax_sim = fig.add_subplot(gs[1, :]) 
    ax_sim_ap = ax_sim.twinx()         

    c_text = "#1f77b4" # Azul (Exterior)
    c_tint = "#d62728" # Rojo (Interior)
    c_tobj = "#2ca02c" # Verde (Setpoint)
    c_aper = "#ff7f0e" # Naranja (Apertura)

    ax_sim.plot(tiempo_horas, temperaturas_exteriores, '*', color=c_text, alpha=0.6, label='T Exterior')
    ax_sim.plot(tiempo_horas, T_controlada, linewidth=2.5, color=c_tint, label='T Interior controlada')
    ax_sim.axhline(V_obj, color=c_tobj, linestyle='--', linewidth=2, label='Setpoint (Confort 25°C)')
    
    ax_sim_ap.fill_between(tiempo_horas, 0, aperturas, color=c_aper, alpha=0.15, label='Apertura de Ventana')
    ax_sim_ap.plot(tiempo_horas, aperturas, color=c_aper, linewidth=1.5, alpha=0.8)
    
    # --- ESCALADO DINÁMICO DE EJES Y ---
    # Buscamos el valor más frío y el más caliente de toda la simulación (incluyendo el objetivo)
    temp_min = min(np.min(temperaturas_exteriores), np.min(T_controlada), V_obj)
    temp_max = max(np.max(temperaturas_exteriores), np.max(T_controlada), V_obj)
    
    # Agregamos 2 grados de margen arriba y abajo para que las curvas no toquen los bordes del gráfico
    ax_sim.set_ylim(temp_min - 2, temp_max + 2)      
    ax_sim_ap.set_ylim(0, 105)   
    
    ax_sim.set_ylabel("Temperatura (°C)", fontsize=12, fontweight='bold')
    ax_sim_ap.set_ylabel("Nivel de Apertura (%)", fontsize=12, color=c_aper, fontweight='bold')
    ax_sim.set_xlabel("Hora del Día", fontsize=12, fontweight='bold')
    ax_sim.grid(True, linestyle='--', alpha=0.7)
    
    lines_1, labels_1 = ax_sim.get_legend_handles_labels()
    lines_2, labels_2 = ax_sim_ap.get_legend_handles_labels()
    ax_sim.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4, frameon=True)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15, top=0.92)
    plt.show()