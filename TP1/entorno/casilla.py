from abc import ABC, abstractmethod

class Casilla(ABC):
    """
    Plantilla fundamental para cualquier espacio dentro del entorno simulado.
    Obliga a las clases derivadas a definir su propio comportamiento físico.
    """
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        return self._x
    
    @property
    def y(self) -> int:
        return self._y

    # Metodos Abstractos
    @property
    @abstractmethod
    def transitable(self) -> bool:
        pass

    @property
    @abstractmethod
    def costo(self) -> float:
        pass