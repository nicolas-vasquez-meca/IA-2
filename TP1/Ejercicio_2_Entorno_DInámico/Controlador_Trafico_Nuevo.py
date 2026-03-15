class ControladorTrafico:

    def __init__(self, agentes):
        self.agentes = agentes
        self.agentes_replanificar = set()

        # planificación inicial
        for agente in self.agentes:
            agente.mover()


    def siguiente_posicion(self, agente):

        if not agente.frontera:
            return None

        _, nodo = agente.frontera[0]
        return (nodo.x, nodo.y)


    def prioridad(self, a, b):

        da = a.heuristica(a.x, a.y)
        db = b.heuristica(b.x, b.y)

        if da < db:
            return a, b
        else:
            return b, a


    def detectar_conflicto(self, a, b):

        sig_a = self.siguiente_posicion(a)
        sig_b = self.siguiente_posicion(b)

        if sig_a is None or sig_b is None:
            return None

        # misma celda
        if sig_a == sig_b:
            return "misma"

        # intercambio
        if sig_a == (b.x, b.y) and sig_b == (a.x, a.y):
            return "intercambio"

        return None


    def recalcular_A(self, agente):

        agente.frontera = []
        agente.visitados = []
        agente.mover()


    def actualizar(self):

        conflictos = []

        for i in range(len(self.agentes)):
            for j in range(i+1, len(self.agentes)):

                a = self.agentes[i]
                b = self.agentes[j]

                tipo = self.detectar_conflicto(a,b)

                if tipo:
                    conflictos.append((a,b,tipo))


        if conflictos:

            for a,b,tipo in conflictos:

                ganador, perdedor = self.prioridad(a,b)

                if tipo == "misma":

                    ganador.mover()
                    # perdedor se queda quieto
                    self.agentes_replanificar.add(perdedor)


                elif tipo == "intercambio":

                    ganador.mover()

                    if perdedor.visitados:
                        perdedor.x, perdedor.y = perdedor.visitados.pop()

                    self.agentes_replanificar.add(perdedor)


        else:

            for agente in self.agentes:

                if agente in self.agentes_replanificar:
                    self.recalcular_A(agente)

                agente.mover()

            self.agentes_replanificar.clear()