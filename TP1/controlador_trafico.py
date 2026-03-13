class ControladorTrafico:

    def __init__(self, agentes):
        self.agentes = agentes

    def detectar_conflictos(self):

        conflictos = []

        for i in range(len(self.agentes)):
            for j in range(i+1, len(self.agentes)):

                a = self.agentes[i]
                b = self.agentes[j]

                sig_a = a.siguiente_posicion()
                sig_b = b.siguiente_posicion()

                if sig_a is None or sig_b is None:
                    continue

                # misma celda
                if sig_a == sig_b:
                    conflictos.append((a,b))

                # intercambio
                if sig_a == (b.x, b.y) and sig_b == (a.x, a.y):
                    conflictos.append((a,b))

        return conflictos


    def resolver_conflicto(self, a, b):

        # prioridad por costo restante
        if len(a.ruta) < len(b.ruta):
            ganador = a
            perdedor = b
        else:
            ganador = b
            perdedor = a

        # retroceder hasta liberar camino
        while perdedor.siguiente_posicion() == ganador.siguiente_posicion():

            if not perdedor.historial:
                break

            perdedor.retroceder()

        ganador.avanzar()


    def actualizar(self):

        conflictos = self.detectar_conflictos()

        if conflictos:

            for a,b in conflictos:
                self.resolver_conflicto(a,b)

        else:

            for agente in self.agentes:
                agente.avanzar()