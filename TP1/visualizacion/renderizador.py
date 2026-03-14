import pygame
import sys
from typing import Tuple, Dict

from entorno.casilla import Casilla
from entorno.camino import Camino
from entorno.estanteria import Estanteria
from entorno.pared import Pared
from entorno.mapa import Mapa


class RenderizadorPygame:

    def __init__(self, mapa_simulacion: 'Mapa', tamano_celda: int = 40):

        """
        Dedicado a la representación gráfica del entorno.
        Mantiene un estado visual independiente para permitir la modificación de colores
        en tiempo de ejecución (ej. visualización de algoritmos de búsqueda).
        """
        # Definición de paleta de colores (Formato RGB)
        self.COLOR_FONDO = (200, 200, 200)       # Gris para el fondo base
        self.COLOR_GRILLA = (220, 220, 220)      # Gris claro para las líneas de la cuadrícula
        self.COLOR_PARED = (0, 0, 0)             # Negro absoluto para obstáculos físicos
        self.COLOR_CAMINO = (255, 255, 255)      # Blanco puro para rutas transitables
        self.COLOR_TEXTO = (0, 0, 0)             # Negro para identificadores numéricos
        self.COLOR_INDICADOR = (255, 0, 0)       # Rojo para los triángulos de acceso
        self.COLOR_FRONTERA = (0, 0, 255)
        self.COLOR_VISITADO = (255, 255, 0)
        self.COLOR_CAMINO_FINAL = (255, 0, 0)
        """
        Inicializa el subsistema gráfico.
        Calcula dinámicamente las dimensiones de la ventana basándose en 
        las proporciones del mapa matemático y el tamaño deseado por celda.
        """
        self._mapa = mapa_simulacion
        self._tamano_celda = tamano_celda
        
        # Dimensiones totales de la ventana generada
        self._ancho_pantalla = self._mapa.ancho * self._tamano_celda
        self._alto_pantalla = self._mapa.largo * self._tamano_celda
        
        # Inicialización de la biblioteca PyGame
        pygame.init()
        self._pantalla = pygame.display.set_mode((self._ancho_pantalla, self._alto_pantalla))
        pygame.display.set_caption("Simulación de Agente de IA y Path Planning")
        
        # Configuración de tipografía para los números de las estanterías
        self._fuente = pygame.font.SysFont(None, int(self._tamano_celda * 0.6))
        
        # Diccionario para almacenar colores temporales asignados durante la ejecución
        # Estructura: {(coordenada_x, coordenada_y): (R, G, B)}
        self._colores_dinamicos: Dict[Tuple[int, int], Tuple[int, int, int]] = {}

    def establecer_color_casilla(self, x: int, y: int, color_rgb: Tuple[int, int, int]) -> None:
        """
        Registra un color específico para una coordenada. 
        Este método será invocado por el controlador del agente 
        para resaltar su progreso sin alterar el modelo de datos original.
        """
        self._colores_dinamicos[(x, y)] = color_rgb

    def limpiar_colores_dinamicos(self) -> None:
        """Restaura todos los caminos a su color original."""
        self._colores_dinamicos.clear()

    def _dibujar_triangulo_acceso(self, x: int, y: int, orientacion: str) -> None:
        """
        Dibuja un polígono (triángulo) en uno de los bordes de la celda 
        para indicar visualmente que dicha cara es un punto de acceso interactivo.
        """
        # Se calculan las coordenadas en píxeles de la celda actual
        px = x * self._tamano_celda
        py = y * self._tamano_celda
        mitad = self._tamano_celda // 2
        margen = self._tamano_celda // 5

        # Se definen los tres vértices del triángulo dependiendo del borde
        if orientacion == "ARRIBA":
            puntos = [(px + mitad, py), (px + margen, py + margen), (px + self._tamano_celda - margen, py + margen)]
        elif orientacion == "ABAJO":
            puntos = [(px + mitad, py + self._tamano_celda), (px + margen, py + self._tamano_celda - margen), (px + self._tamano_celda - margen, py + self._tamano_celda - margen)]
        elif orientacion == "IZQUIERDA":
            puntos = [(px, py + mitad), (px + margen, py + margen), (px + margen, py + self._tamano_celda - margen)]
        elif orientacion == "DERECHA":
            puntos = [(px + self._tamano_celda, py + mitad), (px + self._tamano_celda - margen, py + margen), (px + self._tamano_celda - margen, py + self._tamano_celda - margen)]
        
        pygame.draw.polygon(self._pantalla, self.COLOR_INDICADOR, puntos)

    def actualizar(self) -> None:
        """
        Método principal de renderizado. 
        """
        self._pantalla.fill(self.COLOR_FONDO)

        # Recorrido bidimensional de la matriz espacial
        for y in range(self._mapa.largo):
            for x in range(self._mapa.ancho):
                entidad = self._mapa.obtener_casilla(x, y)
                
                # Definición del rectángulo gráfico para la celda actual
                rectangulo = pygame.Rect(x * self._tamano_celda, y * self._tamano_celda, self._tamano_celda, self._tamano_celda)

                # Si es una pared, se rellena de color negro
                if type(entidad).__name__ == "Pared":
                    pygame.draw.rect(self._pantalla, self.COLOR_PARED, rectangulo)

                # Si es un camino, se aplica el color dinámico si existe, o el blanco por defecto
                elif type(entidad).__name__ == "Camino":
                    color_actual = self._colores_dinamicos.get((x, y), self.COLOR_CAMINO)
                    pygame.draw.rect(self._pantalla, color_actual, rectangulo)

                # Si es una estantería, requiere renderizado compuesto (Fondo, Borde, Texto, Indicadores)
                elif type(entidad).__name__ == "Estanteria":
                    # 1. Fondo blanco
                    pygame.draw.rect(self._pantalla, self.COLOR_CAMINO, rectangulo)

                    # 2. Borde negro de 3 píxeles de grosor
                    pygame.draw.rect(self._pantalla, self.COLOR_PARED, rectangulo, 3)
                    
                    # 3. Renderizado del número de identificación en el centro
                    superficie_texto = self._fuente.render(str(entidad.identificador), True, self.COLOR_TEXTO)
                    rectangulo_texto = superficie_texto.get_rect(center=rectangulo.center)
                    self._pantalla.blit(superficie_texto, rectangulo_texto)
                    
                    # 4. Evaluación lógica de accesos mediante el método validado de la entidad
                    # Se verifica si la posición adyacente garantiza acceso
                    if entidad.validar_acceso(x, y - 1): self._dibujar_triangulo_acceso(x, y, "ARRIBA")
                    if entidad.validar_acceso(x, y + 1): self._dibujar_triangulo_acceso(x, y, "ABAJO")
                    if entidad.validar_acceso(x - 1, y): self._dibujar_triangulo_acceso(x, y, "IZQUIERDA")
                    if entidad.validar_acceso(x + 1, y): self._dibujar_triangulo_acceso(x, y, "DERECHA")

                # Independientemente del contenido, se dibuja la grilla perimetral gris claro
                pygame.draw.rect(self._pantalla, self.COLOR_GRILLA, rectangulo, 1)

        # Intercambio de buffers de video para mostrar el cuadro renderizado
        pygame.display.flip()