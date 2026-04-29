import numpy as np
import matplotlib.pyplot as plt

from Planta import Planta
from bang_bang_ctrl import BangBangCtrl
from pronostico_tiempo import PronosticoTiempo


# =========================================================
# CONFIGURACION GENERAL
# =========================================================

V_OBJ = 25.0
V_INICIAL = 22.0

R = 1728
RV_MAX = 15552
C = 1

# =========================================================
# CONFIGURACION TEMPORAL
# Igual que el test fuzzy de tu compañero
# =========================================================

N_PUNTOS = 48
DT_S = (24 * 3600) / N_PUNTOS

MOSTRAR_GRAFICOS = True


# =========================================================
# SERIE EXTERIOR
# =========================================================

def obtener_serie_exterior():
    """
    Mismo escenario que el test fuzzy:
    día 1 / mes 2
    """

    dia = 25
    mes = 12

    pt = PronosticoTiempo()

    temperaturas = np.array(
        pt.obtener_temperaturas_dia(
            dia,
            mes,
            N_PUNTOS
        ),
        dtype=float
    )

    return temperaturas, dia, mes


# =========================================================
# SIMULACION
# =========================================================

def simular_bang_bang(
        temperaturas_exteriores,
        V_obj,
        V_inicial,
        R,
        Rv_max,
        C,
        dt_s
):

    planta = Planta(
        R=R,
        Rv_max=Rv_max,
        C=C,
        dt=dt_s
    )

    controlador = BangBangCtrl(
        V_obj=V_obj,
        Ve=float(temperaturas_exteriores[0]),
        V=V_inicial
    )

    tiempo_s = np.array(
        [i * dt_s for i in range(len(temperaturas_exteriores))],
        dtype=float
    )

    tiempo_h = tiempo_s / 3600.0

    T_ext = np.array(temperaturas_exteriores, dtype=float)

    T_int = [float(V_inicial)]
    errores = [float(V_inicial - V_obj)]
    aperturas = [0.0]

    v = float(V_inicial)

    for i in range(len(T_ext) - 1):

        ve = float(T_ext[i])

        controlador.set_V(v)
        controlador.set_Ve(ve)

        apertura = float(controlador.control())

        aperturas.append(apertura)

        v_sig = planta.paso(
            v=v,
            apertura=apertura,
            ve=ve
        )

        v = float(v_sig)

        T_int.append(v)
        errores.append(v - V_obj)

    return {
        "tiempo_s": np.array(tiempo_s),
        "tiempo_h": np.array(tiempo_h),
        "T_ext": np.array(T_ext),
        "T_int": np.array(T_int),
        "error": np.array(errores),
        "apertura": np.array(aperturas),
    }


# =========================================================
# METRICAS
# =========================================================

def calcular_metricas(resultado, V_obj):

    tiempo_h = resultado["tiempo_h"]
    T_int = resultado["T_int"]
    error = resultado["error"]
    apertura = resultado["apertura"]

    # =====================================================
    # Intervalo útil de evaluación
    # =====================================================

    mask_util = (tiempo_h >= 8.0) & (tiempo_h <= 20.0)

    error_util = error[mask_util]
    error_total = error

    # =====================================================
    # RMS
    # =====================================================

    rms_util = np.sqrt(np.mean(error_util**2))     # °C
    rms_total = np.sqrt(np.mean(error_total**2))   # °C

    # =====================================================
    # Métrica J
    # =====================================================

    J_util = np.mean(error_util)                   # °C
    J_total = np.mean(error_total)                 # °C

    # =====================================================
    # Error máximo absoluto
    # =====================================================

    error_max_util = np.max(np.abs(error_util))    # °C
    error_max_total = np.max(np.abs(error_total))  # °C

    # =====================================================
    # Temperaturas extrema de TODO el día
    # =====================================================

    temp_min_total = np.min(T_int)                 # °C
    temp_max_total = np.max(T_int)                 # °C

    # =====================================================
    # Bandas de confort
    # =====================================================

    pct_1C_util = 100.0 * np.mean(np.abs(error_util) <= 1.0)
    pct_05C_util = 100.0 * np.mean(np.abs(error_util) <= 0.5)

    pct_1C_total = 100.0 * np.mean(np.abs(error_total) <= 1.0)
    pct_05C_total = 100.0 * np.mean(np.abs(error_total) <= 0.5)

    # =====================================================
    # Esfuerzo de control
    # =====================================================

    cambios_control = int(
        np.sum(np.abs(np.diff(apertura)) > 1e-9)
    )

    esfuerzo_mecanico = float(
        np.sum(np.abs(np.diff(apertura)))
    )

    return {

        "RMS_util": rms_util,
        "RMS_total": rms_total,

        "J_util": J_util,
        "J_total": J_total,

        "ErrorMax_util": error_max_util,
        "ErrorMax_total": error_max_total,

        "TempMin_total": temp_min_total,
        "TempMax_total": temp_max_total,

        "PctDentro1C_util": pct_1C_util,
        "PctDentro05C_util": pct_05C_util,

        "PctDentro1C_total": pct_1C_total,
        "PctDentro05C_total": pct_05C_total,

        "CambiosControl": cambios_control,
        "EsfuerzoMecanico": esfuerzo_mecanico,
    }


