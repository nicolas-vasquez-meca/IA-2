import sys
import time
from statistics import mean
import numpy as np
from pathlib import Path
from typing import List, Optional
import random
from Agentes.Agente import Agente
from entorno.camino import Camino
from entorno.pared import Pared
from entorno.estanteria import Estanteria, Direccion
from entorno.mapa import Mapa


from AG.procesador_demanda import ProcesadorDemanda
from AG.algoritmo_genetico import AlgoritmoGenetico, ConfiguracionAG
from temple.temple import SimulatedAnnealingPicking
from visualizacion.renderizador_dinamico import RenderizadorDinamico

# CONSTRUCCION DEL ENTORNO
def construir_bloque_estanterias(entorno: Mapa, x_origen: int, y_origen: int, asignacion_ids: List[int]) -> None:
    """
    Construye un bloque de 2x4 estanterías.
    Consume los identificadores de la lista inyectada en lugar de calcularlos matemáticamente,
    permitiendo que el Algoritmo Genético defina qué producto va en qué coordenada.
    """
    indice_asignacion = 0
    for fila in range(4):
        for columna in range(2):
            x_actual = x_origen + columna
            y_actual = y_origen + fila
            
            id_asignado = asignacion_ids[indice_asignacion]
            indice_asignacion += 1
            
            direcciones_acceso = [Direccion.IZQUIERDA] if columna == 0 else [Direccion.DERECHA]
                
            nueva_estanteria = Estanteria(
                x=x_actual,
                y=y_actual,
                identificador=id_asignado,
                direcciones=direcciones_acceso,
                capacidad_maxima=10
            )
            entorno.agregar_elemento(nueva_estanteria)


def inicializar_simulacion(cromosoma_optimo: Optional[List[int]] = None) -> Mapa:
    """
    Inicializa la topología del mapa. Si no recibe un cromosoma (Fase 1), 
    asigna un orden secuencial por defecto del 1 al 48.
    """
    ancho_terreno = 15
    largo_terreno = 13
    entorno_simulacion = Mapa(ancho_terreno, largo_terreno)

    # Construcción de perímetro
    for x in range(ancho_terreno):
        for y in range(largo_terreno):
            if (x == 0 or x == ancho_terreno - 1 or y == 0 or y == largo_terreno - 1):
                entorno_simulacion.agregar_elemento(Pared(x, y))

    # Fallback para extracción topológica inicial
    if cromosoma_optimo is None:
        cromosoma_optimo = list(range(1, 49))

    if len(cromosoma_optimo) != 48:
        raise ValueError("Error de integridad: El cromosoma debe contener exactamente 48 identificadores.")

    # Inyección segmentada de IDs por bloque
    construir_bloque_estanterias(entorno_simulacion, 3, 2, cromosoma_optimo[0:8])
    construir_bloque_estanterias(entorno_simulacion, 7, 2, cromosoma_optimo[8:16])
    construir_bloque_estanterias(entorno_simulacion, 11, 2, cromosoma_optimo[16:24])
    construir_bloque_estanterias(entorno_simulacion, 3, 7, cromosoma_optimo[24:32])
    construir_bloque_estanterias(entorno_simulacion, 7, 7, cromosoma_optimo[32:40])
    construir_bloque_estanterias(entorno_simulacion, 11, 7, cromosoma_optimo[40:48])

    entorno_simulacion.rellenar_espacios_vacios(lambda x, y: Camino(x, y))
    return entorno_simulacion


# HERRAMIENTAS DE PRECALCULO
def calcular_distancia_astar(mapa: Mapa, origen: tuple, destino: tuple) -> float:
    """Calcula el costo real de tránsito entre dos coordenadas usando A*."""
    if origen == destino:
        return 0.0
        
    agente = Agente(mapa)
    agente.set_Inicio(origen[0], origen[1])
    agente.set_objetivo(destino[0], destino[1])
    
    # Límite de seguridad para evitar bucles infinitos en zonas bloqueadas
    limite_pasos = 2000
    pasos = 0
    while not agente.camino and pasos < limite_pasos:
        if agente.mover():
            break
        pasos += 1
        
    if not agente.camino:
        return float('inf')
    return agente.visitados[(agente.x, agente.y)].g

def extraer_matriz_distancias(mapa: Mapa, coord_base: tuple) -> np.ndarray:
    """
    Escanea el mapa y genera una matriz 49x49 con las distancias A*.
    Índice 0 = Estación de Carga. Índices 1-48 = Puntos de acceso de estanterías.
    """
    dimension = 49
    matriz = np.zeros((dimension, dimension), dtype=float)
    
    # Mapeo de nodos: 0 -> Base, 1..48 -> Coordenadas de acceso de cada estantería
    nodos_acceso = {0: coord_base}
    for elemento in mapa.elementos:
        if isinstance(elemento, Estanteria):
            # Se utiliza el primer punto de acceso transitable
            nodos_acceso[elemento.identificador] = elemento.puntos_acceso[0]

    # Cálculo simétrico para reducir el tiempo de procesamiento a la mitad
    for i in range(dimension):
        for j in range(i + 1, dimension):
            distancia = calcular_distancia_astar(mapa, nodos_acceso[i], nodos_acceso[j])
            matriz[i][j] = distancia
            matriz[j][i] = distancia
            
    return matriz


