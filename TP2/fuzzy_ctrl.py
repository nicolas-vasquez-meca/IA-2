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
        self.V_obj = Ve

    def set_V(self, V):
        self.V = V
    
    def control(self) -> float: 
        
        # Variables difusas
        err = ctrl.Antecedent(np.arange(-20, 20, 1), 'error') # V(t) - V0
        dT = ctrl.Antecedent(np.arange(-20, 20, 1), 'dt') # Ve - V(t) 

        apertura = ctrl.Consequent(np.arange(0, 101, 1), 'apertura')
        apertura.defuzzify_method = 'mom'
        
        # Funciones de pertenencia
        err['pos'] = fuzy.trimf(err.universe, [-5, 5, 5])
        err['neg'] = fuzy.trimf(err.universe, [-5, -5, 5])

        dT['pos'] = fuzy.trimf(dT.universe, [-5, 5, 5])
        dT['neg'] = fuzy.trimf(dT.universe, [-5, -5, 5])

        apertura['ON'] = fuzy.trimf(apertura.universe, [45, 50, 50])
        apertura['OFF'] = fuzy.trimf(apertura.universe, [45, 45, 50])
        
        # Reglas
        regla1 = ctrl.Rule(dT['pos'] & err['pos'], apertura["OFF"])
        regla2 = ctrl.Rule(dT['neg'] & err['neg'], apertura["OFF"])
        regla3 = ctrl.Rule(dT['pos'] & err['neg'], apertura["ON"])
        regla4 = ctrl.Rule(dT['neg'] & err['pos'], apertura["ON"])

        # Sistema
        sistema_ctrl = ctrl.ControlSystem([regla1, regla2, regla3, regla4])
        sistema = ctrl.ControlSystemSimulation(sistema_ctrl)

        # Entrada
        sistema.input['err'] = (self.V - self.V_obj)
        sistema.input['dT'] = (self.Ve - self.V)

        # Inferencia
        sistema.compute()

        return sistema.output['apertura']