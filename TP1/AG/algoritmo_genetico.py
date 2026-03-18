import random
import numpy as np
from typing import Dict, List, Tuple

class AlgoritmoGenetico:
    """
    Motor de Optimización espacial.
    Minimiza el costo de transito evaluando la topologia de demanda y distancia.
    """

    def __init__(
            self,
            matriz_transicion: np.ndarray,
            matriz_distancias: np.ndarray,
            estantes_ids: List[int],
            coordenadas_ids: List[int],
            tamano_poblacion: int = 100,
            tasa_mutacion: float = 0.05,
            tasa_cruce: float = 0.8,
            limite_iteraciones: int = 500,
            tolerancia_convergencia: int = 50
    ):
        # Datos matriciales
        self.matriz_transicion = matriz_transicion
        self.matriz_distancias = matriz_distancias
        self.estantes_ids = estantes_ids
        self.coordenadas_ids = coordenadas_ids

        # Hiperparametros de Control
        self.tamano_poblacion = tamano_poblacion
        self.tasa_mutacion = tasa_mutacion
        self.tasa_cruce = tasa_cruce
        self.limite_iteraciones = limite_iteraciones
        self.tolerancia_convergencia = tolerancia_convergencia

        # Dinamica de Torneo
        self.tamano_torneo = max(2, int(self.tamano_poblacion * 0.05))

        # Estado Interno
        self.poblacion: List[List[int]] = []
        self.mejor_solucion_historica: List[int] = []
        self.mejor_aptitud_historica: float = -float('inf')

    def _inicializar_poblacion(self) -> None:
        """
        Genera cromosomas iniciales mediante permutaciones aleatorias validas
        """
        self.poblacion = [
            random.sample(self.estantes_ids, len(self.estantes_ids))
            for _ in range (self.tamano_poblacion)
        ]

    def _calcular_aptitud(self, cromosoma: List[int]) -> float:
        """
        Evalua el costo de la distribucion espacial.
        """
        costo_total = 0.0
        dimension_estantes = len(self.estantes_ids)

        # Iteracion sobre los pares de transicion para calcular costo acumulad
        for estante_origen in self.estantes_ids:
            for estante_destino in self.estantes_ids:
                frecuencia = self.matriz_transicion[estante_origen][estante_destino]
                if frecuencia > 0:
                    # Se localiza la coordenada fisica asignada a cada estante en el cromosoma
                    idx_coord_origen = cromosoma.index(estante_origen)
                    idx_coord_destino = cromosoma.index(estante_destino)

                    coord_origen = self.coordenadas_ids[idx_coord_origen]
                    coord_destino = self.coordenadas_ids[idx_coord_destino]

                    distancia = self.matriz_distancias[coord_origen][coord_destino]
                    costo_total += (frecuencia * distancia)

        # Inversion matematica: Menor costo resulta en mayor amplitud
        return 1.0 / (costo_total + 1e-6)

    def seleccion(self, aptitudes: List[float]) -> List[List[int]]:
        """
        Aplica Seleccion Hibrida: Elitismo absoluto + Torneo Estocastico
        """
        nueva_poblacion = []

        # Elitismo. Extraemos el indice del mejor individuo para conservarlo
        mejor_indice = aptitudes.index(max(aptitudes))
        nueva_poblacion.append(self.poblacion[mejor_indice][:])

        # Torneo. Seleccionar el resto de la poblacion
        while len(nueva_poblacion) < self.tamano_poblacion:
            participantes = random.sample(range(self.tamano_poblacion), self.tamano_torneo)
            ganador_torneo = max(participantes, key=lambda idx: aptitudes[idx])
            nueva_poblacion.append(self.poblacion[ganador_torneo][:])

        return nueva_poblacion
    
    def evolucion(self, poblacion_seleccionada: List[List[int]]) -> List[List[int]]:
        """
        Itera sobre la poblacion seleccionada aplicando cruzamiento PMX en pares
        """
        descendencia = []

        for i in range(0, self.tamano_poblacion, 2):
            padre1 = poblacion_seleccionada[i]
            
            # Manejo de poblaciones impares
            if i + 1 < self.tamano_poblacion:
                padre2 = poblacion_seleccionada[i+1]
            else:
                descendencia.append(padre1[:])
                break
                
            if random.random() < self.tasa_cruce:
                hijo1 = self._cruce_pmx(padre1, padre2)
                hijo2 = self._cruce_pmx(padre2, padre1)
                descendencia.extend([hijo1, hijo2])
            else:
                descendencia.extend([padre1[:], padre2[:]])
                
        # Asegurar dimensionamiento poblacional por elitismo
        return descendencia[:self.tamano_poblacion]
    
    def _cruce_pmx(self, p1: List[int], p2: List[int]) -> List[int]:
        """
        Algoritmo PMX (Partially Mapped Crossover). 
        Garantiza herencia de coordenadas sin romper la biyectividad.
        """
        tamano = len(p1)
        hijo = p2[:]
        idx1, idx2 = sorted(random.sample(range(tamano), 2))
        
        # 1. Herencia estricta del subsegmento del primer progenitor
        segmento_p1 = p1[idx1:idx2+1]
        hijo[idx1:idx2+1] = segmento_p1
        
        # 2. Resolución de conflictos mediante mapeo cíclico
        for i in range(idx1, idx2+1):
            elemento_p2 = p2[i]
            if elemento_p2 not in segmento_p1:
                posicion_actual = i
                # Búsqueda de la coordenada original válida
                while idx1 <= posicion_actual <= idx2:
                    elemento_conflicto = p1[posicion_actual]
                    posicion_actual = p2.index(elemento_conflicto)
                hijo[posicion_actual] = elemento_p2
                
        return hijo
    
    def mutacion(self, descendencia: List[List[int]]) -> List[List[int]]:
        """
        Aplica Mutacion de Intercambio (Swap) para evitar duplicados
        """
        for cromosoma in descendencia:
            if random.random() < self.tasa_mutacion:
                idx1, idx2 = random.sample(range(len(cromosoma)), 2)
                # Intercambio de estantes en la matriz espacial
                cromosoma[idx1], cromosoma[idx2] = cromosoma[idx2], cromosoma[idx1]
        return descendencia
    
    def ejecutar(self) -> None:
        """
        Bucle principal del algoritmo. Evalúa la condición de parada por
        convergencia asintótica o por límite de seguridad.
        """
        self._inicializar_poblacion()
        generaciones_sin_mejora = 0
        iteracion_actual = 0

        while iteracion_actual < self.limite_iteraciones and generaciones_sin_mejora < self.tolerancia_convergencia:
            aptitudes = [self._calcular_aptitud(ind) for ind in self.poblacion]
            
            # Registro de la mejor solución de la iteración
            max_aptitud_actual = max(aptitudes)
            if max_aptitud_actual > self.mejor_aptitud_historica:
                self.mejor_aptitud_historica = max_aptitud_actual
                self.mejor_solucion_historica = self.poblacion[aptitudes.index(max_aptitud_actual)][:]
                generaciones_sin_mejora = 0
            else:
                generaciones_sin_mejora += 1

            # Proceso evolutivo
            poblacion_seleccionada = self.seleccion(aptitudes)
            descendencia = self.evolucion(poblacion_seleccionada)
            self.poblacion = self.mutacion(descendencia)
            
            iteracion_actual += 1

    def evaluacion(self) -> Tuple[List[int], float, str]:
        """
        Retorna el modelo entrenado y sus métricas de rendimiento.
        """
        estado_convergencia = "Estable" if self.mejor_aptitud_historica > 0 else "Divergente"
        return self.mejor_solucion_historica, self.mejor_aptitud_historica, estado_convergencia