import matplotlib.pyplot as plt
from typing import List

class VisualizadorTemperatura:
    """
    Clase dedicada a la representación visual de series temporales de temperatura.
    Recibe vectores de datos y genera los gráficos correspondientes.
    """
    
    def __init__(self, estilo: str = 'default'):
        """
        Inicializa el visualizador. Permite inyectar un estilo visual de matplotlib.
        """
        plt.style.use(estilo)

    def graficar_dia(self, temperaturas: List[float], titulo: str = "Variación Térmica Diaria",
                     hora_amanecer: float = 6.5, hora_atardecer: float = 19.5) -> None:
        """
        Grafica un vector de temperaturas a lo largo de 24 horas.
        Incluye sombreado para diferenciar las horas de dia y de noche.
        """
        cantidad_puntos = len(temperaturas)
        if cantidad_puntos <= 1:
            raise ValueError("Se necesitan al menos 2 puntos para graficar una curva diaria.")
            
        # Distribuimos los puntos a lo largo de 24 horas
        horas = [i * 24.0 / (cantidad_puntos - 1) for i in range(cantidad_puntos)]
        
        plt.figure(figsize=(10, 5))
        
        # --- 1. Pintamos los fondos (Día y Noche) ---
        # Noche (Madrugada: de 0h hasta el amanecer)
        plt.axvspan(0, hora_amanecer, color='midnightblue', alpha=0.15, label='Noche')
        
        # Día (Desde el amanecer hasta el atardecer)
        plt.axvspan(hora_amanecer, hora_atardecer, color='gold', alpha=0.15, label='Día')
        
        # Noche (Anochecer: desde el atardecer hasta las 24h)
        # Omitimos el 'label' aquí para que la palabra "Noche" no aparezca duplicada en la leyenda
        plt.axvspan(hora_atardecer, 24, color='midnightblue', alpha=0.15)

        # --- 2. Graficamos la curva térmica ---
        # La dibujamos DESPUÉS de los fondos para que la línea quede por encima y no se opaque
        plt.plot(horas, temperaturas, color='darkorange', linewidth=2.5, label='Temperatura')
        
        plt.title(titulo)
        plt.xlabel("Hora del Día (0-24)")
        plt.ylabel("Temperatura (°C)")
        plt.grid(True, linestyle='--', alpha=0.6)
        
        # Reubicamos la leyenda para que no tape la curva
        plt.legend(loc='upper left') 
        
        plt.xlim(0, 24)
        plt.tight_layout()
        plt.show()

    def graficar_mes(self, temperaturas: List[float], dias_en_mes: int, titulo: str = "Evolución Mensual") -> None:
        """Grafica un vector de temperaturas a lo largo de un mes."""
        cantidad_puntos = len(temperaturas)
        if cantidad_puntos <= 1:
            raise ValueError("Datos insuficientes para graficar el mes.")
            
        # Distribuimos los puntos a lo largo de la cantidad de días del mes
        dias_eje_x = [i * dias_en_mes / (cantidad_puntos - 1) for i in range(cantidad_puntos)]
        
        plt.figure(figsize=(12, 5))
        plt.plot(dias_eje_x, temperaturas, color='coral', linewidth=1.5)
        plt.title(titulo)
        plt.xlabel(f"Días del Mes (1-{dias_en_mes})")
        plt.ylabel("Temperatura (°C)")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xlim(0, dias_en_mes)
        plt.tight_layout()
        plt.show()

    def graficar_anio(self, temperaturas: List[float], temp_media: float = None, titulo: str = "Evolución Anual") -> None:
        """Grafica un vector de temperaturas a lo largo de los 365 días del año."""
        cantidad_puntos = len(temperaturas)
        if cantidad_puntos <= 1:
            raise ValueError("Datos insuficientes para graficar el año.")
            
        # Distribuimos los puntos a lo largo de 365 días
        dias_eje_x = [i * 365.0 / (cantidad_puntos - 1) for i in range(cantidad_puntos)]
        
        plt.figure(figsize=(14, 6))
        plt.plot(dias_eje_x, temperaturas, color='crimson', linewidth=0.5, alpha=0.8)
        
        # Si se provee la temperatura media, la añadimos como referencia visual
        if temp_media is not None:
            plt.axhline(y=temp_media, color='black', linestyle='--', label=f'Media Anual ({temp_media}°C)')
            plt.legend()

        # Lineas divisorias de estaciones
        estaciones = [
            (80, "Otoño", 'darkorange'),
            (172, "Invierno", 'steelblue'),
            (264, "Primavera", 'forestgreen'),
            (355, "Verano", 'firebrick')
        ]

        # Altura dinámica para colocar el texto de las estaciones cerca del borde superior
        altura_texto = max(temperaturas) - (max(temperaturas) - min(temperaturas)) * 0.05
        
        for dia, nombre, color in estaciones:
            # Trazamos la línea vertical
            plt.axvline(x=dia, color=color, linestyle='-.', alpha=0.8, linewidth=1.5)
            # Colocamos el nombre de la estación ligeramente a la derecha de la línea
            plt.text(dia + 3, altura_texto, nombre, color=color, 
                     fontsize=10, fontweight='bold', alpha=0.9)
            
        plt.title(titulo)
        plt.xlabel("Día del Año (1 - 365)")
        plt.ylabel("Temperatura (°C)")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc='upper right')
        plt.xlim(0, 365)
        plt.tight_layout()
        plt.show()