
    from entorno.mapa import Mapa
    from entorno.casilla import Casilla
    import heapq


    class Nodo:
        def __init__(self, mapa: Mapa):
            self.x : int
            self.y: int
            self.transitable: bool
            self.Cc: int # Costo camino
            self.Cd: int # Costo destino

            self.padre = (0,0)
            # Esto le dice a Python cómo comparar dos Nodos 
            # al hacer < entre estos. (lt es Less Than)
        def __lt__(self, otro):
            return self.Cd+self.Cc < otro.Cd + otro.Cc


    class Agente:

        def __init__(self, mapa: Mapa):
            self.x:int
            self.y: int
            self.Cc: int
            self.mapa = mapa

            self.objetivo = (0, 0)

            self.visitados = set() #set
            self.frontera = []   # heap
            self.camino = []     # lista

        def set_objetivo(self, x: int, y: int):
            self.objetivo = (x, y)

        def reconstruir_camino(self):
            


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
                nodo = Nodo(x, y, casilla.transitable, casilla.costo + self.Cc, h, (self.x, self.y))

                heapq.heappush(self.frontera, (nodo.Cc + nodo.Cd, nodo))
                self.Pintar("gris")
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
                    self.Pintar("amarillo")

                    return

        def Pintar(self, color: str):
            pass