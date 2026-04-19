from Planta import simular, Rv_max
import matplotlib.pyplot as plt
from TP2.main_ejemplo import FuzzyCtrl

# -----------------------------
# Controlador (ejemplo) (aqui ya le toca a los de controlador)
# -----------------------------
ctrl_difuso = FuzzyCtrl(Rv_max)

# -----------------------------
# MAIN
# -----------------------------
def main():

    # Ejecutar simulación
    t, v, ve = simular(ctrl_difuso)

    # Graficar
    plt.figure()
    plt.plot(t, ve, label="Exterior", linestyle="dashed")
    plt.plot(t, v, label="Interior (controlado)")
    plt.xlabel("Tiempo (horas)")
    plt.ylabel("Temperatura (°C)")
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()
"""""
from fuzzy_ctrl import fuzzy_ctrl
from Planta import temperatura_exterior
from Planta import planta
from Planta import simular
import numpy as np


if __name__ == "__main__":
    ctrl = fuzzy_ctrl()
    n_puntos = 48
    apertura = 0

    for i in range(n_puntos):
        

        ctrl.set_Ve(       )
        ctrl.set_V(       )
        apertura = ctrl.control()/
"""""