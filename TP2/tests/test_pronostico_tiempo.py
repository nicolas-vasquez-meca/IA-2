import calendar

from pronostico_tiempo import PronosticoTiempo
from visualizador_temperatura import VisualizadorTemperatura

def ejecutar_pruebas():
    print("Iniciando validación del modelo de pronóstico de tiempo...")

    # 1. Instanciamos el modelo con parámetros de un clima de alta amplitud térmica
    modelo = PronosticoTiempo(
        temp_media=20,       # Temperatura media anual
        amp_anual=12.0,        # Diferencia entre la media y el pico del verano
        amp_diaria=7.0,       # Fuerte caída de temperatura en la noche
        dia_pico_verano=15,    # 15 de Enero
        hora_pico_diario=16.0  # El calor máximo se registra a las 16:00 hs
    )

    # Instanciamos el visualizador utilizando un estilo estético de matplotlib
    visualizador = VisualizadorTemperatura(estilo='ggplot')

    # ==========================================
    # PRUEBA 1: Variación de un solo día (Verano)
    # ==========================================
    dia_prueba = 15
    mes_prueba = 1
    puntos_dia = 48  # Muestreo cada media hora para una curva suave
    
    print(f"Generando datos para el día {dia_prueba}/{mes_prueba}...")
    temperaturas_dia = modelo.obtener_temperaturas_dia(dia_prueba, mes_prueba, puntos_dia)
    visualizador.graficar_dia(
        temperaturas=temperaturas_dia, 
        titulo=f"Variación Térmica Diaria - Pleno Verano ({dia_prueba}/{mes_prueba})"
    )

    # ==========================================
    # PRUEBA 2: Variación de un mes entero (Invierno)
    # ==========================================
    mes_invierno = 7
    puntos_por_dia_mes = 24  # Muestreo cada 1 hora
    _, dias_en_mes = calendar.monthrange(2023, mes_invierno)
    
    print(f"Generando datos para el mes {mes_invierno}...")
    temperaturas_mes = []
    for dia in range(1, dias_en_mes + 1):
        temperaturas_mes.extend(
            modelo.obtener_temperaturas_dia(dia, mes_invierno, puntos_por_dia_mes)
        )
        
    visualizador.graficar_mes(
        temperaturas=temperaturas_mes, 
        dias_en_mes=dias_en_mes,
        titulo=f"Evolución Mensual - Pleno Invierno (Mes {mes_invierno})"
    )

    # ==========================================
    # PRUEBA 3: Variación del año completo
    # ==========================================
    puntos_por_dia_anio = 6  # Muestreo cada 4 horas (suficiente para ver la banda sin saturar)
    
    print("Generando datos para el año completo (esto puede tomar un segundo)...")
    temperaturas_anio = []
    
    for mes in range(1, 13):
        _, dias_mes_actual = calendar.monthrange(2023, mes)
        for dia in range(1, dias_mes_actual + 1):
            temperaturas_anio.extend(
                modelo.obtener_temperaturas_dia(dia, mes, puntos_por_dia_anio)
            )
            
    visualizador.graficar_anio(
        temperaturas=temperaturas_anio, 
        temp_media=modelo.temp_media,
        titulo="Envolvente Térmica Anual (Muestreo cada 4 horas)"
    )
    
    print("Pruebas finalizadas con éxito.")

if __name__ == '__main__':
    ejecutar_pruebas()