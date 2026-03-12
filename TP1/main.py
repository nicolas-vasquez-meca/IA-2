# main.py

import pygame
import sys
from entorno.casilla import Casilla
from entorno.camino import Camino
from entorno.pared import Pared
from entorno.estanteria import Estanteria, Direccion
from entorno.mapa import Mapa
from visualizacion.renderizador import RenderizadorPygame

def construir_bloque_estanterias(entorno: Mapa, x_origen: int, y_origen: int, id_inicial: int) -> None:
    """
    Función factoría que automatiza la creación de un bloque de 2x4 estanterías.
    Calcula dinámicamente las coordenadas absolutas, los identificadores secuenciales
    y asigna las reglas de acceso perimetral según la columna.
    """

    # Iteración vertical (4 filas de estanterías)
    for fila in range(4):
        # Iteración horizontal (2 columnas de estanterías)
        for columna in range(2):
            
            # Cálculo de coordenadas espaciales absolutas
            x_actual = x_origen + columna
            y_actual = y_origen + fila
            
            # Cálculo matemático del identificador secuencial
            # Ejemplo para el primer bloque (id_inicial=1):
            # Fila 0, Col 0: 1 + 0 + 0 = 1
            # Fila 0, Col 1: 1 + 0 + 1 = 2
            # Fila 1, Col 0: 1 + 2 + 0 = 3
            id_actual = id_inicial + (fila * 2) + columna
            
            # Asignación asimétrica de accesibilidad
            # Si es la columna 0 (izquierda), el acceso es estrictamente por la izquierda.
            # Si es la columna 1 (derecha), el acceso es estrictamente por la derecha.
            if columna == 0:
                direcciones_acceso = [Direccion.IZQUIERDA]
            else:
                direcciones_acceso = [Direccion.DERECHA]
                
            # Instanciación e inserción en el gestor espacial
            nueva_estanteria = Estanteria(
                x=x_actual,
                y=y_actual,
                identificador=id_actual,
                direcciones=direcciones_acceso,
                capacidad_maxima=10
            )
            entorno.agregar_elemento(nueva_estanteria)

def inicializar_simulacion() -> 'Mapa':
    """
    Función constructora del modelo de datos espacial.
    Diseñada de forma modular para permitir la personalización absoluta del entorno.
    """
    
    # --- CONFIGURACIÓN DEL GESTOR ESPACIAL ---
    ancho_terreno = 15
    largo_terreno = 13
    entorno_simulacion = Mapa(ancho_terreno, largo_terreno)

    # --- CONSTRUCCIÓN DE OBSTÁCULOS ESTÁTICOS (PAREDES) ---
    # Generación del perímetro de contención infranqueable.
    for x in range(ancho_terreno):
        for y in range(largo_terreno):
            if (x == 0 or x == ancho_terreno - 1 or y == 0 or y == largo_terreno - 1):
                entorno_simulacion.agregar_elemento(Pared(x, y))
                
    #debug: Inserción de obstáculos internos personalizados.
    #entorno_simulacion.agregar_elemento(Pared(4, 4))


    # --- CONSTRUCCIÓN DE ENTIDADES INTERACTIVAS (ESTANTERÍAS) ---
    # Fila Superior de Bloques (y = 2)
    construir_bloque_estanterias(entorno_simulacion, x_origen=3, y_origen=2, id_inicial=1)
    construir_bloque_estanterias(entorno_simulacion, x_origen=7, y_origen=2, id_inicial=9)
    construir_bloque_estanterias(entorno_simulacion, x_origen=11, y_origen=2, id_inicial=17)
    
    # Fila Inferior de Bloques (y = 8)
    construir_bloque_estanterias(entorno_simulacion, x_origen=3, y_origen=7, id_inicial=25)
    construir_bloque_estanterias(entorno_simulacion, x_origen=7, y_origen=7, id_inicial=33)
    construir_bloque_estanterias(entorno_simulacion, x_origen=11, y_origen=7, id_inicial=41)

    #estanteria_1 = Estanteria(
    #    x=3,
    #    y=2,
    #    identificador=1,
    #    direcciones=[Direccion.IZQUIERDA],
    #    capacidad_maxima=8
    #)
    #entorno_simulacion.agregar_elemento(estanteria_1)

    # --- TERRENO TRANSITABLE (CAMINOS) ---
    # Todo espacio no ocupado previamente por una Pared o Estantería será un Camino.
    entorno_simulacion.rellenar_espacios_vacios(
        lambda x_vacio, y_vacio: Camino(x_vacio, y_vacio)
    )
    
    return entorno_simulacion

def ejecutar_simulacion_grafica() -> None:
    """
    Controlador principal del ciclo de vida de la aplicación.
    Conecta el modelo de datos matemáticos con el motor de renderizado gráfico.
    """
    
    # Instanciación del modelo espacial base
    mapa_generado = inicializar_simulacion()
    
    # Inicialización del motor gráfico con una escala de 40 píxeles por celda
    motor_grafico = RenderizadorPygame(mapa_generado, tamano_celda=40)
    
    # Prueba de la funcionalidad de coloreado dinámico en tiempo de ejecución
    # Esto simula cómo el futuro algoritmo A* marcará su ruta óptima o 
    # cómo se visualizará la posición en tiempo real del agente de IA.
    #color_ruta_prueba = (150, 255, 150) # Tonalidad verde claro (RGB)
    #motor_grafico.establecer_color_casilla(1, 1, color_ruta_prueba)


    # 4. Bucle infinito de eventos del sistema operativo y renderizado
    simulacion_activa = True
    while simulacion_activa:
        # Procesamiento de interacciones del usuario (ej. presionar la 'X' de la ventana)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                simulacion_activa = False
                
        # Refresco del cuadro visual en la pantalla
        motor_grafico.actualizar()
        
    # Finalización ordenada del subsistema gráfico
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # Punto de entrada estricto del script
    ejecutar_simulacion_grafica()