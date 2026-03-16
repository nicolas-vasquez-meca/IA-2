from TP1.Agentes.Agente import Agente

class ControladorTrafico:

    def __init__(self, agentes):

        # ⚠️ Esto estaba al revés en tu código
        # if len(agentes) == 2:
        #     return ValueError("Solo se pueden usar 2 agentes")

        if len(agentes) != 2:
            raise ValueError("Solo se soportan 2 agentes actualmente")

        self.agentes: list = agentes
        self.agentes_replanificar = set()

        self.paso = 0

        # planificación inicial (A*)
        for agente in self.agentes:

            # ejecuta mover() hasta que termine de calcular el camino
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

            # ⚠️ prevención de error si el camino termina
            if self.paso < len(agente.camino):
                estado_actual.append(agente.camino[self.paso])
            else:
                estado_actual.append((agente.x, agente.y))

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

        # -----------------------------------------------------------------------------------------------
        # CASO 1: NO HAY CONFLICTO
        # -----------------------------------------------------------------------------------------------

        if total_repeticiones == 0:

            for agente in self.agentes:

                if agente in self.agentes_replanificar:

                    # recalcular A*
                    agente.frontera = []
                    agente.visitados = []

                    while not agente.mover():
                        pass

                else:
                    agente.mover()

            self.agentes_replanificar.clear()
            return


        # -----------------------------------------------------------------------------------------------
        # A PARTIR DE AQUÍ SOLO FUNCIONA CORRECTAMENTE PARA 2 AGENTES
        # -----------------------------------------------------------------------------------------------

        if len(self.agentes) != 2:
            print("Conflicto detectado pero el algoritmo solo soporta 2 agentes")
            return


        a = self.agentes[0]
        b = self.agentes[1]

        pos_a = estado_actual[0]
        pos_b = estado_actual[1]

        ganador = self.prioridad(a, b)
        perdedor = b if ganador == a else a


        # -----------------------------------------------------------------------------------------------
        # CASO 2: ambos quieren la MISMA casilla
        # -----------------------------------------------------------------------------------------------

        if pos_a == pos_b:

            # el que tiene prioridad avanza
            while not ganador.mover():
                pass

            # el otro se queda quieto
            self.agentes_replanificar.add(perdedor)


        # -----------------------------------------------------------------------------------------------
        # CASO 3: intercambio de posiciones (están enfrentados)
        # -----------------------------------------------------------------------------------------------

        elif pos_a == (b.x, b.y) and pos_b == (a.x, a.y):

            # el ganador avanza
            while not ganador.mover():
                pass

            # el perdedor retrocede una casilla
            if perdedor.visitados:
                perdedor.x, perdedor.y = perdedor.visitados.pop()

            self.agentes_replanificar.add(perdedor)