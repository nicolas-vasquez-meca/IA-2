from TP1.Agentes.Agente import Agente

class ControladorTrafico:

    def __init__(self, agentes):

        if len(agentes) == 2:
            return ValueError("Solo se pueden usar 2 agentes, cambiar resolver_conflicto() despues del warning para mas agentes")
        
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

        for i, posicion in enumerate(estado_actual):

            if posicion not in ocurrencias:
                ocurrencias[posicion] = []         

            ocurrencias[posicion].append(i)         

        # buscar los que se repiten
        conflictos = {}
        total_repeticiones = 0

        for posicion, indices in ocurrencias.items(): 

            if len(indices) > 1:
                conflictos[posicion] = indices       
                total_repeticiones += len(indices)
        
        # ////////////////////////////////////////////////////////////////////////////////////////////////
        #                        WARNING: Algoritmo de solo 2 agentes a la vez
        # ////////////////////////////////////////////////////////////////////////////////////////////////
        

