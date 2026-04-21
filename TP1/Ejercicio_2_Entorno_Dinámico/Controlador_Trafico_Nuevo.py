class ControladorTrafico:

    def __init__(self, agentes):
        self.agentes = agentes


    def siguiente_posicion(self, agente):

        # Si no hay frontera no hay siguiente movimiento
        if not agente.frontera:
            return None

        _, nodo = agente.frontera[0]   # mejor nodo del heap
        return (nodo.x, nodo.y)


    def detectar_conflictos(self):

        conflictos = []

        for i in range(len(self.agentes)):
            for j in range(i + 1, len(self.agentes)):

                a = self.agentes[i]
                b = self.agentes[j]

                sig_a = self.siguiente_posicion(a)
                sig_b = self.siguiente_posicion(b)

                if sig_a is None or sig_b is None:
                    continue

                # misma celda
                if sig_a == sig_b:
                    conflictos.append((a, b))

                # intercambio de posiciones
                if sig_a == (b.x, b.y) and sig_b == (a.x, a.y):
                    conflictos.append((a, b))

        return conflictos


    def resolver_conflicto(self, a, b):

        # prioridad al que esté más cerca del objetivo
        if a.heuristica(a.x, a.y) < b.heuristica(b.x, b.y):
            ganador = a
            perdedor = b
        else:
            ganador = b
            perdedor = a

        # el perdedor retrocede si puede
        if perdedor.visitados:
            perdedor.x, perdedor.y = perdedor.visitados.pop()

        # el ganador avanza
        ganador.mover()


    def actualizar(self):

        conflictos = self.detectar_conflictos()

        if conflictos:

            for a, b in conflictos:
                self.resolver_conflicto(a, b)

        else:

            for agente in self.agentes:
                agente.mover()