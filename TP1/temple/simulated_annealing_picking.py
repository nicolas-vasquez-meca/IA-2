"""
simulated_annealing_picking.py

Capa de optimización global para el problema de picking en almacén.

Qué hace este módulo:
- Usa el A* ya implementado en la clase Agente para calcular distancias mínimas.
- Usa Simulated Annealing para optimizar el orden global de visita de estanterías.
- Soporta órdenes cargadas desde CSV.
- Usa caché para no recalcular A* entre los mismos pares de puntos.
- Puede reconstruir el recorrido completo final.

Integración esperada con el proyecto actual:
- main.py sigue construyendo el mapa con inicializar_simulacion().
- main.py puede importar este módulo y pedir la mejor secuencia para una orden.
- Luego, opcionalmente, puede animar el recorrido tramo por tramo con Pygame.
"""

from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------
# Imports robustos: funcionan tanto en el proyecto real como en pruebas
# ---------------------------------------------------------------------
try:
    from Agentes.Agente import Agente
except Exception:
    from Agente import Agente  # type: ignore

try:
    from entorno.estanteria import Estanteria
except Exception:
    from estanteria import Estanteria  # type: ignore

try:
    from entorno.mapa import Mapa
except Exception:
    from mapa import Mapa  # type: ignore

Coordinate = Tuple[int, int]


@dataclass(frozen=True)
class SegmentoRuta:
    """Representa un tramo del recorrido entre dos puntos del mapa."""

    origen: Coordinate
    destino: Coordinate
    costo: float
    camino: Tuple[Coordinate, ...]


@dataclass
class ResultadoSA:
    """Resultado completo de la optimización."""

    mejor_estado: List[int]
    mejor_costo: float
    historia_mejor_costo: List[float]
    historia_costo_actual: List[float]
    secuencia_puntos: List[Coordinate]
    recorrido_completo: List[Coordinate]
    segmentos: List[SegmentoRuta]
    iteraciones: int


