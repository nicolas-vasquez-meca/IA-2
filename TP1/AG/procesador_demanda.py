from typing import Dict, List, Tuple
from itertools import chain
from collections import Counter
from lector_csv import LectorOrdenesCSV
import os

class ProcesadorDemanda:
    """
    Modulo para aplicar lógica matemática sobre las secuencias de ordenes.
    recibe datos -> los procesa -> retorna un resultado
    """

    def generar_metricas(secuencias: List[List[int]]) -> Tuple[Dict[int, int], Dict[int, float], int]:
        """
        Calcula las estadísticas de demanda para cada estante.

        Retorna una tupla con: (Frec. Absolutas, Frec. Relativas, Total Operaciones)
        """

        # NOTA:
        # chain.from_iterable una todas las secuencias en una sola linea
        # Counter cuenta cada aparicion
        frecuencias_absolutas = Counter(chain.from_iterable(secuencias))

        total_operaciones = sum(frecuencias_absolutas.values())

        # Frecuencia relativa en una sola linea
        frecuencias_relativas = {
            estante: cantidad / total_operaciones
            for estante, cantidad in frecuencias_absolutas.items()
        }

        return dict(frecuencias_absolutas), frecuencias_relativas, total_operaciones


if __name__ == "__main__":
    print("--- Iniciando validacion ---")
    
    # 1. Creación de entorno efímero
    archivo_prueba = "ordenes_optimizadas.csv"
    with open(archivo_prueba, mode='w', encoding='utf-8') as f:
        f.write("40,26,13\n32,23\n40,32,13\n")
    
    # 2. Ejecución lineal de los módulos
    lector = LectorOrdenesCSV(archivo_prueba)
    datos_crudos = lector.extraer_secuencias()
    
    abs_freq, rel_freq, total = ProcesadorDemanda.generar_metricas(datos_crudos)
    
    # 3. Verificación de resultados
    print(f"[*] Secuencias extraidas: {datos_crudos}")
    print(f"[*] Operaciones totales procesadas: {total}")
    for estante in abs_freq.keys():
        print(f"    - Estante {estante}: {abs_freq[estante]} visitas | Probabilidad: {rel_freq[estante]:.2f}")
    
    # 4. Limpieza
    os.remove(archivo_prueba)
    print("--- Validacion finalizada. ---")