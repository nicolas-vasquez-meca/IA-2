
from entorno.mapa import Mapa
from entorno.casilla import Casilla
import heapq


class Nodo:

    def __init__(self, x, y, transitable, g, h, padre):

        self.x = x
        self.y = y

        self.transitable = transitable

        self.g = g  # costo camino
        self.h = h  # costo destino

        self.padre = padre

    def f(self):
        return self.g + self.h


class Agente:

    def __init__(self, mapa: Mapa):

        self.mapa = mapa

        self.x = 0
        self.y = 0

        self.objetivo = (0,0)

        self.camino = []
        self.visitados = {}
        self.frontera_heap = []
        self.frontera_dict = {}

    def set_Inicio(self, x: int, y: int):
        self.x = x
        self.y = y

        casilla: Casilla= self.mapa.obtener_casilla(x,y)

        if casilla is None:
            raise ValueError("La posición inicial no existe en el mapa")
        
        h = self.heuristica(x,y)

        nodo = Nodo(x,y,casilla.transitable,0,h,None)
        self.visitados[(x,y)] = nodo


    def set_objetivo(self, x: int, y: int):
        self.objetivo = (x, y)


    def reconstruir_camino(self):

        pos = (self.x,self.y)

        while pos is not None:

            self.camino.append(pos)

            nodo = self.visitados[pos]

            pos = nodo.padre

        self.camino.reverse()

    def heuristica(self, x, y):
        return abs(x - self.objetivo[0]) + abs(y - self.objetivo[1])


    def expandir(self):

        vecinos = [
            (self.x-1, self.y),
            (self.x+1, self.y),
            (self.x, self.y-1),
            (self.x, self.y+1)
        ]

        for x,y in vecinos:

            if (x,y) in self.visitados:
                continue

            if (x,y) in self.frontera_dict:
                continue

            casilla = self.mapa.obtener_casilla(x,y)
            if casilla is None or not casilla.transitable:
                continue

            g = self.visitados[(self.x,self.y)].g + casilla.costo
            h = self.heuristica(x,y)

            nodo = Nodo(x,y,casilla.transitable,g,h,(self.x,self.y))

            self.frontera_dict[(x,y)] = nodo

            heapq.heappush(self.frontera_heap,(nodo.f(),(x,y)))


    def mover(self) -> bool:

        if (self.x,self.y) == self.objetivo:

            if not self.camino:
                self.reconstruir_camino()
                return
            else:
                return True

        self.expandir()

        while self.frontera_heap:

            _, pos = heapq.heappop(self.frontera_heap)

            if pos not in self.frontera_dict:
                continue

            nodo = self.frontera_dict.pop(pos)

            if not nodo.transitable:
                continue

            self.x, self.y = pos

            self.visitados[pos] = nodo

            return False
        return True
    
    def obtener_costo_camino(self) -> int:
        if self.camino:
            return len(self.camino)
        else:
            return ValueError("El agente aun no llega a la meta (ejecutar mas veces mover())")
    