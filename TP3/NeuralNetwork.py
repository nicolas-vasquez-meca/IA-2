import numpy as np

class NeuralNetwork:
    def __init__(self):
        self.initialize()

    def initialize(self):
        # ======================== INITIALIZE NETWORK WEIGTHS AND BIASES =============================
        # Fijamos 4 entradas: [distancia_x, alto, ancho, velocidad]
        # 6 neuronas en la capa oculta y 3 salidas correspondientes a las acciones
        self.input_size = 4
        self.hidden_size = 6
        self.output_size = 3
        
        # Inicialización aleatoria uniforme clásica para los pesos y biases
        self.W1 = np.random.uniform(-1.0, 1.0, (self.input_size, self.hidden_size))
        self.b1 = np.random.uniform(-1.0, 1.0, (1, self.hidden_size))
        
        self.W2 = np.random.uniform(-1.0, 1.0, (self.hidden_size, self.output_size))
        self.b2 = np.random.uniform(-1.0, 1.0, (1, self.output_size))
        # ============================================================================================

    def think(self, inputs):
        # ======================== PROCESS INFORMATION SENSED TO ACT =============================
        # Convertimos la lista de entrada en una fila matricial de numpy (1, 4)
        X = np.array(inputs).reshape(1, -1)
        
        # Forward pass: Capa de entrada -> Capa oculta (Activación ReLU)
        Z1 = np.dot(X, self.W1) + self.b1
        A1 = np.maximum(0, Z1)
        
        # Capa oculta -> Capa de salida
        Z2 = np.dot(A1, self.W2) + self.b2
        result = Z2[0] # Extraemos el vector de salida
        # ========================================================================================
        return self.act(result)

    def act(self, output):
        # ======================== USE THE ACTIVATION FUNCTION TO ACT =============================
        # Usamos Softmax para estabilizar la toma de decisiones basada en las salidas más altas
        exp_shifted = np.exp(output - np.max(output))
        probabilities = exp_shifted / np.sum(exp_shifted)
        
        # Elegimos el índice con el valor de probabilidad más alto
        action = np.argmax(probabilities)
        # =========================================================================================
        if (action == 0):
            return "JUMP"
        elif (action == 1):
            return "DUCK"
        elif (action == 2):
            return "RUN"