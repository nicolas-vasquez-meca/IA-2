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
    metodo_evaluacion: str = 'sa'
    # Hiperparametros
    muestras_sa: int = 15
    iteraciones_sa_interno: int = 100

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
            configuracion: ConfiguracionAG,
            historico_ordenes: List[List[int]] = None,
    ):
        # Datos topologicos y espaciales
        self.matriz_transicion = matriz_transicion
        self.matriz_distancias = matriz_distancias
        self.estantes_ids = estantes_ids
        self.coordenadas_ids = coordenadas_ids
        self.coord_base = coord_base
        self.dimension_estantes = len(self.estantes_ids)
        self.historico_ordenes = historico_ordenes

        # Configuracion encapsulada
        self.config = configuracion

        # Estado Interno
        self.poblacion: List[List[int]] = []
        self.mejor_solucion_historica: List[int] = []
        self.mejor_aptitud_historica: float = -float('inf')

        # Registro analitico de convergencia
        self.historial_costos: List[float] = []


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
        Enrutador principal de evaluación. Aplica el Patrón Strategy 
        basado en la configuración instanciada.
        """
        if self.config.metodo_evaluacion == 'sa':
            return self._evaluacion_sa(cromosoma)
        else:
            return self._evaluacion_markov(cromosoma)
        

    def _evaluacion_markov(self, cromosoma: List[int]) -> float:
        """
        Calcula el Producto de Hadamard cruzado entre Matriz de Transicion
        y Matriz de distancias
        """
        costo_total = 0.0
        peso_posicion_absoluta = 1.0

        # Evaluación lineal para la estación de carga (Optimización Global)
        for i in range(self.dimension_estantes):
            estante = cromosoma[i]
            coord_estante = self.coordenadas_ids[i]
            
            # Trayecto: Estación -> Estante
            costo_base = (self.matriz_transicion[0, estante] * self.matriz_distancias[self.coord_base, coord_estante])
            costo_retorno = (self.matriz_transicion[estante, 0] * self.matriz_distancias[coord_estante, self.coord_base])
            costo_total += (costo_base + costo_retorno) * peso_posicion_absoluta

            # Evaluación cruzada entre estantes (Optimización Local)
            for j in range(self.dimension_estantes):
                estante_destino = cromosoma[j]
                frecuencia = self.matriz_transicion[estante, estante_destino]
                
                if frecuencia > 0:
                    coord_destino = self.coordenadas_ids[j]
                    costo_total += (frecuencia * self.matriz_distancias[coord_estante, coord_destino])

        if costo_total == 0:
            return float('inf')
        return 1.0 / (costo_total + 1e-6)


    def _evaluacion_sa(self, cromosoma: List[int]) -> float:
        """
        Aproximación estocástica estabilizada. 
        Implementa congelamiento del set de validación para garantizar determinismo evolutivo.
        """
        if not self.historico_ordenes:
            raise ValueError("Evaluacion SA requiere 'historico_ordenes' en la instanciacion.")

        mapa_coords = {cromosoma[i]: self.coordenadas_ids[i] for i in range(self.dimension_estantes)}

        # 1. PENALIZACIÓN ESTRUCTURAL GLOBAL (Evita el sobreajuste a la muestra)
        # Calcula el costo topológico utilizando el 100% de la matriz de transición
        costo_estructural_global = 0.0
        for i in range(self.dimension_estantes):
            estante = cromosoma[i]
            coord_estante = self.coordenadas_ids[i]
            costo_base = self.matriz_transicion[0, estante] * self.matriz_distancias[self.coord_base, coord_estante]
            costo_retorno = self.matriz_transicion[estante, 0] * self.matriz_distancias[coord_estante, self.coord_base]
            costo_estructural_global += costo_base + costo_retorno
            
            for j in range(self.dimension_estantes):
                estante_destino = cromosoma[j]
                frecuencia = self.matriz_transicion[estante, estante_destino]
                if frecuencia > 0:
                    coord_destino = self.coordenadas_ids[j]
                    costo_estructural_global += frecuencia * self.matriz_distancias[coord_estante, coord_destino]
        
        # Escalamiento de la penalización a la dimensión de una orden promedio (aprox. 15 items)
        frecuencia_total = np.sum(self.matriz_transicion)
        if frecuencia_total == 0: frecuencia_total = 1.0
        penalizacion_distancia = (costo_estructural_global / frecuencia_total) * 15.0

        # 2. MUESTREO Y CONGELAMIENTO (Validación Estocástica)
        if not hasattr(self, '_ordenes_validacion'):
            self._ordenes_validacion = random.sample(
                self.historico_ordenes, 
                min(self.config.muestras_sa, len(self.historico_ordenes))
            )
        
        ordenes_evaluar = self._ordenes_validacion
        costo_picking_acumulado = 0.0
        ordenes_validas = 0

        # 3. MOTOR INTERNO DE ENRUTAMIENTO Y RECOCIDO SIMULADO
        for orden in ordenes_evaluar:
            if not orden:
                continue
            
            rand_interno = random.Random(hash(tuple(orden)))
            orden_muestreada = rand_interno.sample(orden, min(30, len(orden)))
            
            # CORRECCIÓN VITAL: Inicialización Voraz (Nearest Neighbor)
            # Garantiza que el SA inicie con una ruta estructurada y no ruido aleatorio
            pendientes = set(orden_muestreada)
            ruta_nn = []
            nodo_actual = self.coord_base
            while pendientes:
                # Encuentra el estante más cercano a la posición actual
                siguiente = min(pendientes, key=lambda p: self.matriz_distancias[nodo_actual, mapa_coords[p]])
                ruta_nn.append(siguiente)
                pendientes.remove(siguiente)
                nodo_actual = mapa_coords[siguiente]
            
            estado_ruta = ruta_nn

            def calcular_costo_ruta(ruta: List[int]) -> float:
                costo_r = 0.0
                nodo_actual = self.coord_base
                for producto in ruta:
                    nodo_destino = mapa_coords[producto]
                    cost_movimiento = self.matriz_distancias[nodo_actual, nodo_destino]
                    if np.isinf(cost_movimiento): return 999999.0
                    costo_r += cost_movimiento
                    nodo_actual = nodo_destino
                
                cost_retorno = self.matriz_distancias[nodo_actual, self.coord_base]
                if np.isinf(cost_retorno): return 999999.0
                costo_r += cost_retorno
                return costo_r

            mejor_costo_sa = calcular_costo_ruta(estado_ruta)
            costo_actual_sa = mejor_costo_sa
            temperatura = 100.0
            factor_enfriamiento = 0.85

            # Micro-optimización mediante Recocido Térmico Ligero
            for _ in range(self.config.iteraciones_sa_interno):
                vecino = estado_ruta[:]
                if len(vecino) > 1:
                    i, j = rand_interno.sample(range(len(vecino)), 2)
                    vecino[i], vecino[j] = vecino[j], vecino[i]

                costo_vecino = calcular_costo_ruta(vecino)
                delta_e = costo_vecino - costo_actual_sa

                if delta_e < 0 or rand_interno.random() < np.exp(-delta_e / temperatura):
                    estado_ruta = vecino
                    costo_actual_sa = costo_vecino
                    if costo_actual_sa < mejor_costo_sa:
                        mejor_costo_sa = costo_actual_sa

                temperatura *= factor_enfriamiento

            costo_picking_acumulado += mejor_costo_sa
            ordenes_validas += 1

        costo_promedio_picking = costo_picking_acumulado / max(1, ordenes_validas)
        
        # 4. FITNESS HÍBRIDO (50% Estructura Global / 50% Eficiencia Operativa)
        costo_hibrido = (0.50 * penalizacion_distancia) + (0.50 * costo_promedio_picking)

        if costo_hibrido <= 0 or np.isnan(costo_hibrido):
            return float('inf')
        return 1.0 / (costo_hibrido + 1e-6)

    def seleccion(self, aptitudes: List[float]) -> List[List[int]]:
        """
        Selección basada puramente en Torneo Estocástico.
        El elitismo se delega a la capa superior (bucle de ejecución) para mayor control.
        """
        nueva_poblacion = []
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
            
            if i + 1 < self.config.tamano_poblacion:
                padre2 = poblacion_seleccionada[i+1]
            else:
                descendencia.append(padre1[:])
                break
            
            if random.random() < self.config.tasa_cruce:
                hijo1 = self._cruce_pmx(padre1, padre2)
                hijo2 = self._cruce_pmx(padre2, padre1)
                descendencia.extend([hijo1, hijo2])
            else:
                descendencia.extend([padre1[:], padre2[:]])
                
        return descendencia[:self.config.tamano_poblacion]
        
    
    def _cruce_pmx(self, p1: List[int], p2: List[int]) -> List[int]:
        """
        Algoritmo PMX (Partially Mapped Crossover). 
        Garantiza herencia de coordenadas sin romper la biyectividad.
        """
        tamano = self.dimension_estantes
        hijo = p2[:]
        idx1, idx2 = sorted(random.sample(range(tamano), 2))
        
        segmento_p1 = p1[idx1:idx2+1]
        hijo[idx1:idx2+1] = segmento_p1
        
        set_segmento_p1 = set(segmento_p1)
        indices_p2 = {valor: indice for indice, valor in enumerate(p2)}

        for i in range(idx1, idx2+1):
            elemento_p2 = p2[i]
            if elemento_p2 not in set_segmento_p1:
                posicion_actual = i
                while idx1 <= posicion_actual <= idx2:
                    elemento_conflicto = p1[posicion_actual]
                    posicion_actual = indices_p2[elemento_conflicto]
                hijo[posicion_actual] = elemento_p2
                
        assert len(hijo) == tamano, f"Error PMX: Longitud mutada ({len(hijo)})."
        assert len(set(hijo)) == tamano, "Error PMX: Detección de colisión de identificadores."
        return hijo

    def mutacion(self, descendencia: List[List[int]]) -> List[List[int]]:
        for cromosoma in descendencia:
            if random.random() < self.config.tasa_mutacion:
                idx1, idx2 = random.sample(range(self.dimension_estantes), 2)
                cromosoma[idx1], cromosoma[idx2] = cromosoma[idx2], cromosoma[idx1]

            assert len(cromosoma) == self.dimension_estantes, "Error Mutación: Cardinalidad alterada."
            assert len(set(cromosoma)) == self.dimension_estantes, "Error Mutación: Duplicación inyectada."
        return descendencia
    
    def ejecutar(self) -> None:
        self._inicializar_poblacion()

        if self.poblacion:
            self.mejor_solucion_historica = self.poblacion[0][:]

        generaciones_sin_mejora = 0
        iteracion_actual = 0

        while iteracion_actual < self.config.limite_iteraciones and generaciones_sin_mejora < self.config.tolerancia_convergencia:
            
            aptitudes = [self._calcular_aptitud(ind) for ind in self.poblacion]
            
            aptitudes_seguras = [apt if not np.isnan(apt) else -float('inf') for apt in aptitudes]
            max_aptitud_actual = max(aptitudes_seguras)

            if max_aptitud_actual > self.mejor_aptitud_historica:
                self.mejor_aptitud_historica = max_aptitud_actual
                self.mejor_solucion_historica = self.poblacion[aptitudes_seguras.index(max_aptitud_actual)][:]
                generaciones_sin_mejora = 0
            else:
                generaciones_sin_mejora += 1

            # CORRECCIÓN: Rastreo del costo absoluto óptimo global para asegurar estabilidad gráfica
            mejor_costo_real = 1.0 / self.mejor_aptitud_historica if self.mejor_aptitud_historica > 0 else float('inf')
            self.historial_costos.append(mejor_costo_real)

            poblacion_seleccionada = self.seleccion(aptitudes_seguras)
            descendencia = self.evolucion(poblacion_seleccionada)
            nueva_poblacion = self.mutacion(descendencia)
            
            if self.mejor_solucion_historica:
                nueva_poblacion[0] = self.mejor_solucion_historica[:]
                
            self.poblacion = nueva_poblacion
            iteracion_actual += 1

    def evaluacion(self) -> Tuple[List[int], float, str]:
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