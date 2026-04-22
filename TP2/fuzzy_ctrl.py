import numpy as np
import skfuzzy as fuzy
from skfuzzy import control as ctrl

class fuzzy_ctrl:
    def __init__(self, V_obj, Ve, V):
        self.V_obj = V_obj
        self.Ve = Ve
        self.V = V

    def set_Obj(self, V_obj):
        self.V_obj = V_obj
    
    def set_Ve(self, Ve):
        self.Ve = Ve

    def set_V(self, V):
        self.V = V
    
    def control(self) -> float: 
        
        # Variables difusas
        err = ctrl.Antecedent(np.arange(-20, 20, 1), 'error') # V(t) - V0
        dT = ctrl.Antecedent(np.arange(-20, 20, 1), 'dT') # Ve - V(t) 

        apertura = ctrl.Consequent(np.arange(0, 101, 1), 'apertura')
        apertura.defuzzify_method = 'centroid'

        err['neg']  = fuzy.trapmf(err.universe, [-20, -20, -5, 3])
        err['pos']  = fuzy.trapmf(err.universe, [-3, 5, 20, 20])

        dT['neg'] = fuzy.trapmf(dT.universe, [-20, -20, -5, 3])
        dT['pos'] = fuzy.trapmf(dT.universe, [-3, 5, 20, 20])

        apertura['ON'] = fuzy.trapmf(apertura.universe, [45, 50, 50, 100])
        apertura['OFF'] = fuzy.trapmf(apertura.universe, [0, 45, 45, 50])
        
        # Reglas
        regla1 = ctrl.Rule(dT['pos'] & err['pos'], apertura["OFF"])
        regla2 = ctrl.Rule(dT['neg'] & err['neg'], apertura["OFF"])
        regla3 = ctrl.Rule(dT['pos'] & err['neg'], apertura["ON"])
        regla4 = ctrl.Rule(dT['neg'] & err['pos'], apertura["ON"])

        # Sistema
        sistema_ctrl = ctrl.ControlSystem([regla1, regla2, regla3, regla4])
        sistema = ctrl.ControlSystemSimulation(sistema_ctrl)

        # Entrada
        Err = (self.V - self.V_obj)
        Delta_T = (self.Ve - self.V)
        sistema.input['error'] = Err
        sistema.input['dT'] = Delta_T

        # Inferencia
        sistema.compute()
        """
        if (Err*Delta_T >= 0):
            return 0
        else:
            return 100
        """
        return sistema.output['apertura']