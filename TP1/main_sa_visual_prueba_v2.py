from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import pygame
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

try:
    from entorno.camino import Camino
    from entorno.pared import Pared
    from entorno.estanteria import Estanteria, Direccion
    from entorno.mapa import Mapa
except ImportError:
    from entorno.camino import Camino
    from entorno.pared import Pared
    from entorno.estanteria import Estanteria, Direccion
    from entorno.mapa import Mapa

from temple.simulated_annealing_picking import ResultadoSA, SimulatedAnnealingPicking

Coordinate = Tuple[int, int]


# ============================================================
# CONSTRUCCIÓN DEL MAPA
# ============================================================
def construir_bloque_estanterias(entorno: Mapa, x_origen: int, y_origen: int, id_inicial: int) -> None:
    for fila in range(4):
        for columna in range(2):
            x_actual = x_origen + columna
            y_actual = y_origen + fila
            id_actual = id_inicial + (fila * 2) + columna

            direcciones_acceso = [Direccion.IZQUIERDA] if columna == 0 else [Direccion.DERECHA]
            entorno.agregar_elemento(
                Estanteria(
                    x=x_actual,
                    y=y_actual,
                    identificador=id_actual,
                    direcciones=direcciones_acceso,
                    capacidad_maxima=10,
                )
            )


def inicializar_simulacion() -> Mapa:
    ancho_terreno = 15
    largo_terreno = 13
    entorno_simulacion = Mapa(ancho_terreno, largo_terreno)

    for x in range(ancho_terreno):
        for y in range(largo_terreno):
            if x == 0 or x == ancho_terreno - 1 or y == 0 or y == largo_terreno - 1:
                entorno_simulacion.agregar_elemento(Pared(x, y))

    construir_bloque_estanterias(entorno_simulacion, x_origen=3, y_origen=2, id_inicial=1)
    construir_bloque_estanterias(entorno_simulacion, x_origen=7, y_origen=2, id_inicial=9)
    construir_bloque_estanterias(entorno_simulacion, x_origen=11, y_origen=2, id_inicial=17)
    construir_bloque_estanterias(entorno_simulacion, x_origen=3, y_origen=7, id_inicial=25)
    construir_bloque_estanterias(entorno_simulacion, x_origen=7, y_origen=7, id_inicial=33)
    construir_bloque_estanterias(entorno_simulacion, x_origen=11, y_origen=7, id_inicial=41)

    entorno_simulacion.rellenar_espacios_vacios(lambda x_vacio, y_vacio: Camino(x_vacio, y_vacio))
    return entorno_simulacion


# ============================================================
# UTILIDADES
# ============================================================
def costo_segmentos(segmentos) -> int:
    return int(sum(seg.costo for seg in segmentos))


def posiciones_estanterias(solver: SimulatedAnnealingPicking, ids_estanterias: Sequence[int]) -> Dict[int, Coordinate]:
    posiciones: Dict[int, Coordinate] = {}
    for ident in ids_estanterias:
        est = solver.obtener_estanteria(int(ident))
        posiciones[int(ident)] = (est.x, est.y)
    return posiciones


def estanteria_objetivo_en_paso(
    recorrido: Sequence[Coordinate],
    resultado: ResultadoSA,
) -> List[int | None]:
    if not recorrido:
        return []

    objetivos_por_paso: List[int | None] = []
    idx_objetivo = 0
    acceso_actual = resultado.segmentos[idx_objetivo].destino if resultado.segmentos else None

    for pos in recorrido:
        objetivo_actual = resultado.mejor_estado[idx_objetivo] if idx_objetivo < len(resultado.mejor_estado) else None
        objetivos_por_paso.append(objetivo_actual)
        if acceso_actual is not None and pos == acceso_actual:
            idx_objetivo += 1
            if idx_objetivo < len(resultado.segmentos):
                acceso_actual = resultado.segmentos[idx_objetivo].destino
            else:
                acceso_actual = None

    return objetivos_por_paso


