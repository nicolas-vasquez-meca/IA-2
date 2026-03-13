
from entorno.mapa import Mapa
from visualizacion.renderizador import RenderizadorPygame
from entorno.casilla import Casilla
import heapq


class Nodo:
    def __init__(self, mapa: Mapa):
        self.x : int
        self.y: int
        self.transitable: bool
        self.C_camino: int # Costo camino
        self.C_destino: int # Costo destino

        self.padre = (0,0)

        # Esto le dice a Python cómo comparar dos Nodos 
        # al hacer < entre estos. (lt es Less Than)

    def __lt__(self, otro):
        return self.C_destino+self.C_camino < otro.C_destino + otro.C_camino


class Agente:

    def __init__(self, mapa: Mapa, Render: RenderizadorPygame):
        self.x:int
        self.y: int
        self.C_camino: int
        self.mapa = mapa
        self.Render = Render

        self.objetivo = (0, 0)

        self.camino = set()
        self.frontera = []   # heap
        self.visitados = []     # lista

    def set_objetivo(self, x: int, y: int):
        self.objetivo = (x, y)

    def reconstruir_camino(self):
        pass

    def heuristica(self, x, y):
        return abs(x - self.objetivo[0]) + abs(y - self.objetivo[1])


    def buscar_nodo(self, x, y) -> Nodo:
        for nodo in self.frontera:
            if nodo.x == x and nodo.y == y:
                return nodo
        return None


    def verMapa(self, x: int, y: int) -> Nodo:

        if self.buscar_nodo(x,y) is None:

            casilla = self.mapa.obtener_casilla(x, y)
            h = self.heuristica(x, y)
            nodo = Nodo(x, y, casilla.transitable, casilla.costo + self.C_camino, h, (self.x, self.y))

            heapq.heappush(self.frontera, (nodo.C_camino + nodo.C_destino, nodo))
            return nodo
        else:
            return None


    def expandir(self, x: int, y: int):
        self.verMapa(x-1,y)
        self.verMapa(x+1,y)
        self.verMapa(x,y+1)
        self.verMapa(x,y-1)


    def mover(self):

        if (self.x, self.y) == self.objetivo:
            self.reconstruir_camino()
            return
        
        else:
            self.expandir()

            while self.frontera:

                _, nodo = heapq.heappop(self.frontera)

                if not nodo.transitable:
                    continue

                self.x = nodo.x
                self.y = nodo.y

                self.visitados.append((self.x, self.y))

                return