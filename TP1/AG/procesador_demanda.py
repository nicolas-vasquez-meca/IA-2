import numpy as np
from typing import List

import matplotlib.pyplot as plt #< Solo para testing


class ProcesadorDemanda:
    """
    Transforma secuencias lineales de recoleccion en una 
    Matriz de Transición bidimensional de Markov.
    """

    @staticmethod
    def generar_matriz_transicion(secuencias: List[List[int]]) -> np.ndarray:
        """
        Construye una matriz cuadrada donde el valor en la posicion (Fila A, Col B)
        indica cuantas veces el agente viajo desde A hacia B
        """
        # Numero de estante mas grande en todo el historial
        estante_maximo = 0
        for secuencia in secuencias:
            if secuencia:
                maximo_local = max(secuencia)
                if maximo_local > estante_maximo:
                    estante_maximo = maximo_local
        
        # Para agregar la estacion de carga
        dimension = estante_maximo + 1
        
        matriz_frecuencias = np.zeros( (dimension, dimension), dtype=int )

        # Listas para almacenar coordenadas de inicio y fin de cada paso
        coordenadas_origen = []
        coordenadas_destino = []

        # Inyeccion de base y fragmentacion
        for secuencia in secuencias:
            if not secuencia:
                continue
            
            # Agente sale de la base, recoge productos y vuelve a base
            ruta_completa = [0] + secuencia + [0]

            # Fragmentacion de ruta en trayectos individuales
            for indice in range(len(ruta_completa) - 1):
                coordenadas_origen.append(ruta_completa[indice])
                coordenadas_destino.append(ruta_completa[indice + 1])

        # Acumulación matricial
        # np.add.at es una herramienta de numpy.
        # Toma la matriz vacia y por cada par de coordenadas (origen, destino) recopilado,
        # le suma 1 a esa posición especifica
        np.add.at(matriz_frecuencias, (coordenadas_origen, coordenadas_destino), 1)

        return matriz_frecuencias


if __name__ == "__main__":
    print("--- Iniciando validación visual de la matriz de transición ---")
    
    # 1. Preparación de datos: 
    # Para lograr una matriz 5x5, el estante más alto debe ser 4.
    # Ruta interpretada: 0 -> 2 -> 3 -> 4 -> 0 (Ejecutada dos veces)
    datos_simulados = [
        [2, 3, 4],
        [2, 3, 4]
    ]
    
    # 2. Generación matemática
    matriz_resultado = ProcesadorDemanda.generar_matriz_transicion(datos_simulados)
    
    # 3. Impresión estructural en consola
    print("\n[*] Propiedades de la Matriz Generada:")
    print(f"    - Tamaño de la cuadrícula: {matriz_resultado.shape} (Nodos 0 a 4)")
    print("    - Despliegue en texto crudo:")
    print(matriz_resultado)
    
    # 4. Generación del gráfico (Mapa de Calor)
    print("\n[*] Renderizando gráfico de validación. Cierre la ventana gráfica para finalizar el programa.")
    
    # Se crea un lienzo de dibujo (figura) y un eje espacial
    figura, eje = plt.subplots(figsize=(6, 6))
    
    # Se mapean los números de la matriz a un gradiente de color azul ('Blues')
    mapa_calor = eje.matshow(matriz_resultado, cmap='Blues')
    
    # Se añade una barra lateral de referencia para la escala de colores
    figura.colorbar(mapa_calor, label='Frecuencia de Tránsito')
    
    # Se iteran las coordenadas para sobreescribir el número exacto dentro de cada bloque de color
    dimensiones = matriz_resultado.shape[0]
    for fila in range(dimensiones):
        for columna in range(dimensiones):
            valor = matriz_resultado[fila, columna]
            eje.text(columna, fila, str(valor), 
                     va='center', ha='center', 
                     color='white' if valor > 0 else 'black')
            
    # Configuración de etiquetas para comprensión del observador
    plt.title("Matriz Topológica de Demanda Espacial", pad=20)
    plt.xlabel("Nodo de Destino (Columna)")
    plt.ylabel("Nodo de Origen (Fila)")
    
    # Se ajustan las marcas de los ejes para que coincidan con los números de estantes
    eje.set_xticks(range(dimensiones))
    eje.set_yticks(range(dimensiones))
    
    # Despliegue de la ventana gráfica en el sistema operativo
    plt.show()

    print("--- Validación y visualización finalizadas exitosamente. ---")