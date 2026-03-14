import math
import random
import heapq
from typing import Dict, Tuple, List, Optional, Any

import matplotlib.pyplot as plt


# ============================================================
# A* DE EJEMPLO SOBRE UNA GRILLA
# ============================================================

Position = Tuple[int, int]


def manhattan(a: Position, b: Position) -> int:
    """Heurística Manhattan para A* en grillas 4-conectadas."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar_grid(grid: List[List[int]], start: Position, goal: Position) -> Tuple[float, List[Position]]:
    """
    A* simple para una grilla.
    
    Convención de la grilla:
    - 0 = celda transitable
    - 1 = obstáculo / no transitable
    
    Retorna:
    - distancia mínima (cantidad de pasos)
    - camino completo desde start hasta goal
    
    Si no existe camino:
    - retorna (inf, [])
    """
    rows = len(grid)
    cols = len(grid[0])

    def in_bounds(pos: Position) -> bool:
        r, c = pos
        return 0 <= r < rows and 0 <= c < cols

    def passable(pos: Position) -> bool:
        r, c = pos
        return grid[r][c] == 0

    def neighbors(pos: Position) -> List[Position]:
        r, c = pos
        possible = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        return [p for p in possible if in_bounds(p) and passable(p)]

    open_heap = []
    heapq.heappush(open_heap, (0 + manhattan(start, goal), 0, start))

    came_from: Dict[Position, Optional[Position]] = {start: None}
    g_score: Dict[Position, float] = {start: 0}

    while open_heap:
        _, current_g, current = heapq.heappop(open_heap)

        if current == goal:
            # reconstrucción del camino
            path = []
            node = goal
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()
            return current_g, path

        for nxt in neighbors(current):
            tentative_g = g_score[current] + 1

            if nxt not in g_score or tentative_g < g_score[nxt]:
                g_score[nxt] = tentative_g
                f_score = tentative_g + manhattan(nxt, goal)
                heapq.heappush(open_heap, (f_score, tentative_g, nxt))
                came_from[nxt] = current

    return float("inf"), []


# ============================================================
# SIMULATED ANNEALING PARA PICKING
# ============================================================

class WarehousePickingSA:
    """
    Resuelve el orden óptimo aproximado de picking usando Simulated Annealing.
    
    Parámetros principales:
    - start_name: nombre del punto de inicio (por ejemplo 'C')
    - positions: diccionario {nombre_producto_o_estacion: (fila, columna)}
    - distance_provider: función externa que calcula distancia/camino entre dos posiciones
    - return_to_start: si True, al final vuelve al origen
    - initial_temp: temperatura inicial
    - cooling_rate: factor de enfriamiento
    - min_temp: temperatura mínima
    - max_iterations: máximo de iteraciones
    - seed: semilla para reproducibilidad
    """

    def __init__(
        self,
        start_name: str,
        positions: Dict[str, Position],
        distance_provider,
        return_to_start: bool = False,
        initial_temp: float = 100.0,
        cooling_rate: float = 0.995,
        min_temp: float = 1e-3,
        max_iterations: int = 5000,
        seed: Optional[int] = None,
    ):
        self.start_name = start_name
        self.positions = positions
        self.distance_provider = distance_provider
        self.return_to_start = return_to_start

        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        self.max_iterations = max_iterations

        if seed is not None:
            random.seed(seed)

        # Caché de distancias: (A, B) -> distancia
        self.distance_cache: Dict[Tuple[str, str], float] = {}

        # Caché de caminos: (A, B) -> lista de posiciones
        self.path_cache: Dict[Tuple[str, str], List[Position]] = {}

    # --------------------------------------------------------
    # Caché de distancias y caminos
    # --------------------------------------------------------
    def _get_distance_and_path(self, name_a: str, name_b: str) -> Tuple[float, List[Position]]:
        """
        Obtiene la distancia y el camino entre dos puntos usando caché.
        
        El distance_provider puede devolver:
        - solo distancia
        - o una tupla (distancia, camino)
        """
        if (name_a, name_b) in self.distance_cache:
            return self.distance_cache[(name_a, name_b)], self.path_cache.get((name_a, name_b), [])

        pos_a = self.positions[name_a]
        pos_b = self.positions[name_b]

        result = self.distance_provider(pos_a, pos_b)

        if isinstance(result, tuple) and len(result) == 2:
            dist, path = result
        else:
            dist = result
            path = []

        self.distance_cache[(name_a, name_b)] = dist
        self.path_cache[(name_a, name_b)] = path

        # Si el problema es no dirigido, podemos guardar también la inversa.
        # Para la distancia, dist(A,B) = dist(B,A). Para el camino, invertimos.
        self.distance_cache[(name_b, name_a)] = dist
        self.path_cache[(name_b, name_a)] = list(reversed(path)) if path else []

        return dist, path

    def _get_distance(self, name_a: str, name_b: str) -> float:
        """Obtiene solo la distancia entre dos puntos."""
        dist, _ = self._get_distance_and_path(name_a, name_b)
        return dist

    # --------------------------------------------------------
    # Estado inicial y vecinos
    # --------------------------------------------------------
    def random_state(self, products: List[str]) -> List[str]:
        """Genera una permutación aleatoria de los productos."""
        state = products[:]
        random.shuffle(state)
        return state

    def neighbor(self, state: List[str]) -> List[str]:
        """
        Genera un vecino intercambiando dos productos.
        """
        if len(state) < 2:
            return state[:]

        i, j = random.sample(range(len(state)), 2)
        new_state = state[:]
        new_state[i], new_state[j] = new_state[j], new_state[i]
        return new_state

    # --------------------------------------------------------
    # Costo
    # --------------------------------------------------------
    def route_cost(self, state: List[str]) -> float:
        """
        Calcula el costo total de la ruta:
        start -> p1 -> p2 -> ... -> pn -> (opcional) start
        """
        if not state:
            return 0.0

        total = 0.0

        # Desde inicio al primer producto
        total += self._get_distance(self.start_name, state[0])

        # Entre productos consecutivos
        for i in range(len(state) - 1):
            total += self._get_distance(state[i], state[i + 1])

        # Vuelta al inicio (opcional)
        if self.return_to_start:
            total += self._get_distance(state[-1], self.start_name)

        return total

    # --------------------------------------------------------
    # Aceptación
    # --------------------------------------------------------
    @staticmethod
    def acceptance_probability(delta_e: float, temperature: float) -> float:
        """
        Probabilidad de aceptar una peor solución.
        Si delta_e < 0, mejora; en ese caso se acepta siempre por fuera.
        """
        if temperature <= 0:
            return 0.0
        return math.exp(-delta_e / temperature)

    # --------------------------------------------------------
    # Resolución principal
    # --------------------------------------------------------
    def solve(self, products: List[str], initial_state: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Ejecuta Simulated Annealing y devuelve un diccionario con resultados.
        """
        if not products:
            return {
                "best_state": [],
                "best_cost": 0.0,
                "history": [],
                "iterations": 0,
            }

        # Estado inicial
        current_state = initial_state[:] if initial_state is not None else self.random_state(products)
        current_cost = self.route_cost(current_state)

        best_state = current_state[:]
        best_cost = current_cost

        temperature = self.initial_temp
        history = [current_cost]

        iteration = 0

        while temperature > self.min_temp and iteration < self.max_iterations:
            candidate_state = self.neighbor(current_state)
            candidate_cost = self.route_cost(candidate_state)

            delta_e = candidate_cost - current_cost

            # Si mejora, aceptar siempre
            if delta_e < 0:
                current_state = candidate_state
                current_cost = candidate_cost
            else:
                # Si empeora, aceptar con cierta probabilidad
                prob = self.acceptance_probability(delta_e, temperature)
                if random.random() < prob:
                    current_state = candidate_state
                    current_cost = candidate_cost

            # Actualizar mejor solución global
            if current_cost < best_cost:
                best_cost = current_cost
                best_state = current_state[:]

            history.append(best_cost)

            # Enfriamiento
            temperature *= self.cooling_rate
            iteration += 1

        return {
            "best_state": best_state,
            "best_cost": best_cost,
            "history": history,
            "iterations": iteration,
        }

    # --------------------------------------------------------
    # Reconstrucción del recorrido final completo
    # --------------------------------------------------------
    def build_full_route(self, best_state: List[str]) -> Tuple[List[str], List[Position]]:
        """
        Devuelve:
        - la secuencia lógica de nodos [C, P1, P2, ...]
        - el camino completo concatenado sobre la grilla
        
        Requiere que distance_provider devuelva también caminos.
        """
        if not best_state:
            return [self.start_name], [self.positions[self.start_name]]

        logical_route = [self.start_name] + best_state[:]
        if self.return_to_start:
            logical_route.append(self.start_name)

        full_path: List[Position] = []

        for i in range(len(logical_route) - 1):
            a = logical_route[i]
            b = logical_route[i + 1]
            _, segment = self._get_distance_and_path(a, b)

            if not segment:
                # Si no hay camino guardado, al menos concatenamos nodos
                segment = [self.positions[a], self.positions[b]]

            if i == 0:
                full_path.extend(segment)
            else:
                # Evitamos repetir el primer nodo del segmento
                full_path.extend(segment[1:])

        return logical_route, full_path

    # --------------------------------------------------------
    # Visualización de evolución del costo
    # --------------------------------------------------------
    @staticmethod
    def plot_history(history: List[float]) -> None:
        """Grafica la evolución del mejor costo encontrado."""
        plt.figure(figsize=(10, 4))
        plt.plot(history)
        plt.xlabel("Iteración")
        plt.ylabel("Mejor costo")
        plt.title("Evolución del costo - Simulated Annealing")
        plt.grid(True)
        plt.show()

    # --------------------------------------------------------
    # Visualización del recorrido sobre la grilla
    # --------------------------------------------------------
    def plot_grid_route(
        self,
        grid: List[List[int]],
        best_state: List[str],
        title: str = "Recorrido final sobre la grilla"
    ) -> None:
        """
        Dibuja la grilla, obstáculos, posiciones y el recorrido final.
        """
        logical_route, full_path = self.build_full_route(best_state)

        rows = len(grid)
        cols = len(grid[0])

        plt.figure(figsize=(8, 8))

        # Dibujar celdas
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 1:
                    plt.scatter(c, rows - 1 - r, marker='s', s=400)
                else:
                    plt.scatter(c, rows - 1 - r, marker='s', s=400, facecolors='none')

        # Dibujar posiciones etiquetadas
        for name, (r, c) in self.positions.items():
            plt.text(c, rows - 1 - r, name, ha='center', va='center', fontsize=10, fontweight='bold')

        # Dibujar camino
        if full_path:
            xs = [c for (r, c) in full_path]
            ys = [rows - 1 - r for (r, c) in full_path]
            plt.plot(xs, ys, linewidth=2)

        plt.title(title)
        plt.xticks(range(cols))
        plt.yticks(range(rows))
        plt.grid(True)
        plt.show()


