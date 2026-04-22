import numpy as np
import skfuzzy as fuzy
from skfuzzy import control as ctrl

class fuzzy_ctrl:
    def __init__(self, V_obj, Ve, V, estrategia="base"):
        self.V_obj = V_obj
        self.Ve = Ve
        self.V = V
        self.estrategia = estrategia

        # Inicializacion del Sistema Difuso
        self.err = ctrl.Antecedent(np.arange(-20, 20, 1), 'error') # V(t) - V0
        self.dT = ctrl.Antecedent(np.arange(-20, 20, 1), 'dT') # Ve - V(t) 
        self.apertura = ctrl.Consequent(np.arange(0, 101, 1), 'apertura')
        
        self.apertura.defuzzify_method = 'centroid' # Metodo de defusificacion

        # Configurar funciones de pertenencia segun estrategia elegida
        self._configurar_membresias()
        
        # Consecuente con rango completo
        self.apertura['OFF'] = fuzy.trimf(self.apertura.universe, [0, 0, 50])
        self.apertura['MID'] = fuzy.trimf(self.apertura.universe, [0, 50, 100])
        self.apertura['ON'] = fuzy.trimf(self.apertura.universe, [50, 100, 100])
        
        # Reglas de Inferencia
        regla1 = ctrl.Rule(self.dT['pos'] & self.err['pos'], self.apertura["OFF"])
        regla2 = ctrl.Rule(self.dT['neg'] & self.err['neg'], self.apertura["OFF"])
        regla3 = ctrl.Rule(self.dT['pos'] & self.err['neg'], self.apertura["ON"])
        regla4 = ctrl.Rule(self.dT['neg'] & self.err['pos'], self.apertura["ON"])
        regla5 = ctrl.Rule(self.err['Z'], self.apertura['MID'])

        # Inicializar Motor de Simulacion
        sistema_ctrl = ctrl.ControlSystem([regla1, regla2, regla3, regla4, regla5])
        self.sistema = ctrl.ControlSystemSimulation(sistema_ctrl)


    def _configurar_membresias(self):
        """
        Método privado que asigna las formas de las membresías basándose 
        en el parámetro de inicialización 'estrategia'.
        """
        # La variable dT se mantiene estable para todas las pruebas
        self.dT['neg']  = fuzy.trapmf(self.dT.universe, [-20, -20, -1, 1])
        self.dT['pos']  = fuzy.trapmf(self.dT.universe, [-1, 1, 20, 20])
    
        # Selector de Estrategia para la variable Error
        if self.estrategia == "base":
            # Transiciones lineales estándar con centro agudo
            self.err['neg'] = fuzy.trapmf(self.err.universe, [-20, -20, -2, 0])
            self.err['Z']   = fuzy.trimf(self.err.universe, [-2, 0, 2])
            self.err['pos'] = fuzy.trapmf(self.err.universe, [0, 2, 20, 20])

        elif self.estrategia == "gaussiana":
            # Superficie de control ultra-suave
            self.err['neg'] = fuzy.gaussmf(self.err.universe, -5, 2)
            self.err['Z']   = fuzy.gaussmf(self.err.universe, 0, 1.5)
            self.err['pos'] = fuzy.gaussmf(self.err.universe, 5, 2)

        elif self.estrategia == "banda_muerta":
            # Tolerancia al error: El centro es un trapecio con una meseta
            self.err['neg'] = fuzy.trapmf(self.err.universe, [-20, -20, -1.5, -0.5])
            self.err['Z']   = fuzy.trapmf(self.err.universe, [-1.5, -0.5, 0.5, 1.5])
            self.err['pos'] = fuzy.trapmf(self.err.universe, [0.5, 1.5, 20, 20])
            
        else:
            raise ValueError(f"Estrategia '{self.estrategia}' no válida. Use: 'base', 'gaussiana' o 'banda_muerta'.")

    def set_Obj(self, V_obj):
        self.V_obj = V_obj
    
    def set_Ve(self, Ve):
        self.Ve = Ve

    def set_V(self, V):
        self.V = V
    
    def control(self) -> float: 
        # Logica de Control
        self.sistema.input['error'] = (self.V - self.V_obj)
        self.sistema.input['dT'] = (self.Ve - self.V)

        # Inferencia
        self.sistema.compute()
        """
        if (Err*Delta_T >= 0):
            return 0
        else:
            return 100
        """
        return self.sistema.output['apertura']