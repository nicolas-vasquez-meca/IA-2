class BangBangCtrl:
    """
    Controlador bang-bang basado en la consigna:

    Si:
        (v - v0)(ve - v) >= 0
            -> cerrar ventana

    Si:
        (v - v0)(ve - v) < 0
            -> abrir ventana

    Convención de salida:
        apertura = 0   -> ventana cerrada
        apertura = 100 -> ventana abierta
    """

    def __init__(self, V_obj: float, Ve: float, V: float):
        self.V_obj = float(V_obj)
        self.Ve = float(Ve)
        self.V = float(V)

    def set_Obj(self, V_obj: float):
        self.V_obj = float(V_obj)

    def set_Ve(self, Ve: float):
        self.Ve = float(Ve)

    def set_V(self, V: float):
        self.V = float(V)

    def control(self) -> float:
        error = self.V - self.V_obj
        delta_T = self.Ve - self.V

        # Ley bang-bang derivada del análisis por Lyapunov
        if error * delta_T >= 0:
            return 0.0      # cerrar
        return 100.0        # abrir