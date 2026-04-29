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

    planta = Planta(R, Rv_max, C, dt_segundos)
    
    # ---- Controlador Difuso ----
    # Condiciones del sistema
    V_obj = 25              # Setpoint: Temperatura de confort (°C)
    V_actual_inicial = 22   # Condición inicial de la habitación (°C)

    # ---- Condiciones de Simulacion ----
    mes_simulacion = 3              # 1 = Enero (verano), 7 = Julio (invierno)
    dia_inicial_simulacion = 15     # Dia que empezamos
    dias_simulacion = 7           # Simulamos una semana
    
    # Generar vector completo de temperaturas para toda la semana
    temperaturas_exteriores_totales = []
    for dia in range(dia_inicial_simulacion, dia_inicial_simulacion + dias_simulacion):
        temps_dia = pt.obtener_temperaturas_dia(dia, mes_simulacion, n_puntos)
        temperaturas_exteriores_totales.extend(temps_dia)
        
    temperaturas_exteriores_totales = np.array(temperaturas_exteriores_totales)
    total_puntos = len(temperaturas_exteriores_totales) # Serán 48 * 7 = 336 puntos
    
    # ]El vector de tiempo ahora abarca toda la semana (168 horas)
    tiempo_dias = np.array([i * dt_segundos / (3600 * 24) for i in range(total_puntos)])

    # Estrategia puede ser:
    # 1. base
    # 2. banda_muerta
    # 3. gaussiana
    ctrl = fuzzy_ctrl(V_obj, temperaturas_exteriores_totales[0], V_actual_inicial, estrategia="gaussiana")
    
    # ==== SIMULACIÓN (CONTROL DINÁMICO) ====
    print("Iniciando simulación del sistema térmico...")

    # Vectores de almacenamiento para el historial de simulación
    V_actual = V_actual_inicial # Temperatura actual
    T_controlada = []           # Vector con temperaturas controladas
    aperturas = []              # Vector con aperturas

    for i in range(total_puntos):
        Ve = temperaturas_exteriores_totales[i]
        
        # Lectura de sensores (Actualización del controlador)
        ctrl.set_Ve(Ve)
        ctrl.set_V(V_actual)
        
        # Cálculo de la acción de control (Inferencia Difusa)
        apertura = ctrl.control()
        
        # Guardamos el estado actual ANTES de que evolucione la planta
        aperturas.append(apertura)
        T_controlada.append(V_actual)

        # Dinámica de la planta (Aplicar apertura y calcular siguiente estado)
        V_sig = planta.paso(V_actual, apertura, Ve)
        
        # Actualización de estado
        V_actual = V_sig

    T_controlada = np.array(T_controlada)
    aperturas = np.array(aperturas)


    # ==========================================
    # 4. CÁLCULO DE MÉTRICAS DE RENDIMIENTO (KPIs)
    # ==========================================
    error_array = T_controlada - V_obj
    rms_error = np.sqrt(np.mean(np.square(error_array)))
    
    print("\n=== RESULTADOS DE LA SIMULACIÓN ===")
    print(f"Estrategia utilizada : {ctrl.estrategia}")
    print(f"Días simulados       : {dias_simulacion}")
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
    # --- 5.2 Fila Inferior: Simulación Temporal ---
    ax_sim = fig.add_subplot(gs[1, :]) 
    ax_sim_ap = ax_sim.twinx()         

    c_text = "#1f77b4" # Azul (Exterior)
    c_tint = "#d62728" # Rojo (Interior)
    c_tobj = "#2ca02c" # Verde (Setpoint)
    c_aper = "#ff7f0e" # Naranja (Apertura)

    # Reemplazamos tiempo_horas por tiempo_dias
    ax_sim.plot(tiempo_dias, temperaturas_exteriores_totales, '*', color=c_text, alpha=0.6, label='T Exterior')
    ax_sim.plot(tiempo_dias, T_controlada, linewidth=2.5, color=c_tint, label='T Interior controlada')
    ax_sim.axhline(V_obj, color=c_tobj, linestyle='--', linewidth=2, label='Setpoint (Confort 25°C)')
    
    ax_sim_ap.fill_between(tiempo_dias, 0, aperturas, color=c_aper, alpha=0.15, label='Apertura de Ventana')
    ax_sim_ap.plot(tiempo_dias, aperturas, color=c_aper, linewidth=1.5, alpha=0.8)
    
    # --- ESCALADO DINÁMICO DE EJES Y ---
    temp_min = min(np.min(temperaturas_exteriores_totales), np.min(T_controlada), V_obj)
    temp_max = max(np.max(temperaturas_exteriores_totales), np.max(T_controlada), V_obj)
    
    ax_sim.set_ylim(temp_min - 2, temp_max + 2)      
    ax_sim_ap.set_ylim(0, 105)   
    
    ax_sim.set_ylabel("Temperatura (°C)", fontsize=12, fontweight='bold')
    ax_sim_ap.set_ylabel("Nivel de Apertura (%)", fontsize=12, color=c_aper, fontweight='bold')
    
    # --- CONFIGURACIÓN DEL EJE X (DÍAS) ---
    ax_sim.set_xlabel("Tiempo (Días de simulación)", fontsize=12, fontweight='bold')
    
    # Forzamos a que el eje X ponga una marca exactamente en cada día entero (0, 1, 2... 7)
    ax_sim.set_xticks(np.arange(0, dias_simulacion + 1, 1))
    
    # Añadimos líneas divisorias verticales por cada día para mayor claridad
    for d in range(1, dias_simulacion):
        ax_sim.axvline(x=d, color='gray', linestyle=':', alpha=0.5, linewidth=1.5)

    ax_sim.grid(True, linestyle='--', alpha=0.7)
    
    lines_1, labels_1 = ax_sim.get_legend_handles_labels()
    lines_2, labels_2 = ax_sim_ap.get_legend_handles_labels()
    ax_sim.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4, frameon=True)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15, top=0.92)
    plt.show()