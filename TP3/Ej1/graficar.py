# graficar.py
import pandas as pd
import matplotlib.pyplot as plt

# Levanta los datos que escupió tu programa en C++
df = pd.read_csv("predicciones.txt")

plt.figure(figsize=(10, 6))
# Dibuja la nube de puntos original en azul
plt.scatter(df['x'], df['y_real'], color='royalblue', alpha=0.5, label='Nube de Puntos (data.txt)')
# Dibuja la curva que aprendió tu red neuronal en rojo
plt.scatter(df['x'], df['y_prediccion'], color='crimson', s=10, label='Tendencia de la Red Neuronal')

plt.title("Regresion Multicapa - Tendencia del Dataset")
plt.xlabel("X")
plt.ylabel("Y")
plt.legend()
plt.grid(True)
plt.show()