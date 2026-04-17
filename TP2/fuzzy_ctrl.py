
import numpy as np
import skfuzzy as fuzy
from skfuzzy import control as ctrl

class fuzzy_ctrl:
    def __init__(self, V_obj, Ve, C, R,):
        self.V_obj = V_obj
        self.Ve = Ve
        self.C = C
        self.R = R

    def set_Obj(self, V_obj):
        self.V_obj = V_obj
    
    def set_Ve(self, Ve):
        self.V_obj = Ve
    
    def apertura(self):
        
        # Variables difusas
        temperatura = ctrl.Antecedent(np.arange(0, 41, 1), 'temperatura')
        humedad = ctrl.Antecedent(np.arange(-10,11,1), 'humedad')
        
        Apertura = ctrl.Consequent(np.arange(0, 101, 1), 'velocidad')

        # Funciones de pertenencia
        temperatura['pp'] = fuzy.trimf(temperatura.universe, [0, 10, 20])

        Apertura['lenta'] = fuzy.trimf(Apertura.universe, [0, 0, 50])
        Apertura['media'] = fuzy.trimf(Apertura.universe, [25, 50, 75])
        Apertura['rapida'] = fuzy.trimf(Apertura.universe, [50, 100, 100])

        # Reglas
        regla1 = ctrl.Rule(temperatura['baja'], Apertura['lenta'])
        regla2 = ctrl.Rule(temperatura['media'], Apertura['media'])
        regla3 = ctrl.Rule(temperatura['alta'], Apertura['rapida'])

        # Sistema
        sistema_ctrl = ctrl.ControlSystem([regla1, regla2, regla3])
        sistema = ctrl.ControlSystemSimulation(sistema_ctrl)

        # Entrada
        sistema.input['temperatura'] = self.Ve

        # Inferencia
        sistema.compute()

        return sistema.output['Salida']