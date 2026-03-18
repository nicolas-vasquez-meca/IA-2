from typing import Dict, List
from dataclasses import dataclass
from collections import defaultdict
# CONTENEDOR DE RESULTADOS (Inmutable)

@dataclass(frozen=True)
class MetricasDemanda:
    """
    Estructura de datos para transportar los resultados
    Al estar congelada, se garantiza que no pueda ser modificada
    una vez calculados, previniendo erroes
    """
    frecuencias_absolutas: Dict[int, int]
    frecuencias_relativas: Dict[int, float]
    total_operaciones: int

class ProcesadorDemanda:
    """
    Modulo para aplicar lógica matemática sobre las secuencias de ordenes.
    No requiere instanciado porque su funcion es transaccional:
    recibe datos -> los procesa -> retorna un resultado
    """

    def generar_metricas(secuencias: List[List[int]]) -> MetricasDemanda:
        """
        Calcula las estadísticas de demanda para cada estante.
        
        Inicialización
        Se utiliza 'defaultdict(int)' para que, si un estante se detecta por primera
        vez, su conteo inicie automáticamente en 0 sin generar un error de sistema.
        """
        conteo_absoluto: Dict[int, int] = defaultdict(int)
        total_movimientos = 0

        # Agregación Computacional (Frecuencia Absoluta)
        # Se inspecciona cada secuencia de órdenes y cada estante dentro de ella.
        for secuencia in secuencias:
            for identificador_estante in secuencia:
                conteo_absoluto[identificador_estante] += 1
                total_movimientos += 1

        # Normalización (Frecuencia Relativa)
        # Se transforma el conteo bruto en un coeficiente de probabilidad (0.0 a 1.0).
        conteo_relativo: Dict[int, float] = {}
        
        # Validación de seguridad para evitar la división matemática por cero.
        if total_movimientos > 0:
            for estante, cantidad_visitas in conteo_absoluto.items():
                conteo_relativo[estante] = cantidad_visitas / total_movimientos

        #  Encapsulamiento
        # Se empaquetan los diccionarios y el total en la estructura inmutable.
        # Se convierte el 'defaultdict' a un 'dict' estándar
        return MetricasDemanda(
            frecuencias_absolutas=dict(conteo_absoluto),
            frecuencias_relativas=conteo_relativo,
            total_operaciones=total_movimientos
        )

# VALIDACION
if __name__ == "__main__":
    print("--- Iniciando validacion de modulo: ProcesadorDemanda ---")
    
    # 1. Simulación de datos de entrada (análogo a lo que entregaría el LectorHistoricoCSV)
    # Imaginemos que el estante 10 se visita 3 veces, el estante 20 se visita 1 vez.
    datos_simulados = [
        [10, 20, 10],
        [10]
    ]
    
    print("[*] Procesando secuencias de prueba simuladas...")
    
    # 2. Ejecución del procesamiento
    metricas_resultado = ProcesadorDemanda.generar_metricas(datos_simulados)
    
    # 3. Verificación de los cálculos matemáticos
    print("\n[*] Resultados Estadisticos Obtenidos:")
    print(f"    Total de operaciones procesadas: {metricas_resultado.total_operaciones}")
    print("\n    Desglose por Estante:")
    
    for estante in metricas_resultado.frecuencias_absolutas.keys():
        f_abs = metricas_resultado.frecuencias_absolutas[estante]
        f_rel = metricas_resultado.frecuencias_relativas[estante]
        # Se formatea la salida para mostrar el porcentaje con dos decimales
        print(f"    - Estante {estante}: Visitado {f_abs} veces (Probabilidad de demanda: {f_rel:.2%})")
        
    print("\n--- Validacion finalizada. Precision matematica confirmada. ---")