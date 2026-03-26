# --- visualizacion/analizador.py ---

import matplotlib.pyplot as plt
import numpy as np
from typing import List

class AnalizadorMetricas:
    """
    Clase dedicada a generar visualizaciones estadísticas y reportes gráficos
    del rendimiento de los algoritmos de IA.
    """
    
    def __init__(self):
        # Establecer un estilo estético predefinido (limpio y profesional)
        plt.style.use('seaborn-v0_8-whitegrid')
        
    def graficar_convergencia_genetica(self, historial_costos: List[float]) -> None:
        """
        Genera un gráfico grande y detallado mostrando la caída del costo 
        operativo a través de las generaciones del Algoritmo Genético.
        """
        if not historial_costos:
            print("[ADVERTENCIA] No hay historial de costos para graficar.")
            return

        # 1. Crear lienzo grande (proporción ideal para diapositivas 16:9)
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # 2. Renderizado de la curva de costo en AZUL INTENSO
        generaciones = range(len(historial_costos))
        ax.plot(generaciones, historial_costos, 
                color='#1f77b4', # Azul profesional
                linewidth=2.5, 
                label='Mejor Costo Encontrado ($\sum T \circ D$)')
        
        # 3. Estilización de Títulos y Ejes (Grandes y Representativos)
        ax.set_title('EVOLUCIÓN DE LA OPTIMIZACIÓN DEL LAYOUT\nConvergencia del Algoritmo Genético', 
                     fontsize=20, fontweight='bold', pad=20)
        ax.set_xlabel('Generación Consecutiva', fontsize=16, fontweight='bold')
        ax.set_ylabel('Costo Operativo Total (Pasos/Distancia)', fontsize=16, fontweight='bold')
        
        # Aumentar tamaño de los números en los ejes (ticks)
        ax.tick_params(axis='both', which='major', labelsize=12)
        
        # 4. Detalles Visuales de Apoyo
        ax.grid(True, linestyle='--', alpha=0.6) # Rejilla sutil
        ax.legend(loc='upper right', fontsize=13, frameon=True, shadow=True)
        
        # Resaltar punto inicial y final con marcadores
        ax.scatter(0, historial_costos[0], color='#d62728', s=80, zorder=5) # Punto rojo inicial
        ax.scatter(generaciones[-1], historial_costos[-1], color='#2ca02c', s=80, zorder=5) # Punto verde final
        
        # Anotación del costo final
        ax.annotate(f'Costo Final: {int(historial_costos[-1])}', 
                    xy=(generaciones[-1], historial_costos[-1]), 
                    xytext=(-160, 20), 
                    textcoords='offset points', 
                    fontsize=12, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", fc="#e1f5fe", ec="#0277bd", lw=1.5))

        plt.tight_layout()
        
        print("\n>>> Mostrando gráfico de convergencia genético. Cierre la ventana para continuar.")
        plt.show() # Bloquea la ejecución hasta que el usuario cierra la ventana.