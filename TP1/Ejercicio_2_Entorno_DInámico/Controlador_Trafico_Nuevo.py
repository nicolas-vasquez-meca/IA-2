from TP1.Agentes.Agente import Agente
import heapq

class ControladorTrafico:

    def __init__(self, agentes):

        if len(agentes) != 2:
            raise ValueError("Solo se soportan 2 agentes")

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
                self.resolver_conflicto(estado_actual)


    def resolver_conflicto(self, estado_actual: list):

        # diccionario: clave = (x,y) , valor = lista de indices donde aparece
        ocurrencias = {}

        estado_copia = estado_actual

        for i, posicion in enumerate(estado_copia):

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
        # ERROR: HAY CONFLICTO (por haber mas de 2 agentes)
        # -----------------------------------------------------------------------------------------------

        if len(self.agentes) != 2:
            print("Conflicto detectado, el algoritmo solo soporta 2 agentes")
            return

        # -----------------------------------------------------------------------------------------------
        # CASO 0: NO HAY CONFLICTO
        # -----------------------------------------------------------------------------------------------

        if total_repeticiones == 0:
            return

        # -----------------------------------------------------------------------------------------------
        # CASOS 1 y 2:
        # -----------------------------------------------------------------------------------------------
        a: Agente = self.agentes[0]
        b: Agente = self.agentes[1]

        pos_a = estado_copia[0]
        pos_b = estado_copia[1]

        ganador = self.prioridad(a, b)
        perdedor = b if ganador == a else a

        # -----------------------------------------------------------------------------------------------
        # CASO 1: ambos quieren la MISMA casilla     
        # -----------------------------------------------------------------------------------------------

        if pos_a == b.objetivo and pos_b == b.objetivo:

            nuevo_inicio = self.agentes[0].camino[self.paso-1]
            self.agentes[0].set_Inicio[nuevo_inicio]
            while not self.Mover_Agente(b.objetivo[0], b.objetivo[1], 0):
                pass

        elif pos_b == a.objetivo and pos_a == a.objetivo:

            nuevo_inicio = self.agentes[1].camino[self.paso-1]
            self.agentes[1].set_Inicio[nuevo_inicio]

            while not self.Mover_Agente(a.objetivo[0], a.objetivo[1], 1):
                pass

        # -----------------------------------------------------------------------------------------------
        # CASO 2: ambos quieren la MISMA casilla   
        # -----------------------------------------------------------------------------------------------

        if pos_a == pos_b:

            # el que tiene prioridad avanza
            while not ganador.mover():
                pass

            # el otro se queda quieto
            if b == perdedor:
                self.agentes[1].camino.insert(self.paso, self.agentes[1].camino[self.paso])

            elif a == perdedor:
                self.agentes[0].camino.insert(self.paso, self.agentes[1].camino[self.paso])

        # -----------------------------------------------------------------------------------------------
        # CASO 3: intercambio de posiciones (están enfrentados)
        # -----------------------------------------------------------------------------------------------

        elif (self.paso + 1 < len(a.camino)
              and self.paso + 1 < len(b.camino)
              and pos_a == b.camino[self.paso + 1]
              and pos_b == a.camino[self.paso + 1]
            ):

            # el ganador avanza
            while not ganador.mover():
                pass

            # el perdedor retrocede una casilla
            if perdedor.visitados:
                perdedor.x, perdedor.y = perdedor.visitados.pop()


    """
        Lo usamos solo en el caso 1 dentro de resolver conflicto y es para evitar una
        posicion x, y especifica
    """
    def Mover_Agente(self, x: int, y:int, indice_agente: int):

        if (self.agentes[indice_agente].x,self.agentes[indice_agente].y) == self.agentes[indice_agente].objetivo:

            if not self.agentes[indice_agente].camino:
                self.agentes[indice_agente].reconstruir_camino()
                return
            else:
                return True

        self.agentes[indice_agente].expandir()
        # Esto elimina de la frontera el nodo que no queremos =============
        if (x, y) in self.agentes[indice_agente].frontera_dict:
            # Eliminar del dict
            del self.agentes[indice_agente].frontera_dict[(x, y)]
            
            # Eliminar de la lista y re-organizar heap
            h = self.agentes[indice_agente].frontera_heap()
            h[:] = [item for item in h if item[1] != (x, y)]
            heapq.heapify(h)
        #===================================================================


        while self.agentes[indice_agente].frontera_heap:

            _, pos = heapq.heappop(self.agentes[indice_agente].frontera_heap)

            if pos not in self.agentes[indice_agente].frontera_dict:
                continue

            nodo = self.agentes[indice_agente].frontera_dict.pop(pos)

            if not nodo.transitable:
                continue

            self.agentes[indice_agente].x, self.agentes[indice_agente].y = pos

            self.agentes[indice_agente].visitados[pos] = nodo

            return False
        return True