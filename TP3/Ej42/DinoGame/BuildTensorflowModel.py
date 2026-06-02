import subprocess
try:
    import tensorflow as tf
except ImportError as err:
    subprocess.check_call(['pip', 'install', 'tensorflow'])
    subprocess.check_call(['pip', 'install', 'Pillow'])
    import tensorflow as tf

from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

import os
import random
import json
import shutil

# Rutas de las carpetas
source_dir = "images"

train_dir = source_dir + "/train/"
test_dir = source_dir + "/test/"

# Clases
classes = ["up", "down", "right"]

# Limpiar train/test previos antes de regenerar
if os.path.exists(train_dir):
    shutil.rmtree(train_dir)
if os.path.exists(test_dir):
    shutil.rmtree(test_dir)

# Crear directorios
os.makedirs(train_dir, exist_ok=True)
os.makedirs(test_dir, exist_ok=True)

for c in classes:
    os.makedirs(train_dir + c, exist_ok=True)
    os.makedirs(test_dir + c, exist_ok=True)

# Proporción entrenamiento/test
train_ratio = 0.8

# ==========================
# PARÁMETROS DEL MODELO
# ==========================

batch_size = 32

# target_size = (height, width)
image_size = (96, 192)

# Tensorflow usa:
# (alto, ancho, canales)
input_shape = (96, 192, 1)

# ==========================
# CARGA Y PREPROCESADO
# ==========================

def load_and_preprocess_image(file_path, target_size):
    img = load_img(
        file_path,
        color_mode='grayscale',
        target_size=target_size
    )

    img_array = img_to_array(img)
    return img_array

def _image_files_in(dirpath):
    return [
        f for f in os.listdir(dirpath)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))
    ]

# Balanceo de clases
min_images = min(
    len(_image_files_in(os.path.join(source_dir, c)))
    for c in classes
)

print(f"Usando {min_images} imágenes por clase")

# ==========================
# GENERAR TRAIN / TEST
# ==========================

for class_name in classes:

    source_class_dir = os.path.join(source_dir, class_name)

    images = _image_files_in(source_class_dir)

    random.shuffle(images)

    # Balancear
    images = images[:min_images]

    random.shuffle(images)

    num_train_images = int(len(images) * train_ratio)

    # TRAIN
    for img_name in images[:num_train_images]:

        src_img_path = os.path.join(source_class_dir, img_name)

        dest_train_path = os.path.join(
            train_dir + class_name,
            img_name
        )

        img_array = load_and_preprocess_image(
            src_img_path,
            image_size
        )

        tf.keras.preprocessing.image.save_img(
            dest_train_path,
            img_array
        )

    # TEST
    for img_name in images[num_train_images:]:

        src_img_path = os.path.join(source_class_dir, img_name)

        dest_test_path = os.path.join(
            test_dir + class_name,
            img_name
        )

        img_array = load_and_preprocess_image(
            src_img_path,
            image_size
        )

        tf.keras.preprocessing.image.save_img(
            dest_test_path,
            img_array
        )

# ==========================
# DATA GENERATORS
# ==========================

train_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=image_size,
    batch_size=batch_size,
    class_mode='categorical',
    color_mode='grayscale',
    classes=classes,
    shuffle=True
)

validation_datagen = ImageDataGenerator(rescale=1./255)

validation_generator = validation_datagen.flow_from_directory(
    test_dir,
    target_size=image_size,
    batch_size=batch_size,
    class_mode='categorical',
    color_mode='grayscale',
    classes=classes,
    shuffle=False
)

# Guardar mapping clases
with open("class_indices.json", "w") as f:
    json.dump(train_generator.class_indices, f)

print("Class indices:")
print(train_generator.class_indices)

# ==========================
# MODELO
# ==========================

model = tf.keras.models.Sequential([

    tf.keras.layers.Input(shape=input_shape),

    tf.keras.layers.Conv2D(
        32,
        (3, 3),
        activation='relu'
    ),

    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Conv2D(
        64,
        (3, 3),
        activation='relu'
    ),

    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Conv2D(
        128,
        (3, 3),
        activation='relu'
    ),

    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Flatten(),

    tf.keras.layers.Dense(
        128,
        activation='relu'
    ),

    tf.keras.layers.Dropout(0.5),

    tf.keras.layers.Dense(
        len(classes),
        activation='softmax'
    )
])

# ==========================
# COMPILAR
# ==========================

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# ==========================
# CALLBACKS
# ==========================

checkpoint = ModelCheckpoint(
    "tensorflow_nn.keras",
    monitor="val_loss",
    save_best_only=True
)

earlystop = EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True
)

# ==========================
# ENTRENAR
# ==========================

model.fit(
    train_generator,
    epochs=20,
    validation_data=validation_generator,
    callbacks=[checkpoint, earlystop]
)

print("Modelo guardado como tensorflow_nn.keras")