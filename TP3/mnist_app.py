import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageOps
import numpy as np

class MNISTApp:
    def __init__(self, root, trained_model, canvas_size=280):
        self.root = root
        self.rf_model = trained_model
        self.canvas_size = canvas_size
        
        self.root.title("Clasificador Interactivo de Dígitos")
        
        # 1. Lienzo para dibujar (Cambiado a fondo NEGRO)
        self.canvas = tk.Canvas(root, width=canvas_size, height=canvas_size, bg="black", cursor="cross")
        self.canvas.grid(row=0, column=0, padx=10, pady=10)
        
        # 2. Lienzo off-screen optimizado (Cambiado a fondo NEGRO)
        self.image = Image.new("L", (canvas_size, canvas_size), "black")
        
        import PIL.ImageDraw
        self.pil_draw = PIL.ImageDraw.Draw(self.image)
        
        # 3. Separar los eventos correctamente
        self.canvas.bind('<Button-1>', self.start_draw)         
        self.canvas.bind('<B1-Motion>', self.draw_line)         
        self.canvas.bind('<ButtonRelease-1>', self.stop_draw)   
        
        self.old_x, self.old_y = None, None
        
        # 4. Panel de control
        control_frame = ttk.Frame(root)
        control_frame.grid(row=1, column=0, pady=10)
        
        ttk.Button(control_frame, text="Borrar", command=self.clear_canvas).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Predecir", command=self.predict_digit).grid(row=0, column=1, padx=5)
        
        self.result_label = ttk.Label(root, text="Dígito Predicho: __", font=("Helvetica", 20, "bold"))
        self.result_label.grid(row=2, column=0, pady=20)

    def start_draw(self, event):
        self.old_x = event.x
        self.old_y = event.y

    def draw_line(self, event):
        if self.old_x and self.old_y:
            # Dibujo en Tkinter (Cambiado a trazo BLANCO)
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y, 
                                    width=15, fill="white", capstyle='round', smooth=True)
            
            # Dibujo en la memoria de PIL (Cambiado a trazo BLANCO)
            self.pil_draw.line([self.old_x, self.old_y, event.x, event.y], 
                               width=15, fill="white", joint='round')
            
        self.old_x = event.x
        self.old_y = event.y

    def stop_draw(self, event):
        self.old_x, self.old_y = None, None
        
    def clear_canvas(self):
        self.canvas.delete("all")
        # Reiniciar imagen con fondo NEGRO
        self.image = Image.new("L", (self.canvas_size, self.canvas_size), "black")
        import PIL.ImageDraw
        self.pil_draw = PIL.ImageDraw.Draw(self.image)
        self.result_label.config(text="Dígito Predicho: __")
        
    def predict_digit(self):
        # 1. Preprocesamiento: Ya NO invertimos, porque la imagen ya es blanca sobre negro
        mnist_image = self.image.copy()
        
        # Redimensionar: De 280x280 a 28x28 píxeles
        mnist_image = mnist_image.resize((28, 28), Image.Resampling.LANCZOS)
        
        # Convertir a array NumPy
        img_array = np.array(mnist_image)
        
        # Normalizar: Fundamental si entrenaste tu modelo con datos divididos por 255.0
        img_norm = img_array.astype('float32') / 255.0  
        
        # Aplanar: De (28, 28) a (1, 784)
        img_flat = img_norm.reshape(1, 784)
        
        # 2. Predicción
        if self.rf_model:
            pred_digit = self.rf_model.predict(img_flat)[0]
            self.result_label.config(text=f"Dígito Predicho: {pred_digit}")
        else:
            self.result_label.config(text="Error: Modelo no cargado")