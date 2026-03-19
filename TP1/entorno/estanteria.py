from entorno.casilla import Casilla
from enum import Enum
from typing import List, Tuple

class Direccion(Enum):
    """
    Define las direcciones relativas permitidas utilizando pares de números.
    """
    ARRIBA = (0, -1)
    ABAJO = (0, 1)
    IZQUIERDA = (-1, 0)
    DERECHA = (1, 0)

class ObjetoEspecial(Casilla):
    """
    Representa un elemento interactivo estático en el entorno.
    """
    def __init__(self, x: int, y: int, identificador: int, direcciones: List[Direccion]):
        """
        Recibe las direcciones relativas y calcula las coordenadas exactas de acceso.
        """
        super().__init__(x, y)
        self._identificador = identificador
        self._puntos_acceso: List[Tuple[int, int]] = []

        for direccion in direcciones:
            desplazamiento_x, desplazamiento_y = direccion.value
            coordenada_exacta = (x + desplazamiento_x, y + desplazamiento_y)
            self._puntos_acceso.append(coordenada_exacta)

    @property
    def transitable(self) -> bool:
        return False

    @property
    def costo(self) -> float:
        return float('inf')

    @property
    def puntos_acceso(self) -> List[Tuple[int, int]]:
        return self._puntos_acceso
    
    @property
    def identificador(self) -> int:
        return self._identificador
    
    @identificador.setter
    def identificado(self, nuevo_identificador: int) -> None:
        """
        Permite al Algoritmo Genetico asignar un nuevo producto a esta
        coordenada fisica sin necesidad de destruir el objeto en memoria.
        """
        self._identificador = nuevo_identificador

    def validar_acceso(self, x_agente: int, y_agente: int) -> bool:
        """Verifica si el agente se encuentra en una zona de interacción válida."""
        return (x_agente, y_agente) in self._puntos_acceso


class Estanteria(ObjetoEspecial):
    """
    Variante específica de un objeto especial diseñada para el almacenamiento.
    """
    def __init__(self, x: int, y: int, identificador: int, direcciones: List[Direccion], capacidad_maxima: int):
        """
        Incorpora un límite numérico para la cantidad de elementos que puede contener,
        junto con una lista interna vacía para representar su contenido.
        """
        super().__init__(x, y, identificador, direcciones)
        self._capacidad_maxima = capacidad_maxima
        self._inventario: List[str] = []

    def depositar_articulo(self, articulo: str) -> bool:
        """Almacena un nuevo elemento exclusivamente si existe capacidad disponible."""
        if len(self._inventario) < self._capacidad_maxima:
            self._inventario.append(articulo)
            return True
        return False
        
    def consultar_inventario(self) -> List[str]:
        """Devuelve una copia de la lista de elementos almacenados."""
        return self._inventario.copy()