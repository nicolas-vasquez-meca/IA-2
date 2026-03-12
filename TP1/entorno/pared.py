from entorno.casilla import Casilla

class Pared(Casilla):
    """
    Representa una barrera física infranqueable.
    Cumple con el contrato de la plantilla base bloqueando el paso.
    """

    def __init__(self, x: int, y: int):
        super().__init__(x, y)

    @property
    def transitable(self) -> bool:
        """Deniega el movimiento a través de esta coordenada."""
        return False

    @property
    def costo(self) -> float:
        """
        Asigna una dificultad matemática infinita.
        Esto descarta la coordenada durante el cálculo de cualquier ruta.
        """
        return int('inf')