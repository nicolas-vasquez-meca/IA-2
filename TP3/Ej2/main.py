import numpy as np
import matplotlib.pyplot as plt
from keras.datasets import mnist
import tensorflow as tf
from tensorflow import keras

# Cargar el dataset MNIST
(X_train, y_train), (X_test, y_test) = mnist.load_data()

# Mostrar 15 ejemplos aleatorios
r, c = 3, 5
fig = plt.figure(figsize=(2*c, 2*r))
for _r in range(r):
    for _c in range(c):
        ix = np.random.randint(0, len(X_train))
        img = X_train[ix]
        plt.subplot(r, c, _r*c + _c + 1)
        plt.imshow(img, cmap='gray')
        plt.axis("off")
        plt.title(y_train[ix])
plt.tight_layout()
plt.show()


from tensorflow.keras import layers, models
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score

# MNIST viene como imágenes de 28x28 con valores entre 0 y 255

# Normalizamos a rango [0, 1]
X_train_tf = X_train.astype("float32") / 255.0
X_test_tf = X_test.astype("float32") / 255.0

# Agregamos el canal de color: MNIST es escala de grises, entonces canal = 1
# Forma final: (cantidad, alto, ancho, canales)
X_train_tf = X_train_tf.reshape(-1, 28, 28, 1)
X_test_tf = X_test_tf.reshape(-1, 28, 28, 1)

print("X_train_tf:", X_train_tf.shape)
print("X_test_tf:", X_test_tf.shape)
print("y_train:", y_train.shape)
print("y_test:", y_test.shape)



model = models.Sequential([
    layers.Input(shape=(28, 28, 1)),

    # Primera etapa convolucional
    layers.Conv2D(32, kernel_size=(3, 3), activation="relu"),
    layers.MaxPooling2D(pool_size=(2, 2)),

    # Segunda etapa convolucional
    layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),
    layers.MaxPooling2D(pool_size=(2, 2)),

    # Pasamos de imagen/matriz a vector
    layers.Flatten(),

    # Red fully-connected final
    layers.Dense(64, activation="relu"),

    # Capa de salida: 10 neuronas porque hay 10 dígitos: 0,1,2,...,9
    layers.Dense(10, activation="softmax")
])

model.summary()

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

historial = model.fit(
    X_train_tf,
    y_train,
    epochs=5,
    batch_size=64,
    validation_split=0.2
)

plt.figure(figsize=(8, 5))
plt.plot(historial.history["accuracy"], label="Accuracy entrenamiento")
plt.plot(historial.history["val_accuracy"], label="Accuracy validación")
plt.xlabel("Época")
plt.ylabel("Accuracy")
plt.title("Evolución de la exactitud")
plt.grid(True)
plt.legend()
plt.show()