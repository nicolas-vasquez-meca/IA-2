import numpy as np
import skfuzzy as fuzy
from skfuzzy import control as ctrl


class fuzzy_ctrl_pronostico:
    def __init__(self, V_obj, Ve, V, hora, V_pred):
        self.V_obj = V_obj
        self.Ve = Ve
        self.V = V
        self.hora = hora
        self.V_pred = V_pred

    def control(self) -> float: 
        # --- NUEVOS ANTECEDENTES ---
        err = ctrl.Antecedent(np.arange(-20, 20, 1), 'error')
        dT = ctrl.Antecedent(np.arange(-20, 20, 1), 'dT')
        hora = ctrl.Antecedent(np.arange(0, 25, 1), 'hora')
        t_pred = ctrl.Antecedent(np.arange(0, 41, 1), 't_pred') # Temp futura

        apertura = ctrl.Consequent(np.arange(0, 101, 1), 'apertura')
        
        # --- FUNCIONES DE PERTENENCIA ---
        # Hora (Simplificado: Día de 8 a 20, Noche el resto)
        hora['dia'] = fuzy.trapmf(hora.universe, [6, 8, 20, 22])
        hora['noche'] = fuzy.note(hora['dia']) # Lo que no es día es noche

        # Temperatura Predicha
        t_pred['baja'] = fuzy.trimf(t_pred.universe, [0, 0, 25])
        t_pred['alta'] = fuzy.trimf(t_pred.universe, [20, 40, 40])

        # (Mantienes tus funciones de err y dT, pero sugiero trapecios para mayor suavidad)
        err['neg'] = fuzy.trapmf(err.universe, [-20, -20, -2, 0])
        err['zero'] = fuzy.trimf(err.universe, [-2, 0, 2])
        err['pos'] = fuzy.trapmf(err.universe, [0, 2, 20, 20])

        dT['neg'] = fuzy.trapmf(dT.universe, [-20, -20, -2, 0])
        dT['pos'] = fuzy.trapmf(dT.universe, [0, 2, 20, 20])

        # Apertura (0% es cerrada, 100% es abierta)
        apertura['ABRIR'] = fuzy.trimf(apertura.universe, [0, 0, 50])
        apertura['CENTRO'] = fuzy.trimf(apertura.universe, [25, 50, 75])
        apertura['CERRAR'] = fuzy.trimf(apertura.universe, [50, 100, 100])

        # --- REGLAS BASADAS EN LA CONSIGNA ---
        # Reglas de Día (Siguen la lógica de Lyapunov que ya tenías)
        r1 = ctrl.Rule(hora['dia'] & err['pos'] & dT['pos'], apertura['CERRAR'])
        r2 = ctrl.Rule(hora['dia'] & err['neg'] & dT['neg'], apertura['CERRAR'])
        r3 = ctrl.Rule(hora['dia'] & err['neg'] & dT['pos'], apertura['ABRIR'])
        r4 = ctrl.Rule(hora['dia'] & err['pos'] & dT['neg'], apertura['ABRIR'])

        # Reglas de Noche con Pronóstico (Ejemplo de pre-climatización)
        r5 = ctrl.Rule(hora['noche'] & t_pred['alta'] & dT['neg'], apertura['ABRIR']) 
        # (Si mañana hará calor y hoy afuera está fresco, abro para enfriar la estructura)

        # --- SISTEMA ---
        sistema_ctrl = ctrl.ControlSystem([r1, r2, r3, r4, r5])
        sim = ctrl.ControlSystemSimulation(sistema_ctrl)

        # --- ENTRADAS ---
        sim.input['error'] = self.V - self.V_obj
        sim.input['dT'] = self.Ve - self.V
        sim.input['hora'] = self.hora
        sim.input['t_pred'] = self.V_pred

        sim.compute()
        return sim.output['apertura']