# ============================================================
# EJEMPLO COMPLETO
# ============================================================

if __name__ == "__main__":
    # --------------------------------------------------------
    # Grilla del almacén
    # 0 = transitable
    # 1 = obstáculo
    # --------------------------------------------------------
    grid = [
        [0, 0, 0, 0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 1, 0],
        [0, 1, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 1, 0, 0],
    ]

    # --------------------------------------------------------
    # Posiciones importantes
    # --------------------------------------------------------
    positions = {
        "C":  (0, 0),   # estación / punto de inicio
        "P1": (0, 7),
        "P2": (2, 1),
        "P3": (3, 7),
        "P4": (5, 6),
        "P5": (4, 4),
    }

    # Orden a preparar
    order = ["P1", "P2", "P3", "P4", "P5"]

    # --------------------------------------------------------
    # Proveedor externo de distancias usando A*
    # --------------------------------------------------------
    def distance_provider(pos_a: Position, pos_b: Position) -> Tuple[float, List[Position]]:
        """
        Esta función representa tu integración con A*.
        En este ejemplo usamos el A* definido arriba.
        """
        return astar_grid(grid, pos_a, pos_b)

    # --------------------------------------------------------
    # Crear solver
    # --------------------------------------------------------
    solver = WarehousePickingSA(
        start_name="C",
        positions=positions,
        distance_provider=distance_provider,
        return_to_start=False,   # cambiar a True si quieres volver a C
        initial_temp=100.0,
        cooling_rate=0.995,
        min_temp=0.001,
        max_iterations=5000,
        seed=42,
    )

    # --------------------------------------------------------
    # Resolver
    # --------------------------------------------------------
    result = solver.solve(order)

    print("===== RESULTADO =====")
    print("Mejor orden encontrado:", result["best_state"])
    print("Costo total:", result["best_cost"])
    print("Iteraciones ejecutadas:", result["iterations"])

    logical_route, full_path = solver.build_full_route(result["best_state"])
    print("Ruta lógica:", " -> ".join(logical_route))

    # --------------------------------------------------------
    # Visualizaciones
    # --------------------------------------------------------
    solver.plot_history(result["history"])
    solver.plot_grid_route(grid, result["best_state"])