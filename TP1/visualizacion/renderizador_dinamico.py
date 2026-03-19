import pygame
import sys
from typing import Tuple, List, Optional, Set, Dict

from entorno.casilla import Casilla
from entorno.camino import Camino
from entorno.estanteria import Estanteria
from entorno.pared import Pared
from entorno.mapa import Mapa

class RenderizadorDinamico:
    """
    Motor de reproducción visual genérico.
    Diseñado para animar trayectorias de agentes sin acoplarse a un algoritmo específico
    (compatible con A*, Recocido Simulado, o secuencias manuales).
    """

    def __init__(self, mapa_simulacion: Mapa, tamano_celda: int = 40, alto_panel: int = 80):
        self._mapa = mapa_simulacion
        self._tamano_celda = tamano_celda
        self._alto_panel = alto_panel
        
        # Dimensiones totales de la ventana generada
        self._ancho_pantalla = self._mapa.ancho * self._tamano_celda
        self._alto_pantalla = (self._mapa.largo * self._tamano_celda) + self._alto_panel
        
        # Paleta de colores (Formato RGB)
        self.C_FONDO = (235, 235, 235)
        self.C_GRILLA = (210, 210, 210)
        self.C_PARED = (30, 30, 30)
        self.C_CAMINO = (255, 255, 255)
        self.C_TEXTO = (20, 20, 20)
        self.C_INDICADOR = (240, 80, 80)
        
        # Colores de la simulación dinámica
        self.C_AGENTE = (0, 120, 255)         # Azul visible para el agente robótico
        self.C_RUTA_PENDIENTE = (210, 235, 255)
        self.C_RUTA_HECHA = (150, 200, 245)
        self.C_ESTANTE_OBJETIVO = (255, 214, 102)  # Amarillo
        self.C_ESTANTE_LISTO = (180, 230, 180)     # Verde claro
        self.C_PANEL = (245, 245, 245)

        # Inicialización del subsistema gráfico
        pygame.init()
        self._pantalla = pygame.display.set_mode((self._ancho_pantalla, self._alto_pantalla))
        pygame.display.set_caption("Motor de Visualización Dinámica de Rutas")
        
        # Tipografías
        self._fuente_estantes = pygame.font.SysFont(None, int(self._tamano_celda * 0.6))
        self._fuente_panel = pygame.font.SysFont(None, 24)
        self._reloj = pygame.time.Clock()

    def _dibujar_triangulo_acceso(self, x: int, y: int, orientacion: str) -> None:
        """Renderiza los polígonos que indican los frentes de interacción de los estantes."""
        px = x * self._tamano_celda
        py = y * self._tamano_celda
        mitad = self._tamano_celda // 2
        margen = self._tamano_celda // 5

        if orientacion == "ARRIBA":
            puntos = [(px + mitad, py), (px + margen, py + margen), (px + self._tamano_celda - margen, py + margen)]
        elif orientacion == "ABAJO":
            puntos = [(px + mitad, py + self._tamano_celda), (px + margen, py + self._tamano_celda - margen), (px + self._tamano_celda - margen, py + self._tamano_celda - margen)]
        elif orientacion == "IZQUIERDA":
            puntos = [(px, py + mitad), (px + margen, py + margen), (px + margen, py + self._tamano_celda - margen)]
        elif orientacion == "DERECHA":
            puntos = [(px + self._tamano_celda, py + mitad), (px + self._tamano_celda - margen, py + margen), (px + self._tamano_celda - margen, py + self._tamano_celda - margen)]
        
        pygame.draw.polygon(self._pantalla, self.C_INDICADOR, puntos)

    def _dibujar_cuadro(
        self, 
        pos_agente: Tuple[int, int], 
        ruta_hecha: Set[Tuple[int, int]], 
        ruta_pendiente: Set[Tuple[int, int]],
        estantes_objetivo: Set[int],
        estantes_completados: Set[int],
        texto_estado: str
    ) -> None:
        """Renderiza un único fotograma (frame) basado en el estado actual inyectado."""
        self._pantalla.fill(self.C_FONDO)

        # 1. Renderizado de la Cuadrícula Espacial
        for y in range(self._mapa.largo):
            for x in range(self._mapa.ancho):
                entidad = self._mapa.obtener_casilla(x, y)
                rectangulo = pygame.Rect(x * self._tamano_celda, y * self._tamano_celda, self._tamano_celda, self._tamano_celda)

                # Optimización: Se reemplaza la validación de texto (type().__name__) por isinstance
                if isinstance(entidad, Pared):
                    pygame.draw.rect(self._pantalla, self.C_PARED, rectangulo)

                elif isinstance(entidad, Camino):
                    color_camino = self.C_CAMINO
                    if (x, y) in ruta_pendiente: color_camino = self.C_RUTA_PENDIENTE
                    if (x, y) in ruta_hecha: color_camino = self.C_RUTA_HECHA
                    pygame.draw.rect(self._pantalla, color_camino, rectangulo)

                elif isinstance(entidad, Estanteria):
                    color_estante = self.C_CAMINO
                    if entidad.identificador in estantes_objetivo:
                        color_estante = self.C_ESTANTE_LISTO if entidad.identificador in estantes_completados else self.C_ESTANTE_OBJETIVO

                    pygame.draw.rect(self._pantalla, color_estante, rectangulo)
                    pygame.draw.rect(self._pantalla, self.C_PARED, rectangulo, 2)
                    
                    texto = self._fuente_estantes.render(str(entidad.identificador), True, self.C_TEXTO)
                    self._pantalla.blit(texto, texto.get_rect(center=rectangulo.center))
                    
                    if entidad.validar_acceso(x, y - 1): self._dibujar_triangulo_acceso(x, y, "ARRIBA")
                    if entidad.validar_acceso(x, y + 1): self._dibujar_triangulo_acceso(x, y, "ABAJO")
                    if entidad.validar_acceso(x - 1, y): self._dibujar_triangulo_acceso(x, y, "IZQUIERDA")
                    if entidad.validar_acceso(x + 1, y): self._dibujar_triangulo_acceso(x, y, "DERECHA")

                pygame.draw.rect(self._pantalla, self.C_GRILLA, rectangulo, 1)

        # 2. Renderizado del Agente Robótico (Círculo superpuesto)
        centro_x = pos_agente[0] * self._tamano_celda + self._tamano_celda // 2
        centro_y = pos_agente[1] * self._tamano_celda + self._tamano_celda // 2
        radio_agente = int(self._tamano_celda * 0.35)
        pygame.draw.circle(self._pantalla, self.C_AGENTE, (centro_x, centro_y), radio_agente)

        # 3. Renderizado del Panel de Telemetría Inferior
        y_panel = self._mapa.largo * self._tamano_celda
        rect_panel = pygame.Rect(0, y_panel, self._ancho_pantalla, self._alto_panel)
        pygame.draw.rect(self._pantalla, self.C_PANEL, rect_panel)
        pygame.draw.line(self._pantalla, self.C_PARED, (0, y_panel), (self._ancho_pantalla, y_panel), 3)
        
        superficie_texto = self._fuente_panel.render(texto_estado, True, self.C_TEXTO)
        self._pantalla.blit(superficie_texto, (15, y_panel + 30))

        pygame.display.flip()

    def reproducir_trayectoria(
        self, 
        recorrido: List[Tuple[int, int]], 
        ids_orden: List[int],
        fps: int = 10
    ) -> None:
        """
        Orquestador temporal interactivo.
        Permite pausar (ESPACIO) y avanzar/retroceder paso a paso (Flechas).
        """
        if not recorrido:
            print("[ADVERTENCIA] No hay trayectoria para reproducir.")
            return

        indice_actual = 0
        pausado = False
        ejecutando = True
        
        # Mapeo de coordenadas de acceso a IDs de estantes para saber cuándo se recolectan
        accesos_map = {}
        for elemento in self._mapa.elementos:
            if isinstance(elemento, Estanteria):
                for p in elemento.puntos_acceso:
                    accesos_map[p] = elemento.identificador

        estantes_completados = set()

        while ejecutando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        pausado = not pausado
                    elif evento.key == pygame.K_RIGHT and pausado and indice_actual < len(recorrido) - 1:
                        indice_actual += 1
                    elif evento.key == pygame.K_LEFT and pausado and indice_actual > 0:
                        indice_actual -= 1

            if not pausado and indice_actual < len(recorrido) - 1:
                indice_actual += 1
                
            # Actualización del estado lógico
            pos_actual = recorrido[indice_actual]
            
            # Verificación de recolección: si la posición actual es un punto de acceso de una orden
            if pos_actual in accesos_map:
                id_detectado = accesos_map[pos_actual]
                if id_detectado in ids_orden:
                    # Lógica retroactiva: Si avanzamos o retrocedemos manualmente, recalcular completados
                    estantes_completados = set()
                    for pos in recorrido[:indice_actual + 1]:
                        if pos in accesos_map and accesos_map[pos] in ids_orden:
                            estantes_completados.add(accesos_map[pos])

            # Construcción del texto de estado
            estado_str = "[PAUSADO] Use flechas para mover" if pausado else "[REPRODUCIENDO] ESPACIO para pausar"
            progreso_str = f"Paso {indice_actual + 1}/{len(recorrido)} | Recolectados: {len(estantes_completados)}/{len(ids_orden)}"
            texto_panel = f"{estado_str}  ---  {progreso_str}"

            # Inyección de estado al motor de renderizado
            self._dibujar_cuadro(
                pos_agente=pos_actual,
                ruta_hecha=set(recorrido[:indice_actual + 1]),
                ruta_pendiente=set(recorrido[indice_actual + 1:]),
                estantes_objetivo=set(ids_orden),
                estantes_completados=estantes_completados,
                texto_estado=texto_panel
            )

            self._reloj.tick(fps if not pausado else 60)

        pygame.quit()


    def mostrar_mapa_calor(self, frecuencias_absolutas: Dict[int, int]) -> None:
        """
        Renderiza una representación estática del mapa donde la intensidad 
        cromática de cada estantería es directamente proporcional a su demanda histórica.
        """
        self._pantalla.fill(self.C_FONDO)
        
        # 1. Extracción de límites para la normalización matemática
        valores_frecuencia = list(frecuencias_absolutas.values())
        frecuencia_maxima = max(valores_frecuencia) if valores_frecuencia else 1
        frecuencia_minima = min(valores_frecuencia) if valores_frecuencia else 0
        rango_frecuencia = frecuencia_maxima - frecuencia_minima
        if rango_frecuencia == 0:
            rango_frecuencia = 1 # Prevención de división por cero
            
        # 2. Definición del espectro cromático (Gradiente térmico)
        # Color Frío (Baja demanda): Azul claro - RGB(200, 220, 255)
        # Color Caliente (Alta demanda): Rojo oscuro - RGB(220, 20, 20)
        color_frio = (200, 220, 255)
        color_caliente = (220, 20, 20)

        # 3. Renderizado espacial
        for y in range(self._mapa.largo):
            for x in range(self._mapa.ancho):
                entidad = self._mapa.obtener_casilla(x, y)
                rectangulo = pygame.Rect(x * self._tamano_celda, y * self._tamano_celda, self._tamano_celda, self._tamano_celda)

                if isinstance(entidad, Pared):
                    pygame.draw.rect(self._pantalla, self.C_PARED, rectangulo)

                elif isinstance(entidad, Camino):
                    pygame.draw.rect(self._pantalla, self.C_CAMINO, rectangulo)

                elif isinstance(entidad, Estanteria):
                    # Extracción y normalización de la demanda
                    visitas = frecuencias_absolutas.get(entidad.identificador, 0)
                    coeficiente = (visitas - frecuencia_minima) / rango_frecuencia
                    
                    # Interpolación lineal de canales RGB
                    rojo = int(color_frio[0] + (color_caliente[0] - color_frio[0]) * coeficiente)
                    verde = int(color_frio[1] + (color_caliente[1] - color_frio[1]) * coeficiente)
                    azul = int(color_frio[2] + (color_caliente[2] - color_frio[2]) * coeficiente)
                    
                    color_interpolado = (rojo, verde, azul)

                    pygame.draw.rect(self._pantalla, color_interpolado, rectangulo)
                    pygame.draw.rect(self._pantalla, self.C_PARED, rectangulo, 2)
                    
                    # Renderizado del identificador
                    texto = self._fuente_estantes.render(str(entidad.identificador), True, self.C_TEXTO)
                    self._pantalla.blit(texto, texto.get_rect(center=rectangulo.center))
                    
                    # Indicadores de acceso
                    if entidad.validar_acceso(x, y - 1): self._dibujar_triangulo_acceso(x, y, "ARRIBA")
                    if entidad.validar_acceso(x, y + 1): self._dibujar_triangulo_acceso(x, y, "ABAJO")
                    if entidad.validar_acceso(x - 1, y): self._dibujar_triangulo_acceso(x, y, "IZQUIERDA")
                    if entidad.validar_acceso(x + 1, y): self._dibujar_triangulo_acceso(x, y, "DERECHA")

                pygame.draw.rect(self._pantalla, self.C_GRILLA, rectangulo, 1)

        # 4. Renderizado del Panel Inferior
        y_panel = self._mapa.largo * self._tamano_celda
        rect_panel = pygame.Rect(0, y_panel, self._ancho_pantalla, self._alto_panel)
        pygame.draw.rect(self._pantalla, self.C_PANEL, rect_panel)
        pygame.draw.line(self._pantalla, self.C_PARED, (0, y_panel), (self._ancho_pantalla, y_panel), 3)
        
        instrucciones = "[MAPA DE CALOR] Análisis de Agrupamiento. Presione ESPACIO para continuar a la simulación."
        superficie_texto = self._fuente_panel.render(instrucciones, True, self.C_TEXTO)
        self._pantalla.blit(superficie_texto, (15, y_panel + 30))

        pygame.display.flip()

        # 5. Bucle de retención (Pausa el programa hasta que el usuario decida avanzar)
        esperando = True
        while esperando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                    esperando = False