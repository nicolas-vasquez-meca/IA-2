import numpy as np
import matplotlib.pyplot as plt
import inspect

# -----------------------------
# Parámetros del sistema
# -----------------------------
R = 1728                     # resistencia base
Rv_max = 15552              # ventana totalmente cerrada
dt = 60                     # paso de tiempo (1 minuto)
t_total = 48 * 3600         # 48 horas
N = int(t_total / dt)

# -----------------------------
# Temperatura exterior (ejemplo)
# -----------------------------
def temperatura_exterior(t):
    # ciclo diario (en segundos)
    return 20 + 10 * np.sin(2 * np.pi * t / (24 * 3600))

# -----------------------------
# Modelo de la planta
# -----------------------------
def planta(v, ve, Rv):
    return v + dt * (ve - v) / (R + Rv)

# -----------------------------
# Simulación
# -----------------------------
def simular(Rv_func):
    v = 20  # temperatura inicial
    historial_v = []
    historial_ve = []
    tiempo = []

    for k in range(N):
        t = k * dt
        ve = temperatura_exterior(t)
        # Soportar dos tipos de funciones pasadas:
        # - Rv_func(t)  -> función que depende sólo del tiempo
        # - controlador(v, ve, t) -> controlador que decide Rv en base al estado
        Rv = None
        try:
            sig = inspect.signature(Rv_func)
            params = len(sig.parameters)
        except (TypeError, ValueError):
            params = None

        if params == 1:
            Rv = Rv_func(t)
        elif params == 3:
            Rv = Rv_func(v, ve, t)
        else:
            # fallback: intentar ambas formas
            try:
                Rv = Rv_func(t)
            except TypeError:
                Rv = Rv_func(v, ve, t)

        v = planta(v, ve, Rv)

        historial_v.append(v)
        historial_ve.append(ve)
        tiempo.append(t / 3600)  # en horas

    return tiempo, historial_v, historial_ve

# -----------------------------
# Casos de prueba
# -----------------------------

# Ventana siempre abierta
def Rv_abierta(t):
    return 0

# Ventana siempre cerrada
def Rv_cerrada(t):
    return Rv_max

# -----------------------------
# Ejecutar simulaciones
# -----------------------------
t, v_abierta, ve = simular(Rv_abierta)
_, v_cerrada, _ = simular(Rv_cerrada)

# -----------------------------
# Gráficos
# -----------------------------
plt.figure()
plt.plot(t, ve, label="Exterior", linestyle="dashed")
plt.plot(t, v_abierta, label="Interior (ventana abierta)")
plt.plot(t, v_cerrada, label="Interior (ventana cerrada)")
plt.xlabel("Tiempo (horas)")
plt.ylabel("Temperatura (°C)")
plt.legend()
plt.grid()
plt.show()