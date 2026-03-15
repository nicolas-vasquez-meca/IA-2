from TP1.Agentes.Agente import Agente

class ControladorTrafico:

    def __init__(self, agentes):
        self.agentes: list = agentes
        self.agentes_replanificar = set()

        self.paso = 0
        # planificación inicial
        for agente in self.agentes:

            while not agente.mover():
                pass


    def prioridad(self, a: Agente, b: Agente):

        da = a.heuristica(a.x, a.y)
        db = b.heuristica(b.x, b.y)

        if da < db:
            return a
        else:
            return b
        
        
    def Step(self):
        self.paso = self.paso + 1

        estado_actual: list = []

        for agente in self.agentes:
            estado_actual.append(agente.camino[self.paso])

        self.resolver_conflicto(estado_actual)


    def resolver_conflicto(self, estado_actual: list):

        # diccionario: clave = (x,y) , valor = lista de indices donde aparece
        ocurrencias = {}

        for i, posicion in enumerate(estado_actual): # 0, (1,2)

            if posicion not in ocurrencias:
                ocurrencias[posicion] = []            #ocurrencias[1,2] = [] #ocurrencias[4,5] = []

            ocurrencias[posicion].append(i)           # ocurrencias[1,2] = (0,3,4)  # ocurrencias[4,5] = (1,2,5)

        # buscar los que se repiten
        conflictos = {}
        total_repeticiones = 0

        for posicion, indices in ocurrencias.items(): # (1,2) => (0, 3, 4) len => 3

            if len(indices) > 1:
                conflictos[posicion] = indices       # (1,2) 
                total_repeticiones += len(indices)
        
        

        
