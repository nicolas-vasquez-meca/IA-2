import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class FuzzyCtrl:
    def __init__(self, temperatura_val, humedad_val):
        self.temperatura_val = temperatura_val
        self.humedad_val = humedad_val

    def apertura(self):
        # Universos coherentes con NG, NP, Z, PP, PG
        temperatura = ctrl.Antecedent(np.arange(-10, 41, 1), 'temperatura')
        humedad = ctrl.Antecedent(np.arange(35, 81, 1), 'humedad')
        climatizacion = ctrl.Consequent(np.arange(-20, 21, 1), 'climatizacion')
        climatizacion.defuzzify_method = 'mom'
        # Entradas
        temperatura['Z']  = fuzz.trimf(temperatura.universe, [-10, 0, 10])
        temperatura['PP'] = fuzz.trimf(temperatura.universe, [0, 10, 20])

        humedad['M'] = fuzz.trimf(humedad.universe, [35, 50, 65])
        humedad['A'] = fuzz.trimf(humedad.universe, [50, 65, 80])

        # Salidas
        climatizacion['Z']  = fuzz.trimf(climatizacion.universe, [-10, 0, 10])
        climatizacion['PP'] = fuzz.trimf(climatizacion.universe, [0, 10, 20])

        # Reglas del ejemplo
        
        regla1 = ctrl.Rule(temperatura['PP'] & humedad['A'], climatizacion['PP'])
        regla2 = ctrl.Rule(temperatura['Z'] & humedad['M'], climatizacion['Z'])

        sistema_ctrl = ctrl.ControlSystem([regla1, regla2])
        sistema = ctrl.ControlSystemSimulation(sistema_ctrl)

        sistema.input['temperatura'] = self.temperatura_val
        sistema.input['humedad'] = self.humedad_val

        sistema.compute()
        return sistema.output['climatizacion']


if __name__ == "__main__":
    c = FuzzyCtrl(7, 60)
    print(c.apertura())