# =========================================================
# IMPRESION RESULTADOS
# =========================================================

def imprimir_metricas(metricas):

    print("\n" + "=" * 68)
    print("ANÁLISIS DE RENDIMIENTO DEL CONTROLADOR BANG-BANG")
    print("=" * 68)

    print(f"RMS del error (8-20 h)              : {metricas['RMS_util']:.4f} °C")
    print(f"RMS del error (todo el día)         : {metricas['RMS_total']:.4f} °C")

    print(f"J (métrica TP, 8-20 h)              : {metricas['J_util']:.4f} °C")
    print(f"J (todo el día)                     : {metricas['J_total']:.4f} °C")

    print(f"Error máximo abs. (8-20 h)          : {metricas['ErrorMax_util']:.4f} °C")
    print(f"Error máximo abs. (todo el día)     : {metricas['ErrorMax_total']:.4f} °C")

    print(f"Temperatura mínima (todo el día)    : {metricas['TempMin_total']:.4f} °C")
    print(f"Temperatura máxima (todo el día)    : {metricas['TempMax_total']:.4f} °C")

    print(f"% dentro de ±1.0 °C (8-20 h)        : {metricas['PctDentro1C_util']:.2f} %")
    print(f"% dentro de ±0.5 °C (8-20 h)        : {metricas['PctDentro05C_util']:.2f} %")

    print(f"% dentro de ±1.0 °C (todo el día)   : {metricas['PctDentro1C_total']:.2f} %")
    print(f"% dentro de ±0.5 °C (todo el día)   : {metricas['PctDentro05C_total']:.2f} %")

    print(f"Cambios de control                  : {metricas['CambiosControl']} cambios")
    print(f"Esfuerzo mecánico                   : {metricas['EsfuerzoMecanico']:.4f} %")


# =========================================================
# GRAFICOS
# =========================================================

def graficar_resultado(resultado, V_obj, dia, mes):

    tiempo_h = resultado["tiempo_h"]
    T_ext = resultado["T_ext"]
    T_int = resultado["T_int"]
    apertura = resultado["apertura"]

    x1, x2 = 8, 20

    # =====================================================
    # GRAFICO PRINCIPAL - TEMPERATURAS
    # =====================================================

    plt.figure(figsize=(13, 6))

    plt.plot(
        tiempo_h,
        T_ext,
        '--',
        linewidth=2,
        label='Temperatura exterior'
    )

    plt.plot(
        tiempo_h,
        T_int,
        linewidth=2,
        label='Temperatura interior'
    )

    plt.axhline(
        V_obj,
        color='red',
        linestyle=':',
        linewidth=2,
        label='Temperatura confort'
    )

    plt.axvspan(
        x1,
        x2,
        alpha=0.08,
        label='Intervalo útil 8-20 h'
    )

    plt.title(
        f'Control Bang-Bang - Temperaturas | Día {dia}/{mes}',
        fontsize=14
    )

    plt.xlabel('Tiempo [h]', fontsize=12)
    plt.ylabel('Temperatura [°C]', fontsize=12)

    plt.xlim(0, 24)

    # marcas cada 1 hora
    plt.xticks(np.arange(0, 25, 1))

    plt.grid(True, alpha=0.3)

    plt.legend()
    plt.tight_layout()

    # =====================================================
    # GRAFICO DE APERTURA
    # =====================================================

    plt.figure(figsize=(13, 5))

    plt.step(
        tiempo_h,
        apertura,
        where='post',
        linewidth=2
    )

    plt.axvspan(
        x1,
        x2,
        alpha=0.08
    )

    plt.title(
        f'Acción de control Bang-Bang | Día {dia}/{mes}',
        fontsize=14
    )

    plt.xlabel('Tiempo [h]', fontsize=12)
    plt.ylabel('Apertura ventana [%]', fontsize=12)

    plt.xlim(0, 24)
    plt.ylim(-5, 105)

    # marcas cada 1 hora
    plt.xticks(np.arange(0, 25, 1))

    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    plt.show()


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    temperaturas_exteriores, dia, mes = obtener_serie_exterior()

    resultado = simular_bang_bang(
        temperaturas_exteriores=temperaturas_exteriores,
        V_obj=V_OBJ,
        V_inicial=V_INICIAL,
        R=R,
        Rv_max=RV_MAX,
        C=C,
        dt_s=DT_S
    )

    metricas = calcular_metricas(resultado, V_OBJ)

    imprimir_metricas(metricas)

    if MOSTRAR_GRAFICOS:
        graficar_resultado(resultado, V_OBJ, dia, mes)