class SimulatedAnnealingPicking:
    """
    Resuelve el orden de picking usando Simulated Annealing.

    Estado:
        permutación de identificadores de estanterías, por ejemplo [40, 26, 13, 14]

    Vecino:
        intercambio simple entre dos posiciones de la permutación.

    Costo:
        distancia(inicio, acceso_est_1) + suma distancias entre accesos consecutivos
        y opcionalmente regreso al inicio.
    """

    def __init__(
        self,
        mapa: Mapa,
        inicio: Coordinate,
        temperatura_inicial: float = 100.0,
        factor_enfriamiento: float = 0.995,
        temperatura_minima: float = 0.001,
        max_iteraciones: int = 5000,
        volver_al_origen: bool = False,
        semilla: Optional[int] = None,
    ) -> None:
        self.mapa = mapa
        self.inicio = inicio
        self.temperatura_inicial = temperatura_inicial
        self.factor_enfriamiento = factor_enfriamiento
        self.temperatura_minima = temperatura_minima
        self.max_iteraciones = max_iteraciones
        self.volver_al_origen = volver_al_origen

        self.random = random.Random(semilla)

        # id_estanteria -> objeto Estanteria
        self.estanterias: Dict[int, Estanteria] = self._indexar_estanterias()

        # Caché entre coordenadas exactas transitables
        self._cache_segmentos: Dict[Tuple[Coordinate, Coordinate], SegmentoRuta] = {}

        # Caché entre origen puntual y estantería destino: guarda mejor acceso elegido
        self._cache_hacia_estanteria: Dict[Tuple[Coordinate, int], SegmentoRuta] = {}

    # ================================================================
    # BÚSQUEDA DE ESTRUCTURA DEL MAPA
    # ================================================================
    def _indexar_estanterias(self) -> Dict[int, Estanteria]:
        """Recorre el mapa y arma un índice por identificador de estantería."""
        ests: Dict[int, Estanteria] = {}
        for x in range(self.mapa.ancho):
            for y in range(self.mapa.largo):
                casilla = self.mapa.obtener_casilla(x, y)
                if isinstance(casilla, Estanteria):
                    ests[casilla.identificador] = casilla
        return ests

    def obtener_estanteria(self, identificador: int) -> Estanteria:
        """Devuelve la estantería correspondiente al identificador solicitado."""
        if identificador not in self.estanterias:
            raise KeyError(f"No existe una estantería con identificador {identificador}.")
        return self.estanterias[identificador]

    def puntos_acceso_estanteria(self, identificador: int) -> List[Coordinate]:
        """
        Devuelve los puntos de acceso válidos de una estantería.

        Nota:
        En tu clase Estanteria los accesos están guardados en _puntos_acceso.
        Como actualmente no hay property pública, aquí se accede a ese atributo.
        Si luego agregan una property puntos_acceso, este método se puede simplificar.
        """
        est = self.obtener_estanteria(identificador)
        puntos = getattr(est, "_puntos_acceso", None)
        if puntos is None:
            raise AttributeError(
                "La estantería no expone _puntos_acceso. "
                "Agrega una property puntos_acceso o revisa la clase Estanteria."
            )

        puntos_validos: List[Coordinate] = []
        for punto in puntos:
            casilla = self.mapa.obtener_casilla(punto[0], punto[1])
            if casilla is not None and casilla.transitable:
                puntos_validos.append(punto)

        if not puntos_validos:
            raise ValueError(
                f"La estantería {identificador} no tiene puntos de acceso transitables."
            )
        return puntos_validos

    # ================================================================
    # A* APOYADO EN LA CLASE Agente YA EXISTENTE
    # ================================================================
    def _ejecutar_astar(self, origen: Coordinate, destino: Coordinate) -> SegmentoRuta:
        """
        Ejecuta el A* del proyecto creando un Agente nuevo.

        Se crea un agente nuevo por consulta para evitar contaminación de estado
        interno, ya que la clase Agente actual no tiene un método reiniciar().
        """
        if (origen, destino) in self._cache_segmentos:
            return self._cache_segmentos[(origen, destino)]

        agente = Agente(self.mapa)
        agente.set_objetivo(destino[0], destino[1])
        agente.set_Inicio(origen[0], origen[1])

        # Límite defensivo por si algo queda mal configurado
        max_pasos = self.mapa.ancho * self.mapa.largo * 20

        terminado = False
        pasos = 0
        while not terminado and pasos < max_pasos:
            resultado = agente.mover()
            if resultado is True:
                terminado = True
            pasos += 1

        if not agente.camino:
            raise ValueError(
                f"No se encontró camino A* entre {origen} y {destino}."
            )

        # IMPORTANTE:
        # En Agente.obtener_costo_camino() hoy se devuelve len(camino).
        # Eso sirve si todos los costos valen 1. Para mantener compatibilidad,
        # aquí usamos el costo g real del nodo objetivo, que es más correcto.
        costo_real = agente.visitados[(agente.x, agente.y)].g
        camino = tuple(agente.camino)

        segmento = SegmentoRuta(origen=origen, destino=destino, costo=costo_real, camino=camino)
        self._cache_segmentos[(origen, destino)] = segmento

        # Como el mapa es no dirigido y el costo de caminos es simétrico en este caso,
        # guardamos también el inverso.
        self._cache_segmentos[(destino, origen)] = SegmentoRuta(
            origen=destino,
            destino=origen,
            costo=costo_real,
            camino=tuple(reversed(camino)),
        )
        return segmento

    def _mejor_segmento_hacia_estanteria(self, origen: Coordinate, id_estanteria: int) -> SegmentoRuta:
        """
        Dado un punto de origen transitable y una estantería, elige el acceso válido
        que minimiza la distancia A*.

        En el mapa actual cada estantería tiene un solo acceso, pero este método ya
        queda preparado para varios accesos futuros.
        """
        clave = (origen, id_estanteria)
        if clave in self._cache_hacia_estanteria:
            return self._cache_hacia_estanteria[clave]

        mejor: Optional[SegmentoRuta] = None
        for acceso in self.puntos_acceso_estanteria(id_estanteria):
            segmento = self._ejecutar_astar(origen, acceso)
            if mejor is None or segmento.costo < mejor.costo:
                mejor = segmento

        if mejor is None:
            raise ValueError(
                f"No fue posible hallar un acceso válido hacia la estantería {id_estanteria}."
            )

        self._cache_hacia_estanteria[clave] = mejor
        return mejor

    # ================================================================
    # LECTURA DE ÓRDENES
    # ================================================================
    @staticmethod
    def cargar_ordenes_desde_csv(ruta_csv: str | Path) -> List[List[int]]:
        """
        Carga órdenes desde un CSV simple como el que mostraste:
            40,26,13,14,29,34,28
            32,23,22,36,17
            ...

        Cada fila se interpreta como una orden.
        """
        ruta = Path(ruta_csv)
        if not ruta.exists():
            raise FileNotFoundError(f"No existe el archivo: {ruta}")

        ordenes: List[List[int]] = []
        with ruta.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            for fila in reader:
                if not fila:
                    continue
                orden = [int(valor.strip()) for valor in fila if valor.strip()]
                if orden:
                    ordenes.append(orden)
        return ordenes

    @staticmethod
    def seleccionar_orden(ordenes: Sequence[Sequence[int]], indice: int) -> List[int]:
        """Devuelve una orden puntual por índice."""
        if indice < 0 or indice >= len(ordenes):
            raise IndexError(
                f"Índice de orden fuera de rango: {indice}. Total disponible: {len(ordenes)}"
            )
        return list(ordenes[indice])

    # ================================================================
    # VECINDAD, COSTO Y ACEPTACIÓN
    # ================================================================
    def estado_inicial(self, objetivos: Sequence[int]) -> List[int]:
        """Genera un estado inicial aleatorio."""
        estado = list(objetivos)
        self.random.shuffle(estado)
        return estado

    def generar_vecino(self, estado: Sequence[int]) -> List[int]:
        """
        Genera un vecino por simple permutación entre dos objetivos.
        Este punto coincide exactamente con lo que aclaraste.
        """
        vecino = list(estado)
        if len(vecino) < 2:
            return vecino
        i, j = self.random.sample(range(len(vecino)), 2)
        vecino[i], vecino[j] = vecino[j], vecino[i]
        return vecino

    def costo_estado(self, estado: Sequence[int]) -> float:
        """
        Calcula el costo total de una secuencia.

        Importante:
        - El estado se representa con IDs de estanterías.
        - Para cada estantería se elige el mejor punto de acceso desde la posición actual.
        - En el mapa actual hay un único acceso por estantería, así que esto es exacto.
        """
        if not estado:
            return 0.0

        costo_total = 0.0
        posicion_actual = self.inicio

        for id_estanteria in estado:
            segmento = self._mejor_segmento_hacia_estanteria(posicion_actual, id_estanteria)
            costo_total += segmento.costo
            posicion_actual = segmento.destino

        if self.volver_al_origen:
            costo_total += self._ejecutar_astar(posicion_actual, self.inicio).costo

        return costo_total

    @staticmethod
    def probabilidad_aceptacion(delta_e: float, temperatura: float) -> float:
        """Probabilidad de aceptar una solución peor."""
        if delta_e <= 0:
            return 1.0
        if temperatura <= 0:
            return 0.0
        return math.exp(-delta_e / temperatura)

    # ================================================================
    # RECONSTRUCCIÓN DEL RECORRIDO FINAL
    # ================================================================
    def reconstruir_ruta_estado(self, estado: Sequence[int]) -> Tuple[List[Coordinate], List[Coordinate], List[SegmentoRuta]]:
        """
        A partir de una secuencia de estanterías, reconstruye:
        - secuencia de puntos realmente visitados
        - recorrido completo concatenado
        - segmentos individuales
        """
        puntos_visitados: List[Coordinate] = [self.inicio]
        recorrido_total: List[Coordinate] = []
        segmentos: List[SegmentoRuta] = []

        posicion_actual = self.inicio

        for id_estanteria in estado:
            segmento = self._mejor_segmento_hacia_estanteria(posicion_actual, id_estanteria)
            segmentos.append(segmento)
            puntos_visitados.append(segmento.destino)

            if not recorrido_total:
                recorrido_total.extend(segmento.camino)
            else:
                recorrido_total.extend(segmento.camino[1:])

            posicion_actual = segmento.destino

        if self.volver_al_origen and posicion_actual != self.inicio:
            segmento = self._ejecutar_astar(posicion_actual, self.inicio)
            segmentos.append(segmento)
            puntos_visitados.append(self.inicio)
            if not recorrido_total:
                recorrido_total.extend(segmento.camino)
            else:
                recorrido_total.extend(segmento.camino[1:])

        return puntos_visitados, recorrido_total, segmentos

    # ================================================================
    # ALGORITMO PRINCIPAL
    # ================================================================
    def resolver(
        self,
        objetivos: Sequence[int],
        estado_inicial: Optional[Sequence[int]] = None,
    ) -> ResultadoSA:
        """
        Ejecuta Simulated Annealing.
        """
        if not objetivos:
            return ResultadoSA(
                mejor_estado=[],
                mejor_costo=0.0,
                historia_mejor_costo=[0.0],
                historia_costo_actual=[0.0],
                secuencia_puntos=[self.inicio],
                recorrido_completo=[self.inicio],
                segmentos=[],
                iteraciones=0,
            )

        # Validación temprana de IDs
        for objetivo in objetivos:
            self.obtener_estanteria(int(objetivo))

        estado_actual = list(estado_inicial) if estado_inicial is not None else self.estado_inicial(objetivos)
        costo_actual = self.costo_estado(estado_actual)

        mejor_estado = list(estado_actual)
        mejor_costo = costo_actual

        temperatura = self.temperatura_inicial
        historia_mejor_costo = [mejor_costo]
        historia_costo_actual = [costo_actual]

        iteracion = 0
        while temperatura > self.temperatura_minima and iteracion < self.max_iteraciones:
            vecino = self.generar_vecino(estado_actual)
            costo_vecino = self.costo_estado(vecino)

            delta_e = costo_vecino - costo_actual

            if delta_e < 0:
                estado_actual = vecino
                costo_actual = costo_vecino
            else:
                p = self.probabilidad_aceptacion(delta_e, temperatura)
                if self.random.random() < p:
                    estado_actual = vecino
                    costo_actual = costo_vecino

            if costo_actual < mejor_costo:
                mejor_estado = list(estado_actual)
                mejor_costo = costo_actual

            historia_mejor_costo.append(mejor_costo)
            historia_costo_actual.append(costo_actual)

            temperatura *= self.factor_enfriamiento
            iteracion += 1

        secuencia_puntos, recorrido_completo, segmentos = self.reconstruir_ruta_estado(mejor_estado)

        return ResultadoSA(
            mejor_estado=mejor_estado,
            mejor_costo=mejor_costo,
            historia_mejor_costo=historia_mejor_costo,
            historia_costo_actual=historia_costo_actual,
            secuencia_puntos=secuencia_puntos,
            recorrido_completo=recorrido_completo,
            segmentos=segmentos,
            iteraciones=iteracion,
        )

    # ================================================================
    # UTILIDADES DE CONSOLA / DEPURACIÓN
    # ================================================================
    def imprimir_resumen(self, resultado: ResultadoSA) -> None:
        """Imprime un resumen legible en consola."""
        print("\n===== RESULTADO SIMULATED ANNEALING =====")
        print("Inicio:", self.inicio)
        print("Mejor orden de estanterías:", resultado.mejor_estado)
        print("Costo total:", resultado.mejor_costo)
        print("Iteraciones:", resultado.iteraciones)
        print("Puntos visitados:", resultado.secuencia_puntos)

        print("\nSegmentos:")
        for i, segmento in enumerate(resultado.segmentos, start=1):
            print(
                f"  {i}. {segmento.origen} -> {segmento.destino} | "
                f"costo={segmento.costo} | pasos={len(segmento.camino)}"
            )

    @staticmethod
    def graficar_historial(resultado: ResultadoSA) -> None:
        """Grafica la evolución del costo si matplotlib está disponible."""
        try:
            import matplotlib.pyplot as plt
        except Exception:
            print("matplotlib no está disponible; no se puede graficar el historial.")
            return

        plt.figure(figsize=(10, 4))
        plt.plot(resultado.historia_costo_actual, label="Costo actual")
        plt.plot(resultado.historia_mejor_costo, label="Mejor costo")
        plt.xlabel("Iteración")
        plt.ylabel("Costo")
        plt.title("Evolución del costo - Simulated Annealing")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()