# ORQUESTADOR MAESTRO
def ejecutar_pipeline_completo(n_muestras: int = 10) -> None:
    """Ejecuta la secuencia matemática de diseño, optimización y simulación."""

    coordenada_base = (1, 6)
    ruta_csv = Path(__file__).parent / "ordenes.csv"

    # Cargar todas las ordenes disponibles
    todas_las_ordenes = SimulatedAnnealingPicking.cargar_ordenes_desde_csv(ruta_csv)
    
    # Seleccionar N muestras aleatorias
    if len(todas_las_ordenes) < n_muestras:
        n_muestras = len(todas_las_ordenes)
    muestras_test = random.sample(todas_las_ordenes, n_muestras)

    print(f"\n>>> EJECUTANDO BENCHMARK INICIAL ({n_muestras} ordenes)...")
    mapa_inicial = inicializar_simulacion() # Mapa 1-48
    
    costos_antes = []
    tiempos_sa_antes = []

    print("\n=== ESCENARIO 1: DISPOSICION SECUENCIAL (ANTES) ===")
    mapa_inicial = inicializar_simulacion()

    solver_sa = SimulatedAnnealingPicking(
        mapa=mapa_inicial,
        inicio=coordenada_base,
        max_iteraciones=3000,
        volver_al_origen=True
    )

    for i, orden in enumerate(muestras_test):
        inicio_sa = time.time()
        resultado = solver_sa.resolver(orden)
        fin_sa = time.time()
        
        costos_antes.append(resultado.mejor_costo)
        tiempos_sa_antes.append(fin_sa - inicio_sa)
        print(f"  Orden {i+1}/{n_muestras} procesada.", end="\r")

    print("\n\n>>> EJECUTANDO ALGORITMO GENETICO (Optimizacion de Layout)...")
    matriz_distancias = extraer_matriz_distancias(mapa_inicial, coord_base=coordenada_base)
    matriz_transicion = ProcesadorDemanda.generar_matriz_transicion(todas_las_ordenes)

    # 3.3 Configuración del Optimizador
    config = ConfiguracionAG(
        tamano_poblacion=150,
        tasa_mutacion=0.05,
        tasa_cruce=0.9,
        limite_iteraciones=200,
        tolerancia_convergencia=30,
        tamano_torneo=7
    )
    
    optimizador = AlgoritmoGenetico(
        matriz_transicion=matriz_transicion,
        matriz_distancias=matriz_distancias,
        estantes_ids=list(range(1, 49)),
        coordenadas_ids=list(range(1, 49)),
        coord_base=0,
        configuracion=config
    )
    
    start_ag = time.time()
    optimizador.ejecutar()
    cromosoma_ganador, _, _ = optimizador.evaluacion()
    end_ag = time.time()
    
    tiempo_total_ag = end_ag - start_ag

    # ---------------------------------------------------------
    # FASE 3: BENCHMARK FINAL (Mapa Optimizado)
    # ---------------------------------------------------------
    print(f"\n>>> EJECUTANDO BENCHMARK POST-OPTIMIZACION ({n_muestras} ordenes)...")
    mapa_optimizado = inicializar_simulacion(cromosoma_optimo=cromosoma_ganador)
    
    costos_despues = []
    tiempos_sa_despues = []
    
    solver_sa_opt = SimulatedAnnealingPicking(mapa=mapa_optimizado, inicio=coordenada_base, volver_al_origen=True)

    for i, orden in enumerate(muestras_test):
        inicio_sa = time.time()
        resultado = solver_sa_opt.resolver(orden)
        fin_sa = time.time()
        
        costos_despues.append(resultado.mejor_costo)
        tiempos_sa_despues.append(fin_sa - inicio_sa)
        print(f"  Orden {i+1}/{n_muestras} procesada.", end="\r")

    # ---------------------------------------------------------
    # RESULTADOS Y MÉTRICAS
    # ---------------------------------------------------------
    promedio_antes = mean(costos_antes)
    promedio_despues = mean(costos_despues)
    mejora_porcentual = ((promedio_antes - promedio_despues) / promedio_antes) * 100
    
    tiempo_promedio_sa = mean(tiempos_sa_antes + tiempos_sa_despues)

    print("\n" + "="*50)
    print("RESUMEN DE RESULTADOS")
    print("="*50)
    print(f"Tiempo ejecucion Algoritmo Genetico: {tiempo_total_ag:.4f} seg")
    print(f"Tiempo promedio de ruteo (SA) por orden: {tiempo_promedio_sa:.4f} seg")
    print("-" * 50)
    print(f"Costo promedio ANTES: {promedio_antes:.2f}")
    print(f"Costo promedio DESPUES: {promedio_despues:.2f}")
    print(f"MEJORA PROMEDIO TOTAL: {mejora_porcentual:.2f}%")
    print("="*50)

    # 4. Simulación visual de la última orden procesada para cerrar
    print("\nLanzando visualizacion del mapa optimizado...")
    motor_grafico = RenderizadorDinamico(mapa_simulacion=mapa_optimizado, tamano_celda=45)
    motor_grafico.reproducir_trayectoria(
        recorrido=resultado.recorrido_completo,
        ids_orden=muestras_test[-1],
        fps=15
    )

if __name__ == "__main__":
    # Puedes cambiar el número de muestras aquí rápidamente
    ejecutar_pipeline_completo(n_muestras=20)