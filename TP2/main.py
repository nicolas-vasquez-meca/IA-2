from Planta import Planta
import matplotlib.pyplot as plt
from fuzzy_ctrl import fuzzy_ctrl
from pronostico_tiempo import PronosticoTiempo
import numpy as np


if __name__ == "__main__":

    n_puntos = 48
    pt = PronosticoTiempo()
    temperaturas = np.array(pt.obtener_temperaturas_dia(1, 2, n_puntos))

    R = 1728
    Rv_min = 0
    Rv_max = 15552
    C = 1
    dt_minutos = 3600*24/n_puntos

    tiempo = []
    for i in range(n_puntos):
        tiempo.append(i*dt_minutos)

    planta = Planta(R, Rv_max, C, dt_minutos)

    V_obj = 25
    V_actual = 22

    ctrl = fuzzy_ctrl(V_obj, temperaturas[0],V_actual)
    apertura = 0
    aperturas = []
    aperturas.append(0)

    T_controlada = []
    T_controlada.append(V_actual)

    for i in range(n_puntos-1):
 
        ctrl.set_Ve(temperaturas[i])
        ctrl.set_V(V_actual)
        apertura = ctrl.control()
        aperturas.append(apertura)

        V_sig = planta.paso(V_actual, apertura, temperaturas[i])
        V_actual = V_sig
        T_controlada.append(V_sig)

    rms = np.sqrt(np.mean(np.square(T_controlada)))
    print(rms - V_obj)

    plt.figure()
    plt.plot(tiempo, temperaturas, '*', label='T_Exterior')
    plt.plot(tiempo, T_controlada, label='T_Interior')
    plt.axhline(25, linestyle='--', label='Confort')
    plt.legend()
    plt.grid()

    plt.figure()
    plt.plot(tiempo, aperturas)
    plt.grid()
    plt.show()