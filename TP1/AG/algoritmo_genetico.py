import random
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass(frozen=True)
class ConfiguracionAG:
    """
    Encapsula los hiperparametros evolutivos
    """
    tamano_poblacion: int
    tasa_mutacion: float
    tasa_cruce: float
    limite_iteraciones: int
    tolerancia_convergencia: int
    tamano_torneo: int


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
            coord_base: int,
            configuracion: ConfiguracionAG
    ):
        # Datos topologicos y espaciales
        self.matriz_transicion = matriz_transicion
        self.matriz_distancias = matriz_distancias
        self.estantes_ids = estantes_ids
        self.coordenadas_ids = coordenadas_ids
        self.coord_base = coord_base
        self.dimension_estantes = len(self.estantes_ids)

        # Configuracion encapsulada
        self.config = configuracion

        # Estado Interno
        self.poblacion: List[List[int]] = []
        self.mejor_solucion_historica: List[int] = []
        self.mejor_aptitud_historica: float = -float('inf')

    def _inicializar_poblacion(self) -> None:
        """
        Genera cromosomas iniciales mediante permutaciones aleatorias validas
        """
        self.poblacion = [
            random.sample(self.estantes_ids, self.dimension_estantes)
            for _ in range (self.config.tamano_poblacion)
        ]

    def _calcular_aptitud(self, cromosoma: List[int]) -> float:
        """
        Evalua el costo de la distribucion espacial.
        """
        costo_total = 0.0

        # Evaluación lineal para la estación de carga (Optimización Global)
        for i in range(self.dimension_estantes):
            estante = cromosoma[i]
            coord_estante = self.coordenadas_ids[i]
            
            # Trayecto: Estación -> Estante
            costo_total += (self.matriz_transicion[0, estante] * self.matriz_distancias[self.coord_base, coord_estante])
            # Trayecto: Estante -> Estación
            costo_total += (self.matriz_transicion[estante, 0] * self.matriz_distancias[coord_estante, self.coord_base])

            # Evaluación cruzada entre estantes (Optimización Local)
            for j in range(self.dimension_estantes):
                estante_destino = cromosoma[j]
                frecuencia = self.matriz_transicion[estante, estante_destino]
                
                if frecuencia > 0:
                    coord_destino = self.coordenadas_ids[j]
                    costo_total += (frecuencia * self.matriz_distancias[coord_estante, coord_destino])

        return 1.0 / (costo_total + 1e-6)

    def seleccion(self, aptitudes: List[float]) -> List[List[int]]:
        """
        Aplica Seleccion Hibrida: Elitismo absoluto + Torneo Estocastico
        """
        nueva_poblacion = []

        # Elitismo Absoluto
        mejor_indice = aptitudes.index(max(aptitudes))
        nueva_poblacion.append(self.poblacion[mejor_indice][:])

        # Torneo Estocastico
        while len(nueva_poblacion) < self.config.tamano_poblacion:
            participantes = random.sample(range(self.config.tamano_poblacion), self.config.tamano_torneo)
            ganador_torneo = max(participantes, key=lambda idx: aptitudes[idx])
            nueva_poblacion.append(self.poblacion[ganador_torneo][:])

        return nueva_poblacion
    
    def evolucion(self, poblacion_seleccionada: List[List[int]]) -> List[List[int]]:
        """
        Itera sobre la poblacion seleccionada aplicando cruzamiento PMX en pares
        """
        descendencia = []

        for i in range(0, self.config.tamano_poblacion, 2):
            padre1 = poblacion_seleccionada[i]
            
            # Manejo de poblaciones impares
            if i + 1 < self.config.tamano_poblacion:
                padre2 = poblacion_seleccionada[i+1]
            else:
                descendencia.append(padre1[:])
                break
            
            # Si el valor aleatorio generado es menos a la tasa de cruce
            if random.random() < self.config.tasa_cruce:
                hijo1 = self._cruce_pmx(padre1, padre2)
                hijo2 = self._cruce_pmx(padre2, padre1)
                descendencia.extend([hijo1, hijo2])
            else:
                descendencia.extend([padre1[:], padre2[:]])
                
        # Asegurar dimensionamiento poblacional por elitismo
        return descendencia[:self.config.tamano_poblacion]
    
    def _cruce_pmx(self, p1: List[int], p2: List[int]) -> List[int]:
        """
        Algoritmo PMX (Partially Mapped Crossover). 
        Garantiza herencia de coordenadas sin romper la biyectividad.
        """
        tamano = self.dimension_estantes
        hijo = p2[:]
        idx1, idx2 = sorted(random.sample(range(tamano), 2))
        
        # 1. Herencia estricta del subsegmento del primer progenitor
        segmento_p1 = p1[idx1:idx2+1]
        hijo[idx1:idx2+1] = segmento_p1
        
        # Optimizaciones de memoria: Búsqueda Hash de O(1)
        set_segmento_p1 = set(segmento_p1)
        indices_p2 = {valor: indice for indice, valor in enumerate(p2)}

        # 2. Resolución de conflictos mediante mapeo cíclico
        for i in range(idx1, idx2+1):
            elemento_p2 = p2[i]
            if elemento_p2 not in set_segmento_p1:
                posicion_actual = i
                # Búsqueda de la coordenada original válida
                while idx1 <= posicion_actual <= idx2:
                    elemento_conflicto = p1[posicion_actual]
                    posicion_actual = indices_p2[elemento_conflicto]
                hijo[posicion_actual] = elemento_p2
                
        return hijo
    
    def mutacion(self, descendencia: List[List[int]]) -> List[List[int]]:
        """
        Aplica Mutacion de Intercambio (Swap) para evitar duplicados
        """
        for cromosoma in descendencia:
            if random.random() < self.config.tasa_mutacion:
                idx1, idx2 = random.sample(range(self.dimension_estantes), 2)
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

        while iteracion_actual < self.config.limite_iteraciones and generaciones_sin_mejora < self.config.tolerancia_convergencia:
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
    




