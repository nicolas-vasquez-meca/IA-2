from entorno.casilla import Casilla

class Camino(Casilla):
    """
    Implementación concreta de una celda transitable en el entorno.
    Representa el espacio libre por donde el agente de IA puede desplazarse.
    """
    
    def __init__(self, x: int, y: int, costo_transito: int = 1):
        """
        Representa un espacio libre en el entorno.
        Cumple con el contrato de la plantilla base permitiendo el paso fluido.
        """
        super().__init__(x, y)
        self._costo_transito = costo_transito

    @property
    def transitable(self) -> bool:
        """Satisface el contrato de la clase base permitiendo el paso del agente."""
        return True

    @property
    def costo(self) -> float:
        """Devuelve el peso algorítmico asignado a esta coordenada."""
        return self._costo_transito