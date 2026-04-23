import numpy as np
import skfuzzy as fuzy
from skfuzzy import control as ctrl


class fuzzy_ctrl:
    def __init__(self, V_obj, Ve, V, estrategia="base", hora=0.0, T_predicha=None):
        self.V_obj = V_obj
        self.Ve = Ve
        self.V = V
        self.estrategia = estrategia
        self.hora_actual = hora
        self.T_predicha = Ve if T_predicha is None else T_predicha

        self.apertura = ctrl.Consequent(np.arange(0, 101, 1), 'apertura')
        self.apertura.defuzzify_method = 'centroid'
        self._configurar_consecuente()

        if self.estrategia == "pronostico":
            self._inicializar_controlador_pronostico()
        else:
            self._inicializar_controlador_base()

    def _configurar_consecuente(self):
        self.apertura['OFF'] = fuzy.trapmf(self.apertura.universe, [0, 0, 0, 50])
        self.apertura['MID'] = fuzy.trimf(self.apertura.universe, [40, 50, 60])
        self.apertura['ON'] = fuzy.trapmf(self.apertura.universe, [50, 100, 100, 100])

    def _inicializar_controlador_base(self):
        self.err = ctrl.Antecedent(np.arange(-20, 20, 1), 'error')
        self.dT = ctrl.Antecedent(np.arange(-20, 20, 1), 'dT')

        self._configurar_membresias_base()

        regla1 = ctrl.Rule(self.dT['pos'] & self.err['pos'], self.apertura['OFF'])
        regla2 = ctrl.Rule(self.dT['neg'] & self.err['neg'], self.apertura['OFF'])
        regla3 = ctrl.Rule(self.dT['pos'] & self.err['neg'], self.apertura['ON'])
        regla4 = ctrl.Rule(self.dT['neg'] & self.err['pos'], self.apertura['ON'])
        regla5 = ctrl.Rule(self.err['Z'], self.apertura['MID'])

        sistema_ctrl = ctrl.ControlSystem([regla1, regla2, regla3, regla4, regla5])
        self.sistema = ctrl.ControlSystemSimulation(sistema_ctrl)

    def _inicializar_controlador_pronostico(self):
        self.z = ctrl.Antecedent(np.arange(-200, 201, 1), 'z')
        self.hora = ctrl.Antecedent(np.arange(0, 24.5, 0.5), 'hora')
        self.t_pred = ctrl.Antecedent(np.arange(-10, 46, 0.5), 'T_predicha')

        self._configurar_membresias_pronostico()

        reglas = [
            # ===== DIA: control normal =====
            ctrl.Rule(self.hora['dia'] & self.z['pos'], self.apertura['OFF']),
            ctrl.Rule(self.hora['dia'] & self.z['Z'],   self.apertura['MID']),
            ctrl.Rule(self.hora['dia'] & self.z['neg'], self.apertura['ON']),

            # ===== NOCHE + pronóstico ALTO: sesgo a abrir =====
            ctrl.Rule(self.hora['noche'] & self.t_pred['alta'] & self.z['pos'], self.apertura['MID']),
            ctrl.Rule(self.hora['noche'] & self.t_pred['alta'] & self.z['Z'],   self.apertura['ON']),
            ctrl.Rule(self.hora['noche'] & self.t_pred['alta'] & self.z['neg'], self.apertura['ON']),

            # NUEVOOOOO
            # ===== NOCHE + pronóstico NEUTRO: control normal =====
            ctrl.Rule(self.hora['noche'] & self.t_pred['normal'] & self.z['pos'], self.apertura['OFF']),
            ctrl.Rule(self.hora['noche'] & self.t_pred['normal'] & self.z['Z'],   self.apertura['MID']),
            ctrl.Rule(self.hora['noche'] & self.t_pred['normal'] & self.z['neg'], self.apertura['ON']),

            # ===== NOCHE + pronóstico BAJO: sesgo a cerrar =====
            ctrl.Rule(self.hora['noche'] & self.t_pred['baja'] & self.z['pos'], self.apertura['OFF']),
            ctrl.Rule(self.hora['noche'] & self.t_pred['baja'] & self.z['Z'],   self.apertura['OFF']),
            ctrl.Rule(self.hora['noche'] & self.t_pred['baja'] & self.z['neg'], self.apertura['MID']),
        ]

        sistema_ctrl = ctrl.ControlSystem(reglas)
        self.sistema = ctrl.ControlSystemSimulation(sistema_ctrl)

    def _configurar_membresias_base(self):
        self.dT['neg'] = fuzy.trapmf(self.dT.universe, [-20, -20, -1, 1])
        self.dT['pos'] = fuzy.trapmf(self.dT.universe, [-1, 1, 20, 20])

        if self.estrategia == "base":
            self.err['neg'] = fuzy.trapmf(self.err.universe, [-20, -20, -1, 0])
            self.err['Z'] = fuzy.trimf(self.err.universe, [-1.5, 0, 1.5])
            self.err['pos'] = fuzy.trapmf(self.err.universe, [0, 1, 20, 20])
        elif self.estrategia == "gaussiana":
            self.err['neg'] = fuzy.gaussmf(self.err.universe, -5, 2)
            self.err['Z'] = fuzy.gaussmf(self.err.universe, 0, 1.5)
            self.err['pos'] = fuzy.gaussmf(self.err.universe, 5, 2)
        elif self.estrategia == "banda_muerta":
            self.err['neg'] = fuzy.trapmf(self.err.universe, [-20, -20, -1.5, -0.5])
            self.err['Z'] = fuzy.trapmf(self.err.universe, [-2, -1, 1, 2])
            self.err['pos'] = fuzy.trapmf(self.err.universe, [0.5, 1.5, 20, 20])
        else:
            raise ValueError(
                f"Estrategia '{self.estrategia}' no válida. Use: 'base', 'gaussiana', 'banda_muerta' o 'pronostico'."
            )

    def _configurar_membresias_pronostico(self):
        self.z['neg'] = fuzy.trapmf(self.z.universe, [-200, -200, -4, 0])
        self.z['Z'] = fuzy.trimf(self.z.universe, [-3, 0, 3])
        self.z['pos'] = fuzy.trapmf(self.z.universe, [0, 4, 200, 200])

        dia_mf = fuzy.trapmf(self.hora.universe, [6, 8.0, 19, 21])
        noche = []
        for punto in dia_mf:
            noche.append(1-punto)

        self.hora['dia'] = dia_mf
        self.hora['noche'] = noche

        temp_borde = self.V_obj
        self.t_pred['baja'] = fuzy.trapmf(self.t_pred.universe, [-10.0, -10.0, temp_borde - 1.0, temp_borde + 0.5])
        self.t_pred['alta'] = fuzy.trapmf(self.t_pred.universe, [temp_borde - 0.5, temp_borde + 1.0, 45.0, 45.0])

    def graficar_membresias(self):
        import matplotlib.pyplot as plt

        variables = []
        if self.estrategia == "pronostico":
            variables = [
                (self.z, "Variable: Z = (V - Vobj)(Ve - V)"),
                (self.hora, "Variable: Hora"),
                (self.t_pred, "Variable: Temperatura Predicha"),
                (self.apertura, "Variable: Apertura de Ventana"),
            ]
        else:
            variables = [
                (self.err, f"Variable: Error (Estrategia: {self.estrategia.capitalize()})"),
                (self.dT, "Variable: Diferencial de Temperatura (dT)"),
                (self.apertura, "Variable: Apertura de Ventana"),
            ]

        for variable, titulo in variables:
            variable.view()
            plt.title(titulo)
        plt.show()

    def set_Obj(self, V_obj):
        self.V_obj = V_obj
        if self.estrategia == "pronostico":
            self._inicializar_controlador_pronostico()

    def set_Ve(self, Ve):
        self.Ve = Ve

    def set_V(self, V):
        self.V = V

    def set_hora(self, hora):
        self.hora_actual = hora

    def set_T_predicha(self, T_predicha):
        self.T_predicha = T_predicha

    def _resetear_simulador(self):
        self.sistema.reset()

    def control(self) -> float:
        self._resetear_simulador()

        if self.estrategia == "pronostico":
            z_val = (self.V - self.V_obj) * (self.Ve - self.V)
            self.sistema.input['z'] = z_val
            self.sistema.input['hora'] = self.hora_actual
            self.sistema.input['T_predicha'] = self.T_predicha
        else:
            self.sistema.input['error'] = self.V - self.V_obj
            self.sistema.input['dT'] = self.Ve - self.V

        self.sistema.compute()
        return self.sistema.output['apertura']
