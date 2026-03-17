from Agentes.Agente import Agente
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
        

    def get_pos(self, camino, i):
        if i < len(camino):
            return camino[i]
        return camino[-1]
    

    def Step(self):

        estado_siguiente = []

        # 1️⃣ mirar el futuro (sin mover)
        for agente in self.agentes:
            if self.paso+1 < len(agente.camino):
                estado_siguiente.append(agente.camino[self.paso+1])

        # 2️⃣ resolver conflictos
        self.resolver_conflicto(estado_siguiente)

        # 3️⃣ ahora sí mover
        for agente in self.agentes:
            if self.paso+1 < len(agente.camino):
                agente.x, agente.y = agente.camino[self.paso+1]

        # 4️⃣ avanzar tiempo
        self.paso += 1


    def resolver_conflicto(self, estado_siguiente: list):

        # DEBUG
        if(self.paso >= 4 and self.paso <= 9):
            a: Agente = self.agentes[0]
            b: Agente = self.agentes[1]

            pos_a = self.get_pos(a.camino, self.paso)
            pos_b = self.get_pos(b.camino, self.paso)

            next_a = self.get_pos(a.camino, self.paso+1)
            next_b = self.get_pos(b.camino, self.paso+1)

            print(self.paso)
            print(pos_a)
            print(pos_b)
            print(next_a)
            print(next_b)
        # DEBUG
        
        # ////////////////////////////////////////////////////////////////////////////////////////////////
        #                        WARNING: Algoritmo de solo 2 agentes a la vez
        # ////////////////////////////////////////////////////////////////////////////////////////////////
        a: Agente = self.agentes[0]
        b: Agente = self.agentes[1]

        pos_a = self.get_pos(a.camino, self.paso)
        pos_b = self.get_pos(b.camino, self.paso)

        next_a = self.get_pos(a.camino, self.paso+1)
        next_b = self.get_pos(b.camino, self.paso+1)

        # -----------------------------------------------------------------------------------------------
        # ERROR: HAY CONFLICTO (por haber mas de 2 agentes)
        # -----------------------------------------------------------------------------------------------

        if len(self.agentes) != 2:
            print("Conflicto detectado, el algoritmo solo soporta 2 agentes")
            return

        # -----------------------------------------------------------------------------------------------
        # CASOS 1 y 2:
        # -----------------------------------------------------------------------------------------------

        ganador = self.prioridad(a, b)
        perdedor = b if ganador == a else a

        # -----------------------------------------------------------------------------------------------
        # CASO 1: uno llego a la posicion final y molesta al otro   
        # -----------------------------------------------------------------------------------------------

        if pos_a == b.objetivo and pos_b == b.objetivo:
            print("caso 1")
            nuevo_inicio = self.agentes[0].camino[self.paso-1]
            self.agentes[0].set_Inicio(nuevo_inicio)
            while not self.Mover_Agente(b.objetivo[0], b.objetivo[1], 0):
                pass

        elif pos_b == a.objetivo and pos_a == a.objetivo:
            print("caso 1")
            nuevo_inicio = self.agentes[1].camino[self.paso-1]
            self.agentes[1].set_Inicio(nuevo_inicio)

            while not self.Mover_Agente(a.objetivo[0], a.objetivo[1], 1):
                pass


        # -----------------------------------------------------------------------------------------------
        # CASO 2: ambos quieren la MISMA casilla   
        # -----------------------------------------------------------------------------------------------

        # Caso donde estan enfrentadas y quieren ir a la posicion del otro
        elif (pos_a == next_b and pos_b == next_a):

            print("caso 2a")
            # el perdedor retrocede una casilla
            if a == perdedor:
                camino = self.agentes[0].camino

                prev = camino[self.paso-1]
                actual = camino[self.paso]

                self.agentes[0].camino.insert(self.paso+1, prev)        # retrocede
                self.agentes[0].camino.insert(self.paso+2, actual)    # vuelve al original

            elif b == perdedor:
                camino = self.agentes[1].camino

                prev = camino[self.paso-1]
                actual = camino[self.paso]

                self.agentes[1].camino.insert(self.paso+1, prev)
                self.agentes[1].camino.insert(self.paso+2, actual)



        # Caso donde llegarian al mismo tiempo a la casilla
        elif (next_a == next_b):

            print("caso 2b: ⚠️ COLISIÓN futura detectada")
            # El perdedor espera
            if a == perdedor:
                # El perdedor etrocede pero luego debe seguir por donde venia
                self.agentes[0].camino.insert(self.paso, self.agentes[0].camino[self.paso])
                
            elif b == perdedor:
                # Retrocede pero luego debe seguir por donde venia
                self.agentes[1].camino.insert(self.paso, self.agentes[1].camino[self.paso])


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