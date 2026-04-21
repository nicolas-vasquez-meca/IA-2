import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Parámetros
# -----------------------------
dt = 60
t_total = 48 * 3600
N = int(t_total / dt)

R = 1728
Rv_max = 15552
C = 1

# -----------------------------
# Temperatura exterior
# -----------------------------
def temperatura_exterior(t):
    return 20 + 10 * np.sin(2 * np.pi * t / (24 * 3600))

# -----------------------------
# Planta (UN PASO)
# -----------------------------
def planta(v, ve, R, Rv, C):
    return v + dt * (ve - v) / (C * (R + Rv))

# -----------------------------
# Controlador (ejemplo)
# -----------------------------
def controlador(v, ve, t):
    v0 = 25
    Z = (v - v0) * (ve - v)
    return Rv_max if Z >= 0 else 0

# -----------------------------
# Simulación
# -----------------------------
def simular():

    v = 20  # inicial

    t_hist = []
    v_hist = []
    ve_hist = []
    Rv_hist = []

    for k in range(N):
        t = k * dt

        ve = temperatura_exterior(t)

        # controlador usa estado actual
        Rv = controlador(v, ve, t)

        # limitar
        Rv = max(0, min(Rv, Rv_max))

        # planta calcula siguiente
        v = planta(v, ve, R, Rv, C)

        # guardar
        t_hist.append(t / 3600)
        v_hist.append(v)
        ve_hist.append(ve)
        Rv_hist.append(Rv)

    return t_hist, v_hist, ve_hist, Rv_hist

# -----------------------------
# MAIN
# -----------------------------
t, v, ve, Rv = simular()

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