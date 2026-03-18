from Agentes.Agente import Agente
import heapq

class ControladorTrafico:

    def __init__(self, agentes):

        if len(agentes) != 2:
            raise ValueError("Solo se soportan 2 agentes")

        self.agentes: list = agentes
        self.paso = 0

        self.llego_A = False
        self.llego_B = False


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

        if self.paso == 0:
            for agente in self.agentes:
                while not agente.mover():
                    pass

        estado_siguiente = []

        # ---------------------------
        # SIEMPRE FUTURO (consistente)
        # ---------------------------
        for agente in self.agentes:
            next_pos = self.get_pos(agente.camino, self.paso + 1)
            estado_siguiente.append(next_pos)

        # ---------------------------
        # resolver conflictos
        # ---------------------------
        self.resolver_conflicto(estado_siguiente)

        # ---------------------------
        # mover agentes
        # ---------------------------
        i = 0
        for agente in self.agentes:
            next_pos = self.get_pos(agente.camino, self.paso + 1)

            if i == 0 and not self.llego_A:
                agente.x, agente.y = next_pos

            elif i == 1 and not self.llego_B:
                agente.x, agente.y = next_pos

            # check llegada
            if i == 0 and (agente.x, agente.y) == agente.objetivo:
                self.llego_A = True

            elif i == 1 and (agente.x, agente.y) == agente.objetivo:
                self.llego_B = True

            i += 1

        self.paso += 1


    def resolver_conflicto(self, estado_siguiente: list):

        # DEBUG
        a: Agente = self.agentes[0]
        b: Agente = self.agentes[1]

        pos_a = self.get_pos(a.camino, self.paso)
        pos_b = self.get_pos(b.camino, self.paso)

        next_a = estado_siguiente[0]
        next_b = estado_siguiente[1]

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

        next_a = estado_siguiente[0]
        next_b = estado_siguiente[1]

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

        if self.llego_A and next_b == pos_a: # Cambiamos la trayectoria de B
            print("🚫 B quiere entrar al objetivo ocupado por A")

            x,y = self.agentes[1].camino[self.paso]
            self.agentes[1].set_Inicio(x,y)

            while not self.Mover_Agente(a.objetivo, 1):
                pass




        if self.llego_B and next_a == pos_b: # Cambiamos la trayectoria de A
            print("🚫 A quiere entrar al objetivo ocupado por B")

            x,y = self.agentes[0].camino[self.paso]
            self.agentes[0].set_Inicio(x,y)

            while not self.Mover_Agente(b.objetivo, 0):
                pass


        # -----------------------------------------------------------------------------------------------
        # CASO 2: ambos quieren la MISMA casilla   
        # -----------------------------------------------------------------------------------------------

        # Caso donde estan enfrentadas y quieren ir a la posicion del otro
        elif (pos_a == next_b and pos_b == next_a):

            print("caso 2a")
            # el perdedor retrocede una casilla
            if a == perdedor:
                camino = a.camino

                prev = camino[self.paso-1]
                actual = camino[self.paso]
                actual_ganador = b.camino[self.paso]

                indx: int = 1
                while prev == actual or prev == actual_ganador:
                    indx += 1

                    if indx <= self.paso:
                        prev = camino[self.paso-indx]
                    else:
                        break

                self.agentes[0].camino.insert(self.paso+1, prev)        # retrocede
                self.agentes[0].camino.insert(self.paso+2, actual)    # vuelve al original

            elif b == perdedor:
                camino = b.camino

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


    def Mover_Agente(self, objetivo_bloqueado, indice_agente):

        agente = self.agentes[indice_agente]

        camino_viejo = agente.camino[:self.paso+1]

        # reset A*
        agente.camino = []
        agente.visitados = {}
        agente.frontera_heap = []
        agente.frontera_dict = {}

        agente.set_Inicio(agente.x, agente.y)

        while True:
            agente.expandir()

            # 🚫 bloquear celda
            if objetivo_bloqueado in agente.frontera_dict:
                del agente.frontera_dict[objetivo_bloqueado]

                agente.frontera_heap = [
                    item for item in agente.frontera_heap
                    if item[1] != objetivo_bloqueado
                ]
                heapq.heapify(agente.frontera_heap)

            if not agente.frontera_heap:
                break

            _, pos = heapq.heappop(agente.frontera_heap)

            if pos not in agente.frontera_dict:
                continue

            nodo = agente.frontera_dict.pop(pos)

            if not nodo.transitable:
                continue

            agente.x, agente.y = pos
            agente.visitados[pos] = nodo

            if pos == agente.objetivo:
                agente.reconstruir_camino()

                # fusionar caminos
                nuevo_camino = agente.camino

                # evitar duplicar la posición actual
                agente.camino = camino_viejo + nuevo_camino[1:]

                return True

        return False