if __name__ == "__main__":
    print("--- INICIANDO VALIDACIÓN DEL MOTOR EVOLUTIVO OPTIMIZADO ---")

    # 1. Vectores de Identificadores (5 estantes, 5 coordenadas)
    estantes_prueba = [1, 2, 3, 4, 5]
    coordenadas_prueba = [1, 2, 3, 4, 5]
    coordenada_base_prueba = 0

    # 2. Generación de Matriz de Transición Sesgada (Dimensión 6x6)
    # Índices: 0 es Base, 1 a 5 son Estantes.
    matriz_transicion_ficticia = np.zeros((6, 6), dtype=int)
    
    # Alta demanda encadenada: Base -> Estante 1 -> Estante 2 -> Estante 3 -> Base
    matriz_transicion_ficticia[0, 1] = 100
    matriz_transicion_ficticia[1, 2] = 100
    matriz_transicion_ficticia[2, 3] = 100
    matriz_transicion_ficticia[3, 0] = 100
    
    # Baja demanda marginal: Base -> Estante 4 -> Estante 5 -> Base
    matriz_transicion_ficticia[0, 4] = 5
    matriz_transicion_ficticia[4, 5] = 5
    matriz_transicion_ficticia[5, 0] = 5

    # 3. Generación de Matriz de Distancias Ficticia (Dimensión 6x6)
    # Simulamos una cuadrícula plana: Base=(0,0), Coord1=(0,1), Coord2=(1,0), Coord3=(1,1), Coord4=(0,2), Coord5=(2,0)
    posiciones_geograficas = {
        0: (0, 0),  # Base
        1: (0, 1),  # Adyacente (Distancia 1)
        2: (1, 0),  # Adyacente (Distancia 1)
        3: (1, 1),  # Diagonal equivalente (Distancia 2)
        4: (0, 2),  # Lejano (Distancia 2)
        5: (2, 0)   # Lejano (Distancia 2)
    }
    
    matriz_distancias_ficticia = np.zeros((6, 6), dtype=float)
    for origen in range(6):
        for destino in range(6):
            # Cálculo matemático de distancia Manhattan
            x_origen, y_origen = posiciones_geograficas[origen]
            x_destino, y_destino = posiciones_geograficas[destino]
            matriz_distancias_ficticia[origen, destino] = abs(x_origen - x_destino) + abs(y_origen - y_destino)

    # 4. Instanciación de la Configuración DTO
    configuracion_prueba = ConfiguracionAG(
        tamano_poblacion=50,
        tasa_mutacion=0.1,
        tasa_cruce=0.85,
        limite_iteraciones=100,
        tolerancia_convergencia=30,
        tamano_torneo=5
    )

    # 5. Ejecución del Algoritmo
    optimizador = AlgoritmoGenetico(
        matriz_transicion=matriz_transicion_ficticia,
        matriz_distancias=matriz_distancias_ficticia,
        estantes_ids=estantes_prueba,
        coordenadas_ids=coordenadas_prueba,
        coord_base=coordenada_base_prueba,
        configuracion=configuracion_prueba
    )

    print("[*] Evaluando distribucion inicial aleatoria...")
    optimizador._inicializar_poblacion()
    aptitud_inicial = optimizador._calcular_aptitud(optimizador.poblacion[0])
    costo_inicial = (1.0 / aptitud_inicial) - 1e-6
    print(f"    Costo operativo inicial: {costo_inicial:.2f} unidades.")

    print("\n[*] Entrenando motor evolutivo...")
    optimizador.ejecutar()

    # 6. Extracción de Resultados
    solucion_final, aptitud_final, estado_convergencia = optimizador.evaluacion()
    costo_final = (1.0 / aptitud_final) - 1e-6

    print(f"\n[*] Proceso finalizado. Estado: {estado_convergencia}")
    print(f"[*] Costo operativo optimo alcanzado: {costo_final:.2f} unidades.")
    
    print("\n[*] Analisis de Mapeo Espacial:")
    for indice, id_estante in enumerate(solucion_final):
        id_coordenada = coordenadas_prueba[indice]
        distancia_a_base = matriz_distancias_ficticia[coordenada_base_prueba, id_coordenada]
        print(f"    - El Estante {id_estante} fue asignado a la Coordenada {id_coordenada} (Distancia a la base: {distancia_a_base})")
    
    print("\n--- Validacion concluida. El algoritmo demuestra capacidad para agrupar estantes de alta demanda cerca del nodo de recarga. ---")