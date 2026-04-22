import math
from datetime import date
from typing import List

class PronosticoTiempo:
    """
    Modelo simplificado de temperatura
    """
    def __init__(self,
                 temp_media: float = 17.0,
                 amp_anual: float = 8.0,
                 amp_diaria: float = 4.0,
                 dia_pico_verano: int = 15,
                 hora_pico_diario: float = 15.0):
        """
        Inicializa el modelo de pronostico con los parametros climaticos.
        """
        self.temp_media = temp_media
        self.amp_anual = amp_anual
        self.amp_diaria = amp_diaria
        self.dia_pico_verano = dia_pico_verano
        self.hora_pico_diario = hora_pico_diario

    def _fecha_a_dia_anio(self, dia: int, mes: int, ano: int = 2026) -> int:
        """
        Convierte un dia y mes generico al numero de dia en el año (1-365).
        """
        fecha = date(ano, mes, dia)
        return fecha.timetuple().tm_yday
        
    def _calcular_temperatura_exacta(self, dia_anio: float, hora_dia: float) -> float:
        """
        Calcula la temperatura para una dia y hora especifica del dia.
        """
        # Componente anual
        angulo_anual = (2*math.pi / 365) * (dia_anio - self.dia_pico_verano)
        componente_anual = self.amp_anual * math.cos(angulo_anual)

        # Componente diario
        angulo_diaria = (2*math.pi / 24) * (hora_dia - self.hora_pico_diario)
        componente_diaria = self.amp_diaria * math.cos(angulo_diaria)

        return self.temp_media + componente_anual + componente_diaria
        
    def obtener_temperaturas_dia(self, dia: int, mes: int, cantidad_puntos: int) -> float:
        """
        Retorna una lista con la evolucion de la temperatura durante un dia especifico.
        
        Parametros:
            - dia: Dia del mes (1-31).
            - mes: Mes del año (1-12).
            - cantidad_puntos: Cantidad de puntos a tomar durante las 24hs.
        
        Retorna:
            - List[float]: Lista con las temperaturas a lo largo del dia.
        """

        # Validacion de tipos de datos
        if not all(isinstance(arg, int) for arg in (dia, mes, cantidad_puntos)):
            raise TypeError("dia, mes y cantidad_puntos deben ser enteros.")
        
        # Validacion logica de los puntos
        if cantidad_puntos < 1:
            raise ValueError("cantidad_puntos a calcular debe ser al menos 1.")
        
        # Validacion de fecha
        try:
            dia_anio = self._fecha_a_dia_anio(dia, mes)
        except:
            raise ValueError(f"Fecha invalida: el dia {dia} no es valido para el mes {mes}.")
        
        # Calculo de temperaturas
        temperaturas = []

        for i in range(cantidad_puntos):
            # Si solo hay un punto se toma el mediodia
            if cantidad_puntos == 1:
                hora_actual = 12.0
            # Si hay mas distribuimos de 0 a 24hs
            else:
                hora_actual = (i * 24.0 / cantidad_puntos - 1)

            dia_fraccional = dia_anio + (hora_actual / 24.0)

            temp = self._calcular_temperatura_exacta(dia_fraccional, hora_actual)
            temperaturas.append(round(temp, 2))

        return temperaturas




