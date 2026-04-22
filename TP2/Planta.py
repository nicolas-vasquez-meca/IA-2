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

    def apertura_a_Rv(self, apertura):
        return self.Rv_max * (1 - (apertura / 100.0))

    def paso(self, v, apertura, ve):
        # conversión interna
        Rv = self.apertura_a_Rv(apertura)
        return v + self.dt * (ve - v) / (self.C * (self.R + Rv))

# -----------------------------
# Simulación
# -----------------------------
def simular(planta, controlador, t_total):

    N = int(t_total / planta.dt)

    v = 20

    t_hist = []
    v_hist = []
    ve_hist = []
    Rv_hist = []

    for k in range(N):
        t = k * planta.dt

        ve = planta.temperatura_exterior(t)

        # controlador → % apertura
        apertura = controlador.control()

        # saturar apertura (no Rv!)
        apertura = max(0, min(apertura, 100))

        # planta usa apertura directamente
        v = planta.paso(v, apertura, ve)

        # guardar Rv real (solo para graficar)
        Rv = planta.apertura_a_Rv(apertura)

        # actualizar controlador
        controlador.set_V(v)
        controlador.set_Ve(ve)

        # guardar
        t_hist.append(t / 3600)
        v_hist.append(v)
        ve_hist.append(ve)
        Rv_hist.append(Rv)

    return t_hist, v_hist, ve_hist, Rv_hist

def simular_con_prediccion(planta, controlador, t_total, T_pred):

    N = int(t_total / planta.dt)

    v = 20  # inicial

    t_hist = []
    v_hist = []
    ve_hist = []
    Rv_hist = []

    for k in range(N):
        t = k * planta.dt

        ve = planta.temperatura_exterior(t)

        # 🔥 NUEVO: temperatura futura
        ve_pred = planta.temperatura_exterior(t + T_pred)

        # actualizar controlador
        controlador.set_V(v)
        controlador.set_Ve(ve)
        controlador.set_Ve_pred(ve_pred)
        controlador.set_t(t)

        # controlador → apertura
        apertura = controlador.control()

        # saturar
        apertura = max(0, min(apertura, 100))

        # planta
        v = planta.paso(v, apertura, ve)

        # guardar Rv real (solo para ver)
        Rv = planta.apertura_a_Rv(apertura)

        # guardar historial
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