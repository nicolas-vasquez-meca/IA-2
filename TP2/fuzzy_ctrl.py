import numpy as np
import skfuzzy as fuzy
from skfuzzy import control as ctrl

class fuzzy_ctrl:
    def __init__(self, V_obj, Ve):
        self.V_obj = V_obj
        self.Ve = Ve

    def set_Obj(self, V_obj):
        self.V_obj = V_obj
    
    def set_Ve(self, Ve):
        self.V_obj = Ve
    
    def apertura(self):
        
        # Variables difusas
        temperatura = ctrl.Antecedent(np.arange(-10, 41, 1), 'temperatura')
        humedad = ctrl.Antecedent(np.arange(35,81,1), 'humedad')
        
        climatizacion = ctrl.Consequent(np.arange(0, 101, 1), 'climatizacion')

        # Funciones de pertenencia
        temperatura['PP'] = fuzy.trimf(temperatura.universe, [0, 10, 20])
        temperatura['Z'] = fuzy.trimf(temperatura.universe, [-10, 0, 10])

        humedad['M'] = fuzy.trimf(humedad.universe, [35, 50, 65])
        humedad['A'] = fuzy.trimf(humedad.universe, [50, 65, 80])

        climatizacion['PP'] = fuzy.trimf(climatizacion.universe, [0, 10, 20])
        climatizacion['Z'] = fuzy.trimf(climatizacion.universe, [-10, 0, 10])

        # Reglas
        regla1 = ctrl.Rule(temperatura['PP'] & humedad['A'], climatizacion["PP"])
        regla2 = ctrl.Rule(temperatura['Z'] & humedad['M'], climatizacion["Z"])

        # Sistema
        sistema_ctrl = ctrl.ControlSystem([regla1, regla2])
        sistema = ctrl.ControlSystemSimulation(sistema_ctrl)

        # Entrada
        sistema.input['temperatura'] = 7
        sistema.input['humedad'] = 60

        # Inferencia
        sistema.compute()

        return sistema.output['climatizacion']