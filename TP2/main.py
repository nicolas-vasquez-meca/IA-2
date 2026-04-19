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
        apertura = ctrl.control()