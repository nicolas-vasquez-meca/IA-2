from Planta import Planta
import matplotlib.pyplot as plt
from fuzzy_ctrl import fuzzy_ctrl
from pronostico_tiempo import PronosticoTiempo


if __name__ == "__main__":

    n_puntos = 48
    pt = PronosticoTiempo()
    temperaturas : list[float] = pt.obtener_temperaturas_dia(23, 4, n_puntos)

    R = 1728
    Rv_min = 0
    Rv_max = 15552
    C = 1
    dt_minutos = 60*24/n_puntos

    planta = Planta(R, Rv_max, C, dt_minutos)

    ctrl = fuzzy_ctrl()
    ctrl.set_Obj = 25
    V = 15
    apertura = 0


    for i in range(n_puntos):

        planta.paso(V, apertura, temperaturas[i])
        ctrl.set_Ve()
        ctrl.set_V()
        apertura = ctrl.control()

