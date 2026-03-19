from typing import List, Optional, Callable, Iterable
from entorno.casilla import Casilla


class Mapa:
    """
    Estructura organizativa que consolida el espacio del entorno.
    Su arquitectura delega la creación masiva de terreno a una función externa,
    simplificando radicalmente la disposición inicial de los elementos.
    """
    
    def __init__(self, ancho: int, largo: int):
        """
        Establece las dimensiones máximas del terreno.
        Inicializa una estructura bidimensional vacía (compuesta por valores nulos).
        """
        self._ancho = ancho
        self._largo = largo
        
        # Se genera una cuadrícula donde cada celda está inicialmente vacía (None)
        self._cuadricula: List[List[Optional['Casilla']]] = [
            [None for _ in range(largo)] for _ in range(ancho)
        ]

    def agregar_elemento(self, elemento: 'Casilla') -> None:
        """
        Posiciona una entidad específica en el tablero.
        Permite registrar únicamente los obstáculos, reduciendo el esfuerzo de diseño.
        
        Verifica estrictamente que las coordenadas del elemento no excedan los límites definidos.
        """
        x = elemento.x
        y = elemento.y
        
        if 0 <= x < self._ancho and 0 <= y < self._largo:
            self._cuadricula[x][y] = elemento
        else:
            raise ValueError(f"Imposible posicionar. Las coordenadas ({x}, {y}) exceden los límites del terreno.")

    def rellenar_espacios_vacios(self, generador_defecto: Callable[[int, int], 'Casilla']) -> None:
        """
        Automatiza la creación del terreno transitable.
        Recorre la totalidad de la matriz y, si encuentra una coordenada sin asignar,
        utiliza la función externa proveída para crear un espacio base (ej. Camino).
        """
        for x in range(self._ancho):
            for y in range(self._largo):
                if self._cuadricula[x][y] is None:
                    # Inyección de dependencia: se llama a la función externa para crear la casilla
                    self._cuadricula[x][y] = generador_defecto(x, y)

    def obtener_casilla(self, x: int, y: int) -> Optional['Casilla']:
        """
        Provee acceso seguro a la información física de una coordenada específica.
        Es el método principal que utilizará el algoritmo de búsqueda de rutas (ej. A*)
        para evaluar el entorno.
        """
        if 0 <= x < self._ancho and 0 <= y < self._largo:
            return self._cuadricula[x][y]
        return None

    @property
    def ancho(self) -> int:
        """Permite consultar el límite horizontal del mapa."""
        return self._ancho

    @property
    def largo(self) -> int:
        """Permite consultar el límite vertical del mapa."""
        return self._largo
    
    @property
    def elementos(self) -> Iterable['Casilla']:
        """
        Iterador global del mapa.
        Recorre la cuadrícula bidimensional y retorna secuencialmente todas 
        las entidades físicas válidas (Paredes, Caminos, Estanterías).
        
        Implementado como un generador (yield) para no duplicar el uso 
        de la memoria RAM construyendo listas temporales.
        """
        for x in range(self._ancho):
            for y in range(self._largo):
                entidad = self._cuadricula[x][y]
                if entidad is not None:
                    yield entidad