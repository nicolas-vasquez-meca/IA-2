import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt

def graficar_defusificacion_centroide():
    """
    Genera un gráfico explicativo de alta calidad para presentaciones 
    mostrando el proceso de inferencia, recorte (clipping) y defusificación 
    por Centroide para la variable de Apertura de Ventana.
    """
    
    # --- 1. Definición del Universo y Funciones de Pertenencia ---
    x_aper = np.arange(0, 101, 1) # Universo de apertura: 0% a 100%

    # Funciones de pertenencia del Consecuente (con los hombros que definimos)
    aper_OFF = fuzz.trapmf(x_aper, [0, 0, 0, 50])
    aper_MID = fuzz.trimf(x_aper, [40, 50, 60])
    aper_ON  = fuzz.trapmf(x_aper, [50, 100, 100, 100])

    # --- 2. Caso de Aplicación: Niveles de Activación de las Reglas ---
    # Escenario: T_int = 26.5°C, T_ext = 15°C
    activacion_OFF = 0.0  # No hace falta cerrar
    activacion_MID = 0.4  # Se activa parcialmente porque estamos cerca de 25°C
    activacion_ON  = 0.8  # Se activa fuertemente para dejar entrar el frío

    # --- 3. Inferencia Lógica (Recorte / Clipping de Mamdani) ---
    # La función fmin recorta la "punta" de la figura geométrica
    aper_OFF_clip = np.fmin(activacion_OFF, aper_OFF)
    aper_MID_clip = np.fmin(activacion_MID, aper_MID)
    aper_ON_clip  = np.fmin(activacion_ON, aper_ON)

    # --- 4. Agregación (Unión de todas las figuras recortadas) ---
    # La función fmax fusiona las áreas en una sola figura geométrica sólida
    aper_agregada = np.fmax(aper_OFF_clip, np.fmax(aper_MID_clip, aper_ON_clip))

    # --- 5. Defusificación (Cálculo del Centroide) ---
    centroide_x = fuzz.defuzz(x_aper, aper_agregada, 'centroid')
    
    # Obtenemos la altura de la figura en el punto del centroide para graficar la línea
    centroide_y = fuzz.interp_membership(x_aper, aper_agregada, centroide_x)

    # ==========================================
    # VISUALIZACIÓN DE ALTA CALIDAD
    # ==========================================
    # Colores profundos de la paleta
    c_off = '#1a365d' # Azul Marino
    c_mid = '#4a5568' # Gris Pizarra
    c_on  = '#9b2c2c' # Rojo Carmesí
    c_agg = '#ff7f0e' # Naranja (Área Agregada)

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle('Proceso de Defusificación: Método del Centroide', fontsize=18, fontweight='bold', y=0.95)

    # 1. Dibujar las funciones originales como "sombras" o líneas punteadas de fondo
    ax.plot(x_aper, aper_OFF, linestyle='--', linewidth=1.5, color=c_off, alpha=0.5, label='Conjuntos Originales')
    ax.plot(x_aper, aper_MID, linestyle='--', linewidth=1.5, color=c_mid, alpha=0.5)
    ax.plot(x_aper, aper_ON,  linestyle='--', linewidth=1.5, color=c_on,  alpha=0.5)

    # 2. Rellenar las áreas individuales recortadas
    ax.fill_between(x_aper, 0, aper_OFF_clip, color=c_off, alpha=0.6)
    ax.fill_between(x_aper, 0, aper_MID_clip, color=c_mid, alpha=0.6)
    ax.fill_between(x_aper, 0, aper_ON_clip,  color=c_on,  alpha=0.6)

    # Trazar el borde del área agregada total (la silueta final)
    ax.plot(x_aper, aper_agregada, linewidth=3, color='black', label='Área Agregada (Unión)')

    # 3. Dibujar el Centroide (La acción física resultante)
    ax.vlines(centroide_x, 0, centroide_y, color='black', linewidth=3, linestyle='-')
    
    # Dibujar el "punto" de equilibrio
    ax.plot(centroide_x, centroide_y, 'ko', markersize=10)
    ax.plot(centroide_x, 0, 'ko', markersize=10) # Punto en el eje X

    # Anotaciones explicativas de las reglas
    ax.text(60, 0.45, f'Activación MID: {activacion_MID}', fontsize=11, color=c_mid, fontweight='bold')
    ax.text(80, 0.85, f'Activación ON: {activacion_ON}', fontsize=11, color=c_on, fontweight='bold')
    
    # Etiqueta gigante para el Centroide
    texto_centroide = f'Centroide (Apertura Final) = {centroide_x:.1f} %'
    ax.annotate(texto_centroide,
                xy=(centroide_x, 0), xycoords='data',
                xytext=(centroide_x - 30, 0.2), textcoords='data',
                arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=8),
                fontsize=14, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="black", lw=2))

    # Formateo del gráfico
    ax.set_title('Escenario: T. Interior = 26.5°C | T. Exterior = 15.0°C | Objetivo = 25.0°C', fontsize=14, pad=10)
    ax.set_xlabel('Nivel de Apertura de la Ventana (%)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Grado de Pertenencia ($\mu$)', fontsize=14, fontweight='bold')
    
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1.1)
    
    # Ajustes estéticos de los ejes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.grid(True, linestyle=':', alpha=0.7)

    ax.legend(loc='upper left', fontsize=12)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    graficar_defusificacion_centroide()