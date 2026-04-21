import numpy as np
import matplotlib.pyplot as plt
from fuzzy_ctrl import fuzzy_ctrl   # tu clase

# -----------------------------
# Clase Planta
# -----------------------------
class Planta:

    def __init__(self, R, Rv_max, C, dt):
        self.R = R
        self.Rv_max = Rv_max
        self.C = C
        self.dt = dt

    def temperatura_exterior(self, t):
        return 20 + 10 * np.sin(2 * np.pi * t / (24 * 3600))

    def paso(self, v, apertura, ve):
        Rv = self.apertura_a_Rv(apertura)
        return v + self.dt * (ve - v) / (self.C * (self.R + Rv))

    def apertura_a_Rv(self, apertura):
        """
        apertura: 0 → ventana abierta
                  100 → ventana cerrada
        """
        return self.Rv_max * (apertura / 100)


# -----------------------------
# Simulación
# -----------------------------
def simular(planta, controlador, t_total):

    N = int(t_total / planta.dt)

    v = 20  # condición inicial

    t_hist = []
    v_hist = []
    ve_hist = []
    Rv_hist = []

    for k in range(N):
        t = k * planta.dt

        ve = planta.temperatura_exterior(t)

        # CONTROLADOR → devuelve % apertura
        apertura = controlador.control()

        # convertir a Rv
        Rv = planta.apertura_a_Rv(apertura)

        # saturación
        Rv = max(0, min(Rv, planta.Rv_max))

        # PLANTA
        v = planta.paso(v, Rv, ve)

        # actualizar controlador con nuevo estado
        controlador.set_V(v)
        controlador.set_Ve(ve)

        # guardar
        t_hist.append(t / 3600)
        v_hist.append(v)
        ve_hist.append(ve)
        Rv_hist.append(Rv)

    return t_hist, v_hist, ve_hist, Rv_hist


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":

    # Parámetros
    R = 1728
    Rv_max = 15552
    C = 1
    dt = 60
    t_total = 48 * 3600

    # Crear planta
    planta = Planta(R, Rv_max, C, dt)

    # Crear controlador difuso
    ctrl = fuzzy_ctrl(V_obj=25, Ve=20, V=20)

    # Simular
    t, v, ve, Rv = simular(planta, ctrl, t_total)

    # -----------------------------
    # Gráficos
    # -----------------------------
    plt.figure()
    plt.plot(t, ve, '--', label='Exterior')
    plt.plot(t, v, label='Interior')
    plt.axhline(25, linestyle='--', label='Confort')
    plt.legend()
    plt.grid()

    plt.figure()
    plt.plot(t, Rv, label='Rv')
    plt.legend()
    plt.grid()

    plt.show()