# =====================================================================
# FUNCIONES AUXILIARES DE INTEGRACIÓN CON EL MAIN ACTUAL
# =====================================================================
def optimizar_orden_desde_csv(
    mapa: Mapa,
    inicio: Coordinate,
    ruta_csv: str | Path,
    indice_orden: int = 0,
    temperatura_inicial: float = 100.0,
    factor_enfriamiento: float = 0.995,
    temperatura_minima: float = 0.001,
    max_iteraciones: int = 5000,
    volver_al_origen: bool = False,
    semilla: Optional[int] = 42,
) -> ResultadoSA:
    """
    Función de alto nivel para usar directo desde main.py.
    """
    solver = SimulatedAnnealingPicking(
        mapa=mapa,
        inicio=inicio,
        temperatura_inicial=temperatura_inicial,
        factor_enfriamiento=factor_enfriamiento,
        temperatura_minima=temperatura_minima,
        max_iteraciones=max_iteraciones,
        volver_al_origen=volver_al_origen,
        semilla=semilla,
    )

    ordenes = solver.cargar_ordenes_desde_csv(ruta_csv)
    orden = solver.seleccionar_orden(ordenes, indice_orden)
    resultado = solver.resolver(orden)
    return resultado


def optimizar_orden_manual(
    mapa: Mapa,
    inicio: Coordinate,
    orden: Sequence[int],
    temperatura_inicial: float = 100.0,
    factor_enfriamiento: float = 0.995,
    temperatura_minima: float = 0.001,
    max_iteraciones: int = 5000,
    volver_al_origen: bool = False,
    semilla: Optional[int] = 42,
) -> ResultadoSA:
    """Alternativa simple para pasar una orden manualmente."""
    solver = SimulatedAnnealingPicking(
        mapa=mapa,
        inicio=inicio,
        temperatura_inicial=temperatura_inicial,
        factor_enfriamiento=factor_enfriamiento,
        temperatura_minima=temperatura_minima,
        max_iteraciones=max_iteraciones,
        volver_al_origen=volver_al_origen,
        semilla=semilla,
    )
    return solver.resolver(list(orden))
