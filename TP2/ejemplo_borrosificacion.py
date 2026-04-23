import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt

def graficar_borrosificacion_singleton_corregida():
    """
    Genera una figura horizontal explicando el proceso de borrosificación Singleton,
    corrigiendo el solapamiento de textos e incluyendo diagramas de flujo inferiores.
    """
    
    # --- 1. Definición de Universos ---
    x_err = np.arange(-5, 5.1, 0.1)
    x_dt  = np.arange(-10, 10.1, 0.1)

    # Funciones de pertenencia (Estrategia Base)
    err_neg = fuzz.trapmf(x_err, [-20, -20, -2, 0])
    err_Z   = fuzz.trimf(x_err, [-2, 0, 2])
    err_pos = fuzz.trapmf(x_err, [0, 2, 20, 20])

    dt_neg  = fuzz.trapmf(x_dt, [-20, -20, -1, 1])
    dt_pos  = fuzz.trapmf(x_dt, [-1, 1, 20, 20])

    # --- 2. Caso de Estudio ---
    val_err = 1.0   # Habitación a 26°C -> Error de +1°C
    val_dt  = -5.0  # Habitación a 26°C, Exterior a 21°C -> dT de -5°C

    # Cálculo de los grados de pertenencia
    mu_err_neg = fuzz.interp_membership(x_err, err_neg, val_err)
    mu_err_Z   = fuzz.interp_membership(x_err, err_Z, val_err)
    mu_err_pos = fuzz.interp_membership(x_err, err_pos, val_err)

    mu_dt_neg  = fuzz.interp_membership(x_dt, dt_neg, val_dt)
    mu_dt_pos  = fuzz.interp_membership(x_dt, dt_pos, val_dt)

    # --- 3. Configuración del Gráfico ---
    # Aumentamos la altura de 6 a 8 para dejar espacio al diagrama inferior
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle('Proceso de Borrosificación: Método Singleton', 
                 fontsize=20, fontweight='bold', y=0.96)

    c_neg = '#1f77b4' # Azul
    c_Z   = '#2ca02c' # Verde
    c_pos = '#d62728' # Rojo
    c_sensor = '#333333' # Gris oscuro para la lectura

    # ==========================================
    # PANEL 1: VARIABLE ERROR
    # ==========================================
    ax1.plot(x_err, err_neg, color=c_neg, linewidth=2.5, label='Negativo')
    ax1.plot(x_err, err_Z,   color=c_Z,   linewidth=2.5, label='Cero (Z)')
    ax1.plot(x_err, err_pos, color=c_pos, linewidth=2.5, label='Positivo')

    ax1.axvline(x=val_err, color=c_sensor, linestyle='-', linewidth=3, alpha=0.7, label=f'Lectura Sensor: {val_err}°C')

    # CORRECCIÓN DE SOLAPAMIENTO (Offsets Verticales)
    if mu_err_Z > 0:
        ax1.plot(val_err, mu_err_Z, 'ko', markersize=10)
        ax1.hlines(mu_err_Z, -5, val_err, colors=c_Z, linestyles='--', linewidth=2)
        # Texto desplazado un poco hacia arriba
        ax1.text(-4.8, mu_err_Z + 0.04, f'$\mu(Z) = {mu_err_Z:.2f}$', fontsize=14, fontweight='bold', color=c_Z)

    if mu_err_pos > 0:
        ax1.plot(val_err, mu_err_pos, 'ko', markersize=10)
        # Línea y texto desplazados ligeramente hacia abajo para evitar pisar al verde
        ax1.hlines(mu_err_pos - 0.015, -5, val_err, colors=c_pos, linestyles='--', linewidth=2)
        ax1.text(-4.8, mu_err_pos - 0.08, f'$\mu(Pos) = {mu_err_pos:.2f}$', fontsize=14, fontweight='bold', color=c_pos)

    ax1.set_title(f'Paso 1: Evaluar Error (V - Vobj)', fontsize=16, pad=15)
    ax1.set_xlim(-5, 5)
    ax1.set_ylim(-0.05, 1.1)
    ax1.set_xlabel('Error (°C)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Grado de Pertenencia ($\mu$)', fontsize=14, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.7)
    ax1.legend(loc='upper right', fontsize=12)

    # ==========================================
    # PANEL 2: VARIABLE dT
    # ==========================================
    ax2.plot(x_dt, dt_neg, color=c_neg, linewidth=2.5, label='Negativo')
    ax2.plot(x_dt, dt_pos, color=c_pos, linewidth=2.5, label='Positivo')

    ax2.axvline(x=val_dt, color=c_sensor, linestyle='-', linewidth=3, alpha=0.7, label=f'Lectura Sensor: {val_dt}°C')

    if mu_dt_neg > 0:
        ax2.plot(val_dt, mu_dt_neg, 'ko', markersize=10)
        ax2.hlines(mu_dt_neg, -10, val_dt, colors=c_neg, linestyles='--', linewidth=2)
        ax2.text(-9.5, mu_dt_neg + 0.04, f'$\mu(Neg) = {mu_dt_neg:.2f}$', fontsize=14, fontweight='bold', color=c_neg)

    ax2.set_title(f'Paso 2: Evaluar Diferencial Térmico (Ve - V)', fontsize=16, pad=15)
    ax2.set_xlim(-10, 10)
    ax2.set_ylim(-0.05, 1.1)
    ax2.set_xlabel('Diferencial dT (°C)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Grado de Pertenencia ($\mu$)', fontsize=14, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.7)
    ax2.legend(loc='center right', fontsize=12)

    # ==========================================
    # AGREGADO: DIAGRAMAS DE FLUJO INFERIORES
    # ==========================================
    def dibujar_diagrama_bloques(ax, val_in, texto_salida):
        # Coordenada Y relativa por debajo del eje X
        y_pos = -0.28 
        
        # 1. Caja de Entrada (Sensor)
        ax.text(0.15, y_pos, f"Sensor Real:\n{val_in}", transform=ax.transAxes,
                va='center', ha='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle="square,pad=0.6", facecolor="#e2e8f0", edgecolor="black", lw=1.5))
                
        # 2. Flecha hacia Proceso
        ax.annotate("", xy=(0.38, y_pos), xytext=(0.25, y_pos), xycoords='axes fraction',
                    arrowprops=dict(facecolor='black', shrink=0.0, width=2, headwidth=8))
                    
        # 3. Caja de Proceso (Borrosificador)
        ax.text(0.5, y_pos, "Borrosificación\n(Singleton)", transform=ax.transAxes,
                va='center', ha='center', fontsize=12, fontweight='bold', color="#856404",
                bbox=dict(boxstyle="round,pad=0.8", facecolor="#fff3cd", edgecolor="#856404", lw=2))
                
        # 4. Flecha hacia Salida
        ax.annotate("", xy=(0.75, y_pos), xytext=(0.62, y_pos), xycoords='axes fraction',
                    arrowprops=dict(facecolor='black', shrink=0.0, width=2, headwidth=8))
                    
        # 5. Caja de Salida (Grados de Verdad)
        ax.text(0.85, y_pos, f"Salidas Difusas (μ):\n{texto_salida}", transform=ax.transAxes,
                va='center', ha='center', fontsize=12, fontweight='bold', color="#0f5132",
                bbox=dict(boxstyle="square,pad=0.6", facecolor="#d1e7dd", edgecolor="#0f5132", lw=1.5))

    # Formateo de los textos de salida de los diagramas
    out1_text = ""
    if mu_err_Z > 0: out1_text += f"μ(Z) = {mu_err_Z:.2f}\n"
    if mu_err_pos > 0: out1_text += f"μ(Pos) = {mu_err_pos:.2f}"
    
    out2_text = ""
    if mu_dt_neg > 0: out2_text += f"μ(Neg) = {mu_dt_neg:.2f}"

    # Inyección de los diagramas
    dibujar_diagrama_bloques(ax1, f"{val_err} °C", out1_text.strip())
    dibujar_diagrama_bloques(ax2, f"{val_dt} °C", out2_text.strip())

    # Ajuste drástico de los márgenes inferiores para hacer lugar a los diagramas
    plt.subplots_adjust(bottom=0.25, wspace=0.15)
    plt.show()

if __name__ == "__main__":
    graficar_borrosificacion_singleton_corregida()