# ============================================================
# VISUALIZADOR PYGAME
# ============================================================
class VisualizadorPicking:
    def __init__(self, mapa: Mapa, tamano_celda: int = 48, panel_inferior: int = 95) -> None:
        pygame.init()
        self.mapa = mapa
        self.tamano_celda = tamano_celda
        self.panel_inferior = panel_inferior
        self.ancho = mapa.ancho * tamano_celda
        self.alto = mapa.largo * tamano_celda + panel_inferior
        self.screen = pygame.display.set_mode((self.ancho, self.alto))
        self.font = pygame.font.SysFont(None, int(tamano_celda * 0.55))
        self.font_small = pygame.font.SysFont(None, 28)
        self.clock = pygame.time.Clock()

        self.COLORS = {
            "bg": (235, 235, 235),
            "grid": (210, 210, 210),
            "wall": (0, 0, 0),
            "road": (255, 255, 255),
            "shelf": (255, 255, 255),
            "shelf_border": (70, 70, 70),
            "text": (20, 20, 20),
            "access": (240, 80, 80),
            "start": (240, 230, 0),
            "path_done": (126, 187, 245),
            "path_pending": (210, 235, 255),
            "agent": (10, 10, 10),
            "target_shelf": (255, 214, 102),
            "completed_shelf": (214, 196, 240),
            "order_shelf": (214, 196, 240),
            "panel": (245, 245, 245),
        }

    def close(self) -> None:
        pygame.quit()

    def _rect(self, x: int, y: int) -> pygame.Rect:
        return pygame.Rect(x * self.tamano_celda, y * self.tamano_celda, self.tamano_celda, self.tamano_celda)

    def _draw_access_triangle(self, x: int, y: int, orientation: str) -> None:
        px = x * self.tamano_celda
        py = y * self.tamano_celda
        half = self.tamano_celda // 2
        margin = self.tamano_celda // 5

        if orientation == "ARRIBA":
            pts = [(px + half, py), (px + margin, py + margin), (px + self.tamano_celda - margin, py + margin)]
        elif orientation == "ABAJO":
            pts = [
                (px + half, py + self.tamano_celda),
                (px + margin, py + self.tamano_celda - margin),
                (px + self.tamano_celda - margin, py + self.tamano_celda - margin),
            ]
        elif orientation == "IZQUIERDA":
            pts = [(px, py + half), (px + margin, py + margin), (px + margin, py + self.tamano_celda - margin)]
        else:
            pts = [
                (px + self.tamano_celda, py + half),
                (px + self.tamano_celda - margin, py + margin),
                (px + self.tamano_celda - margin, py + self.tamano_celda - margin),
            ]
        pygame.draw.polygon(self.screen, self.COLORS["access"], pts)

    def draw(
        self,
        recorrido_hecho: Iterable[Coordinate],
        recorrido_pendiente: Iterable[Coordinate],
        ids_orden: Sequence[int],
        estanteria_actual: int | None,
        estanterias_completadas: Sequence[int],
        pos_agente: Coordinate,
        inicio: Coordinate,
        texto_panel: str,
    ) -> None:
        self.screen.fill(self.COLORS["bg"])

        done_set = set(recorrido_hecho)
        pending_set = set(recorrido_pendiente)
        done_shelves = set(estanterias_completadas)
        order_shelves = set(ids_orden)

        for y in range(self.mapa.largo):
            for x in range(self.mapa.ancho):
                casilla = self.mapa.obtener_casilla(x, y)
                rect = self._rect(x, y)

                if isinstance(casilla, Pared):
                    pygame.draw.rect(self.screen, self.COLORS["wall"], rect)
                elif isinstance(casilla, Camino):
                    color = self.COLORS["road"]
                    if (x, y) in pending_set:
                        color = self.COLORS["path_pending"]
                    if (x, y) in done_set:
                        color = self.COLORS["path_done"]
                    if (x, y) == inicio:
                        color = self.COLORS["start"]
                    pygame.draw.rect(self.screen, color, rect)
                elif isinstance(casilla, Estanteria):
                    color = self.COLORS["shelf"]
                    if casilla.identificador in order_shelves:
                        color = self.COLORS["order_shelf"]
                    if casilla.identificador in done_shelves:
                        color = self.COLORS["completed_shelf"]
                    if estanteria_actual is not None and casilla.identificador == estanteria_actual:
                        color = self.COLORS["target_shelf"]
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, self.COLORS["shelf_border"], rect, 3)
                    label = self.font.render(str(casilla.identificador), True, self.COLORS["text"])
                    self.screen.blit(label, label.get_rect(center=rect.center))
                    if casilla.validar_acceso(x, y - 1):
                        self._draw_access_triangle(x, y, "ARRIBA")
                    if casilla.validar_acceso(x, y + 1):
                        self._draw_access_triangle(x, y, "ABAJO")
                    if casilla.validar_acceso(x - 1, y):
                        self._draw_access_triangle(x, y, "IZQUIERDA")
                    if casilla.validar_acceso(x + 1, y):
                        self._draw_access_triangle(x, y, "DERECHA")

                pygame.draw.rect(self.screen, self.COLORS["grid"], rect, 1)

        ax, ay = pos_agente
        center = (ax * self.tamano_celda + self.tamano_celda // 2, ay * self.tamano_celda + self.tamano_celda // 2)
        pygame.draw.circle(self.screen, self.COLORS["agent"], center, max(6, self.tamano_celda // 6))

        panel_y = self.mapa.largo * self.tamano_celda
        panel_rect = pygame.Rect(0, panel_y, self.ancho, self.panel_inferior)
        pygame.draw.rect(self.screen, self.COLORS["panel"], panel_rect)
        pygame.draw.line(self.screen, self.COLORS["wall"], (0, panel_y), (self.ancho, panel_y), 2)
        texto = self.font_small.render(texto_panel, True, self.COLORS["text"])
        self.screen.blit(texto, (12, panel_y + 30))

        pygame.display.flip()


# ============================================================
# FIGURAS CON MATPLOTLIB
# ============================================================
def dibujar_mapa_en_axes(
    ax,
    mapa: Mapa,
    solver: SimulatedAnnealingPicking,
    orden: Sequence[int],
    recorrido: Sequence[Coordinate],
    costo: float,
    titulo: str,
    inicio: Coordinate,
    shelf_order_color: str = "#d6c4f0",
    shelf_highlight_color: str = "#d6c4f0",
    path_color: str = "#86bdf5",
) -> None:
    ax.set_xlim(0, mapa.ancho)
    ax.set_ylim(mapa.largo + 1.8, 0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor("#efefef")

    order_set = set(orden)
    shelf_positions = posiciones_estanterias(solver, orden)

    for x in range(mapa.ancho):
        for y in range(mapa.largo):
            casilla = mapa.obtener_casilla(x, y)
            face = "white"
            edge = "#d0d0d0"
            lw = 1
            if isinstance(casilla, Pared):
                face = "#000000"
                edge = "#000000"
            elif isinstance(casilla, Estanteria):
                face = "white"
                edge = "#666666"
                lw = 2
                if casilla.identificador in order_set:
                    face = shelf_order_color
            rect = Rectangle((x, y), 1, 1, facecolor=face, edgecolor=edge, linewidth=lw)
            ax.add_patch(rect)
            if isinstance(casilla, Estanteria):
                ax.text(x + 0.5, y + 0.53, str(casilla.identificador), ha="center", va="center", fontsize=7)

    ax.add_patch(Rectangle((inicio[0], inicio[1]), 1, 1, facecolor="#f0e000", edgecolor="#d0c700", linewidth=1.5))
    ax.text(inicio[0] + 0.5, inicio[1] + 0.53, "C", ha="center", va="center", fontsize=9, fontweight="bold")

    if recorrido:
        xs = [p[0] + 0.5 for p in recorrido]
        ys = [p[1] + 0.5 for p in recorrido]
        ax.plot(xs, ys, color=path_color, linewidth=6, solid_capstyle="round")

    for est_id in orden:
        ex, ey = shelf_positions[est_id]
        ax.add_patch(Rectangle((ex, ey), 1, 1, facecolor=shelf_highlight_color, edgecolor="#666666", linewidth=2.5))
        ax.text(ex + 0.5, ey + 0.53, str(est_id), ha="center", va="center", fontsize=7)

    ax.set_title(f"{titulo}\n{list(orden)}\nCosto del camino: {int(costo)}", fontsize=12)


def mostrar_figura_comparacion(
    mapa: Mapa,
    solver: SimulatedAnnealingPicking,
    orden_original: Sequence[int],
    resultado: ResultadoSA,
    inicio: Coordinate,
) -> None:
    _, recorrido_original, segmentos_original = solver.reconstruir_ruta_estado(orden_original)

    fig, axs = plt.subplots(1, 2, figsize=(13, 5))
    fig.patch.set_facecolor("#efefef")

    dibujar_mapa_en_axes(
        axs[0],
        mapa,
        solver,
        orden_original,
        recorrido_original,
        costo_segmentos(segmentos_original),
        "Orden original",
        inicio,
    )
    dibujar_mapa_en_axes(
        axs[1],
        mapa,
        solver,
        resultado.mejor_estado,
        resultado.recorrido_completo,
        resultado.mejor_costo,
        "Mejor orden encontrado",
        inicio,
    )

    arrow = FancyArrowPatch((0.48, 0.56), (0.52, 0.56), transform=fig.transFigure, mutation_scale=55, color="black", arrowstyle="simple")
    fig.add_artist(arrow)
    plt.tight_layout(rect=(0.02, 0.02, 0.98, 0.95))
    plt.show()


def mostrar_evolucion_clara(
    resultado: ResultadoSA,
    costo_original: float,
    estado_inicial: Sequence[int],
    costo_inicial: float,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(resultado.historia_mejor_costo, linewidth=2.2, color="#1f77b4", label="Mejor costo encontrado")
    ax.axhline(costo_original, linestyle="--", linewidth=2, color="#d62728", label=f"Costo orden original = {int(costo_original)}")
    ax.scatter([0], [costo_inicial], color="#2ca02c", s=70, zorder=5, label=f"Estado inicial SA = {int(costo_inicial)}")
    ax.annotate(
        f"Inicial SA\n{list(estado_inicial)}\nCosto = {int(costo_inicial)}",
        xy=(0, costo_inicial),
        xytext=(18, 18),
        textcoords="offset points",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#aaaaaa"),
    )
    ax.annotate(
        f"Mejor final = {int(resultado.mejor_costo)}",
        xy=(len(resultado.historia_mejor_costo) - 1, resultado.historia_mejor_costo[-1]),
        xytext=(-110, 18),
        textcoords="offset points",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#aaaaaa"),
    )
    ax.set_xlabel("Iteración")
    ax.set_ylabel("Costo")
    ax.set_title("Evolución del mejor costo encontrado")
    ax.grid(True, alpha=0.35)
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.show()


# ============================================================
# ANIMACIÓN
# ============================================================
def animar_mejor_recorrido(
    mapa: Mapa,
    resultado: ResultadoSA,
    inicio: Coordinate,
    tamano_celda: int = 48,
    fps: int = 5,
) -> None:
    vis = VisualizadorPicking(mapa, tamano_celda=tamano_celda)
    pygame.display.set_caption("Simulated Annealing - Recorrido óptimo")

    recorrido = list(resultado.recorrido_completo)
    if not recorrido:
        return

    objetivos_por_paso = estanteria_objetivo_en_paso(recorrido, resultado)
    recogidas = set()
    indice = 0
    total_obj = len(resultado.mejor_estado)
    delay_ms = max(0, int(1000 / max(fps, 1)))

    running = True
    paused = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_RIGHT and paused and indice < len(recorrido) - 1:
                    indice += 1
                elif event.key == pygame.K_LEFT and paused and indice > 0:
                    indice -= 1

        if not paused and indice < len(recorrido) - 1:
            indice += 1
            pygame.time.delay(delay_ms)

        pos_actual = recorrido[indice]
        est_actual = objetivos_por_paso[indice] if indice < len(objetivos_por_paso) else None

        for idx_seg, seg in enumerate(resultado.segmentos):
            if pos_actual == seg.destino and idx_seg < len(resultado.mejor_estado):
                recogidas.add(resultado.mejor_estado[idx_seg])
        estanterias_completadas = list(recogidas)

        texto = (
            f"Orden óptima: {resultado.mejor_estado} | Objetivo actual: {est_actual if est_actual is not None else '-'} | "
            f"Recogidos: {len(estanterias_completadas)}/{total_obj} | Costo total: {int(resultado.mejor_costo)} | "
            f"ESPACIO pausa"
        )
        vis.draw(
            recorrido_hecho=recorrido[: indice + 1],
            recorrido_pendiente=recorrido[indice + 1 :],
            ids_orden=resultado.mejor_estado,
            estanteria_actual=est_actual,
            estanterias_completadas=estanterias_completadas,
            pos_agente=pos_actual,
            inicio=inicio,
            texto_panel=texto,
        )
        vis.clock.tick(60)

    vis.close()


# ============================================================
# CONSOLA
# ============================================================
def mostrar_resumen(
    orden_original: Sequence[int],
    costo_original: float,
    estado_inicial: Sequence[int],
    costo_inicial: float,
    resultado: ResultadoSA,
) -> None:
    print("\n" + "=" * 76)
    print("SIMULATED ANNEALING PARA PICKING")
    print("=" * 76)
    print(f"Orden original:          {list(orden_original)}")
    print(f"Costo orden original:    {int(costo_original)}")
    print(f"Estado inicial SA:       {list(estado_inicial)}")
    print(f"Costo estado inicial SA: {int(costo_inicial)}")
    print(f"Mejor orden encontrado:  {resultado.mejor_estado}")
    print(f"Mejor costo:             {int(resultado.mejor_costo)}")
    print(f"Mejora vs orden original:{int(costo_original - resultado.mejor_costo)}")
    print(f"Iteraciones:             {resultado.iteraciones}")
    print("=" * 76)


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================
def ejecutar_desde_csv(
    indice_orden: int = 0,
    temperatura_inicial: float = 100.0,
    factor_enfriamiento: float = 0.995,
    temperatura_minima: float = 0.001,
    max_iteraciones: int = 5000,
    volver_al_origen: bool = False,
    semilla: int = 42,
    tamano_celda: int = 48,
    fps_animacion: int = 5,
    mostrar_evolucion: bool = True,
    mostrar_comparacion: bool = True,
    mostrar_animacion: bool = True,
) -> None:
    mapa = inicializar_simulacion()
    inicio = (1, 6)

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

    ruta_csv = Path(__file__).with_name("ordenes.csv")
    ordenes = solver.cargar_ordenes_desde_csv(ruta_csv)
    orden_original = solver.seleccionar_orden(ordenes, indice_orden)
    costo_original = solver.costo_estado(orden_original)

    estado_inicial = solver.estado_inicial(orden_original)
    costo_inicial = solver.costo_estado(estado_inicial)
    resultado = solver.resolver(orden_original, estado_inicial=estado_inicial)

    mostrar_resumen(orden_original, costo_original, estado_inicial, costo_inicial, resultado)

    if mostrar_evolucion:
        mostrar_evolucion_clara(resultado, costo_original, estado_inicial, costo_inicial)

    if mostrar_comparacion:
        mostrar_figura_comparacion(mapa, solver, orden_original, resultado, inicio)

    if mostrar_animacion:
        animar_mejor_recorrido(mapa, resultado, inicio, tamano_celda=tamano_celda, fps=fps_animacion)


def main() -> None:
    ejecutar_desde_csv(
        indice_orden=25,
        temperatura_inicial=100.0,
        factor_enfriamiento=0.995,
        temperatura_minima=0.001,
        max_iteraciones=5000,
        volver_al_origen=False,
        semilla=42,
        tamano_celda=48,
        fps_animacion=5,
        mostrar_evolucion=True,
        mostrar_comparacion=True,
        mostrar_animacion=True,
    )


if __name__ == "__main__":
    main()
