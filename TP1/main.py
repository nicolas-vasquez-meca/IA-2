# main.py

import pygame
import sys
from Agentes.Agente import Agente
from entorno.casilla import Casilla
from entorno.camino import Camino
from entorno.pared import Pared
from entorno.estanteria import Estanteria, Direccion
from entorno.mapa import Mapa
from visualizacion.renderizador import RenderizadorPygame
from Ejercicio_2_Entorno_DInámico.Controlador_Trafico_Nuevo import ControladorTrafico

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

    # 1. Instanciación del modelo espacial
    mapa_generado = inicializar_simulacion()

    # 2. Inicialización del motor gráfico
    motor_grafico = RenderizadorPygame(mapa_generado, tamano_celda=40)
    clock = pygame.time.Clock()

    # 3. Creación del agente
    agente = Agente(mapa_generado)

    X_i = 1
    Y_i = 6
    agente.set_Inicio(X_i,Y_i)
    motor_grafico.establecer_color_casilla(X_i, Y_i, (255, 0, 0))
    agente.set_objetivo(9, 9)

    # -------------------------------
    # VARIABLES DE OBSERVACIÓN
    # -------------------------------

    frontera_anterior = set()
    posicion_anterior = (agente.x, agente.y)

    # -------------------------------
    # LOOP PRINCIPAL
    # -------------------------------

    simulacion_activa = True

    while simulacion_activa:
        
        # Eventos del sistema
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                simulacion_activa = False

        # -------------------------------
        # PASO DEL ALGORITMO
        # -------------------------------

        agente.mover()
        print("costo" ,agente.obtener_costo_camino())
        posicion_actual = (agente.x, agente.y)

        # -------------------------------
        # DETECTAR NODOS NUEVOS EN FRONTERA
        # -------------------------------

        frontera_actual = set(agente.frontera_dict.keys())

        nuevos = frontera_actual - frontera_anterior

        for x, y in nuevos:
            motor_grafico.establecer_color_casilla(x, y, (0, 0, 255))  # azul

        # -------------------------------
        # DETECTAR MOVIMIENTO DEL AGENTE
        # -------------------------------

        if posicion_actual != posicion_anterior:

            motor_grafico.establecer_color_casilla(
                posicion_actual[0],
                posicion_actual[1],
                (255, 255, 0)   # amarillo
            )

        # -------------------------------
        # SI SE ENCONTRÓ CAMINO FINAL
        # -------------------------------

        if agente.camino:

            for x, y in agente.camino:
                motor_grafico.establecer_color_casilla(
                    x, y, (255, 0, 0)  # rojo
                )

        # -------------------------------
        # ACTUALIZAR HISTORIA
        # -------------------------------

        frontera_anterior = frontera_actual
        posicion_anterior = posicion_actual

        # -------------------------------
        # RENDER
        # -------------------------------

        motor_grafico.actualizar()
        clock.tick(5)

    pygame.quit()
    sys.exit()

def ejecutar_simulacion_grafica_Ej2() -> None:

    import pygame
    import sys

    # 1. Mapa
    mapa_generado = inicializar_simulacion()

    # 2. Motor gráfico
    motor_grafico = RenderizadorPygame(mapa_generado, tamano_celda=40)
    clock = pygame.time.Clock()

    # 3. Crear agentes
    agente1 = Agente(mapa_generado)
    agente2 = Agente(mapa_generado)

    # POSICIONES INICIALES
    agente1.set_Inicio(1, 6)
    agente1.set_objetivo(9, 9)

    agente2.set_Inicio(13, 6)
    agente2.set_objetivo(5, 9)

    # 4. Controlador de tráfico
    controlador = ControladorTrafico([agente1, agente2])

    # -------------------------------
    # LOOP PRINCIPAL
    # -------------------------------

    simulacion_activa = True
    paused = False
    simulaciones: int = 1 # 3 en total

    while simulacion_activa:

        # -------------------------------
        # EVENTOS
        # -------------------------------
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                simulacion_activa = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    paused = not paused

        # POSICIONES INICIALES
        if (controlador.paso >= len(controlador.agentes[0].camino) + 2
            and controlador.paso >= len(controlador.agentes[1].camino) + 2
            and controlador.paso != 0):
            
            simulaciones += 1 

            motor_grafico.limpiar_colores_dinamicos()
            controlador.paso = 0
            controlador.llego_A = False
            controlador.llego_B = False

            controlador.agentes[0].camino = []
            controlador.agentes[0].visitados = {}
            controlador.agentes[0].frontera_heap = []
            controlador.agentes[0].frontera_dict = {}

            controlador.agentes[1].camino = []
            controlador.agentes[1].visitados = {}
            controlador.agentes[1].frontera_heap = []
            controlador.agentes[1].frontera_dict = {}

            if simulaciones == 2:
                print("Caso nuevo!!")
                controlador.agentes[0].set_Inicio(1, 6)
                controlador.agentes[0].set_objetivo(6, 9)

                controlador.agentes[1].set_Inicio(5, 3)
                controlador.agentes[1].set_objetivo(6, 10)

            elif simulaciones == 3:
                print("Caso nuevo!!")
                controlador.agentes[0].set_Inicio(1, 6)
                controlador.agentes[0].set_objetivo(5, 10)

                controlador.agentes[1].set_Inicio(5, 2)
                controlador.agentes[1].set_objetivo(5, 9)
            
            else:
                break

        # -------------------------------
        # STEP DINÁMICO
        # -----------------------------

        if not paused:
            controlador.Step()

        # -------------------------------
        # DIBUJAR CAMINOS (HISTORIAL)
        # -------------------------------
        for i, agente in enumerate(controlador.agentes):

            limite = min(controlador.paso, len(agente.camino))

            for paso in range(limite):

                x, y = agente.camino[paso-1]

                if i == 0:
                    color = (255, 165, 0)  # 🟠 naranja
                else:
                    color = (100, 200, 255)  # 🔵 celeste

                motor_grafico.establecer_color_casilla(x, y, color)

        # -------------------------------
        # DIBUJAR POSICIÓN ACTUAL
        # -------------------------------
        for i, agente in enumerate(controlador.agentes):

            if controlador.paso < len(agente.camino):
                x, y = agente.camino[controlador.paso-1]
            else:
                x, y = agente.camino[-1]

            if i == 0:
                color = (255, 0, 0)  # 🔴 rojo
            else:
                color = (0, 0, 255)  # 🔵 azul

            motor_grafico.establecer_color_casilla(x, y, color)

        # -------------------------------
        # RENDER
        # -------------------------------
        motor_grafico.actualizar()
        clock.tick(2)  # velocidad de la simulación

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # Punto de entrada estricto del script

    if sys.argv[1] == "1":
        ejecutar_simulacion_grafica()

    elif sys.argv[1] == "2":
        ejecutar_simulacion_grafica_Ej2()