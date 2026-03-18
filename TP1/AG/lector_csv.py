import csv
import os
from typing import List

class LectorOrdenesCSV:
    """
    Responsable de la interacción con el sistema de archivos.
    Extrae y transforma secuencias de caracteres en matrices numéricas estructuradas.
    """

    def __init__(self, ruta_archivo: str):
        self.ruta_archivo = ruta_archivo

    def extraer_secuencias(self) -> List[List[int]]:
        """
        Ejecuta la lectura del archivo CSV especificado.

        Retorna: Matriz donde cada sublista representa una secuencia
        cronologica de identificados de estantes.
        """
        with open(self.ruta_archivo, mode='r', encoding='utf-8') as archivo:
            # Se utiliza la división de texto por comas
            return [[int(valor) for valor in linea.split(',')] for linea in archivo if linea.strip()]
    

if __name__ == "__main__":
    print("--- Iniciando validacion de modulo: LectorHistoricoCSV ---")
    
    # Preparación del entorno de prueba (Creación de archivo temporal)
    archivo_prueba = "ordenes_test.csv"
    datos_simulados = [
        "40,26,13,14,29,34,28",
        "32,23,22,36,17",
        "28,1,41,23,38,19,21"
    ]
    
    with open(archivo_prueba, mode='w', encoding='utf-8', newline='') as f:
        for linea in datos_simulados:
            f.write(linea + "\n")
            
    print(f"[*] Archivo de prueba '{archivo_prueba}' generado exitosamente.")

    # 2. Ejecución de la unidad lógica
    try:
        lector = LectorOrdenesCSV(archivo_prueba)
        resultado_matriz = lector.extraer_secuencias()
        
        # 3. Verificacion de resultados
        print("\n[*] Extraccion completada. Verificando estructura de salida:")
        for indice, secuencia in enumerate(resultado_matriz):
            print(f"    Secuencia {indice + 1}: {secuencia}")
            
        # 4. Limpieza del entorno de prueba
        os.remove(archivo_prueba)
        print(f"\n[*] Limpieza completada: Archivo '{archivo_prueba}' eliminado.")
        print("--- Validacion finalizada sin errores. Modulo listo para integracion. ---")
        
    except Exception as e:
        print(f"\n[FALLO EN VALIDACION] La prueba aislada fue interrumpida: {e}")