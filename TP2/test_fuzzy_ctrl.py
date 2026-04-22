import matplotlib.pyplot as plt
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
    
    # dt_minutos en realidad está en SEGUNDOS (24h * 3600s / n_puntos)
    dt_segundos = 3600 * 24 / n_puntos
    
    # Vector de tiempo en HORAS para el eje X
    tiempo_horas = np.array([i * dt_segundos / 3600 for i in range(n_puntos)])

    V_obj = 25
    V_actual_inicial = 22

    # --- 2. Bucle de Simulación por Estrategia ---
    estrategias = ["base", "gaussiana", "banda_muerta"]
    resultados = {}

    print("=== ANÁLISIS DE RENDIMIENTO DEL CONTROLADOR DIFUSO ===")
    print(f"{'Estrategia':<15} | {'Error RMS (°C)':<15} | {'Esfuerzo Mecánico (%)':<20}")
    print("-" * 55)

    for est in estrategias:
        planta = Planta(R, Rv_max, C, dt_segundos)
        ctrl = fuzzy_ctrl(V_obj, temperaturas[0], V_actual_inicial, estrategia=est)
        
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
            
        # Cálculo del Error RMS correcto
        error_array = np.array(T_controlada) - V_obj
        rms_error = np.sqrt(np.mean(np.square(error_array)))
        
        # Cálculo del Esfuerzo de Control (Sumatoria de variaciones de la ventana)
        esfuerzo = np.sum(np.abs(np.diff(aperturas)))
        
        resultados[est] = {
            "T_controlada": T_controlada,
            "aperturas": aperturas,
            "rms": rms_error,
            "esfuerzo": esfuerzo
        }
        
        print(f"{est.capitalize():<15} | {rms_error:<15.3f} | {esfuerzo:<20.1f}")

    # --- 3. Visualización Gráfica ---
    # Creamos 3 subplots apilados (compartiendo el eje X)
    fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    fig.suptitle("Comparativa de Estrategias de Lógica Difusa", fontsize=16, fontweight='bold')

    # Paleta de colores llamativos y profesionales
    c_text = "#1f77b4" # Azul
    c_tint = "#d62728" # Rojo
    c_tobj = "#2ca02c" # Verde Oscuro (Confort)
    c_aper = "#ff7f0e" # Naranja

    for idx, est in enumerate(estrategias):
        ax = axs[idx]
        ax_ap = ax.twinx()  # Creamos el eje Y secundario para la apertura
        
        # Ploteo de Temperaturas (Eje Izquierdo)
        ax.plot(tiempo_horas, temperaturas, '*', color=c_text, alpha=0.5, label='T Exterior')
        ax.plot(tiempo_horas, resultados[est]["T_controlada"], linewidth=2.5, color=c_tint, label='T Interior')
        ax.axhline(V_obj, color=c_tobj, linestyle='--', linewidth=2, label='Confort (25°C)')
        
        # Ploteo de Apertura (Eje Derecho - Superpuesto)
        # Usamos fill_between para crear un área sombreada que sea fácil de leer de fondo
        ax_ap.fill_between(tiempo_horas, 0, resultados[est]["aperturas"], color=c_aper, alpha=0.15, label='Apertura %')
        ax_ap.plot(tiempo_horas, resultados[est]["aperturas"], color=c_aper, linewidth=1.5, alpha=0.8)
        
        # Configuración de límites y etiquetas
        ax.set_ylim(15, 35)      # Rango térmico sugerido (ajustar si hace más frío)
        ax_ap.set_ylim(0, 105)   # La apertura va de 0 a 100%
        
        ax.set_ylabel("Temperatura (°C)", fontsize=11)
        ax_ap.set_ylabel("Apertura (%)", fontsize=11, color=c_aper)
        ax.set_title(f"Estrategia: {est.capitalize()}  |  Error RMS: {resultados[est]['rms']:.2f} °C", fontweight='bold')
        ax.grid(True, linestyle=':', alpha=0.7)
        
        # Colocar la leyenda solo en el primer gráfico para no saturar la imagen
        if idx == 0:
            lines_1, labels_1 = ax.get_legend_handles_labels()
            lines_2, labels_2 = ax_ap.get_legend_handles_labels()
            # Unimos ambas leyendas en la esquina superior izquierda
            ax.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', ncol=4, fontsize=9)

    axs[2].set_xlabel("Tiempo (Horas del día)", fontsize=12)
    plt.tight_layout()
    plt.subplots_adjust(top=0.92) # Espacio para el título principal
    plt.show()