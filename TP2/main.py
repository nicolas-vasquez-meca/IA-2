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
    tiempo = range(0, n_puntos*dt_minutos, dt_minutos)

    planta = Planta(R, Rv_max, C, dt_minutos)

    ctrl = fuzzy_ctrl()
    ctrl.set_Obj = 25
    V_actual = 15
    apertura = 0

    T_controlada : list[float] = {}
    T_controlada.append[V_actual]

    for i in range(n_puntos-1):
 
        ctrl.set_Ve(temperaturas[i])
        ctrl.set_V(V_actual)
        apertura = ctrl.control()
        V_sig = planta.paso(V_actual, apertura, temperaturas[i])
        T_controlada.append(V_actual)
        V_actual = V_sig

    plt.figure()
    plt.plot(tiempo, temperaturas, '--', label='T_Exterior')
    plt.plot(tiempo, T_controlada, label='T_Interior')
    plt.axhline(25, linestyle='--', label='Confort')
    plt.legend()
    plt.grid()

    plt.show()
