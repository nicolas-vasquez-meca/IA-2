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

        secuencias = []
        try:
            with open(self.ruta_archivo, mode='r', encoding='utf-8') as archivo:
                lector_csv = csv.reader(archivo)
                for fila in lector_csv:
                    # Se descartan filas vacías resultantes de saltos de línea anómalos
                    if fila:
                        # Transformación de tipo y limpieza de espacios en blanco
                        secuencia_entera = [int(identificador.strip()) for identificador in fila if identificador.strip()]
                        if secuencia_entera:
                            secuencias.append(secuencia_entera)
        
        except FileNotFoundError:
            print(f"[ERROR CRÍTICO DE I/O] El archivo '{self.ruta_archivo}' no fue localizado en el sistema.")
            raise
        except ValueError as error_valor:
            print(f"[ERROR DE TIPADO] Se detectó un valor no numérico en la secuencia de órdenes: {error_valor}")
            raise
            
        return secuencias
    

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
            print(f"    Secuencia {indice + 1}: {secuencia} | Tipo de dato interno: {type(secuencia[0]).__name__}")
            
        # 4. Limpieza del entorno de prueba
        os.remove(archivo_prueba)
        print(f"\n[*] Limpieza completada: Archivo '{archivo_prueba}' eliminado.")
        print("--- Validacion finalizada sin errores. Modulo listo para integracion. ---")
        
    except Exception as e:
        print(f"\n[FALLO EN VALIDACION] La prueba aislada fue interrumpida: {e}")