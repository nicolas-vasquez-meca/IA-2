import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

def graficar_matriz_fam_proyector():
    """
    Genera una figura de la Matriz FAM optimizada para presentaciones 
    en proyector y reportes técnicos de alta calidad.
    """
    # Etiquetas
    err_labels = ['Negativo', 'Cero (Z)', 'Positivo']
    dt_labels = ['Negativo', 'Positivo']
    
    # Matriz de texto para visualización
    fam_text = np.array([
        ['OFF', 'ON'],
        ['MID', 'MID'],
        ['ON', 'OFF']
    ])
    
    # Matriz numérica para asignar colores (0: OFF, 1: MID, 2: ON)
    fam_num = np.array([
        [0, 2],
        [1, 1],
        [2, 0]
    ])

    # --- DISEÑO PROFESIONAL DE COLORES ---
    # Colores profundos: Azul Marino (OFF), Gris Pizarra (MID), Rojo Carmesí (ON)
    hex_colors = ['#1a365d', '#4a5568', '#9b2c2c']
    cmap_custom = ListedColormap(hex_colors)

    # Figura más grande y apaisada
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Trazar el mapa con bordes negros gruesos separando las celdas
    cax = ax.matshow(fam_num, cmap=cmap_custom)
    
    # Configuración de Ejes (Tamaños de fuente grandes para proyector)
    ax.set_xticks(np.arange(len(dt_labels)))
    ax.set_yticks(np.arange(len(err_labels)))
    ax.set_xticklabels(dt_labels, fontsize=16)
    ax.set_yticklabels(err_labels, fontsize=16)
    
    # Títulos de los ejes
    ax.set_xlabel('Diferencial de Temperatura (dT)', fontsize=18, fontweight='bold', labelpad=15)
    ax.set_ylabel('Error de Temperatura (V - Vobj)', fontsize=18, fontweight='bold', labelpad=15)
    ax.xaxis.set_label_position('top') 
    
    # Dibujar la grilla blanca para separar bien las celdas
    ax.set_xticks(np.arange(-.5, len(dt_labels), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(err_labels), 1), minor=True)
    ax.grid(which='minor', color='white', linestyle='-', linewidth=4)
    ax.tick_params(which='minor', bottom=False, left=False)

    # Inyectar el texto dentro de cada celda
    for i in range(len(err_labels)):
        for j in range(len(dt_labels)):
            ax.text(j, i, fam_text[i, j], ha='center', va='center', 
                    fontsize=24, fontweight='bold', color='white')
            
    # Título Principal
    plt.title("Reglas de Control Difuso: Matriz FAM", y=1.25, fontsize=22, fontweight='bold')
    
    # Ajuste para evitar recortes
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    graficar_matriz_fam_proyector()