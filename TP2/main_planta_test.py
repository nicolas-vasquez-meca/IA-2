#!/usr/bin/env python3
"""Main alternativo para probar la `Planta` con varios casos de resistencia de ventana.
Genera gráficas en PNG y muestra un resumen numérico por caso.
"""
import os
import runpy
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
PLANTA_PATH = os.path.join(HERE, 'Planta.py')

# Evitar que el código en Planta intente mostrar ventanas al importarlo.
plt.show = lambda *a, **k: None

mod = runpy.run_path(PLANTA_PATH)

simular = mod.get('simular')
Planta = mod.get('Planta')

if simular is None:
    raise RuntimeError('No se encontró la función simular en Planta.py')

if Planta is None:
    raise RuntimeError('No se encontró la clase Planta en Planta.py')

# Instancia de planta para pruebas
planta = Planta(R=1728, Rv_max=15552, C=1, dt=60)

class ControladorPorFun:
    def __init__(self, func, planta):
        self.func = func
        self.planta = planta
        self.step = 0

    def control(self):
        t = self.step * self.planta.dt
        self.step += 1
        Rv = self.func(t)
        apertura = 0 if self.planta.Rv_max == 0 else 100 * Rv / self.planta.Rv_max
        return max(0, min(apertura, 100))

    def set_V(self, v):
        self.v = v

    def set_Ve(self, ve):
        self.ve = ve

# Definición de casos:
def Rv_half_open(t):
    return planta.Rv_max / 2

def Rv_sinusoidal(t):
    # ventana que varía sinusoidalmente (más abierta de día)
    return planta.Rv_max * 0.5 * (1 + np.sin(2 * np.pi * t / (24 * 3600)))

def Rv_periodic_dayopen(t):
    hour = (t / 3600) % 24
    return 0 if 8 <= hour < 20 else planta.Rv_max

# Random toggles: crear RNG una vez para que cambie en el tiempo
rng = np.random.RandomState(seed=0)
def Rv_random_toggle(t):
    return 0 if rng.rand() > 0.5 else planta.Rv_max

def Rv_step_change(t):
    # cerrada la primera mitad de la simulación, abierta la segunda
    total_seconds = 48 * 3600
    return planta.Rv_max if t < (total_seconds / 2) else 0

CASES = {
    'abierta': lambda t: 0,
    'mitad_abierta': Rv_half_open,
    'sinusoidal': Rv_sinusoidal,
    'dia_abierta': Rv_periodic_dayopen,
    'random_toggle': Rv_random_toggle,
    'step': Rv_step_change,
}

OUT_DIR = os.path.join(HERE)
os.makedirs(OUT_DIR, exist_ok=True)

def run_case(name, func):
    controlador = ControladorPorFun(func, planta)
    t, v_hist, ve, Rv_hist = simular(planta, controlador, 48 * 3600)
    v = np.array(v_hist)
    summary = {
        'final': float(v[-1]),
        'min': float(v.min()),
        'max': float(v.max()),
        'mean': float(v.mean()),
    }

    # Guardar gráfica
    plt.figure()
    plt.plot(t, ve, label='Exterior', linestyle='dashed')
    plt.plot(t, v, label=f'Interior ({name})')
    plt.xlabel('Tiempo (horas)')
    plt.ylabel('Temperatura (°C)')
    plt.legend()
    plt.grid()
    out_path = os.path.join(OUT_DIR, f'planta_case_{name}.png')
    plt.savefig(out_path)
    plt.close()

    return summary, out_path

def main():
    results = {}
    for name, func in CASES.items():
        s, p = run_case(name, func)
        results[name] = (s, p)
        print(f"Caso '{name}': final={s['final']:.3f}, min={s['min']:.3f}, max={s['max']:.3f}, mean={s['mean']:.3f} -> {p}")

    print('\nGráficas guardadas en el directorio TP2 (archivos planta_case_*.png)')

if __name__ == '__main__':
    main()
