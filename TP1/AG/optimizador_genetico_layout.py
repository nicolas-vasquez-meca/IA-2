#FALTA REVISAR EL CODIGO, NO SE SI FUNCIONA O NO, PERO LA IDEA ES ESA

import random
import csv

class OptimizadorLayout:

    def __init__(self, mapa, estacion):

        self.mapa = mapa
        self.estacion = estacion
        self.frecuencias = {}

    # -------------------
    # leer órdenes
    # -------------------

    def cargar_ordenes(self, archivo):

        with open(archivo) as f:

            reader = csv.reader(f)

            for orden in reader:

                for producto in orden:

                    p = int(producto)

                    self.frecuencias[p] = self.frecuencias.get(p,0) + 1


    # -------------------
    # fitness
    # -------------------

    def fitness(self, layout):

        costo = 0

        ex = self.estacion.x
        ey = self.estacion.y

        for producto,estanteria in layout.items():

            x = estanteria.x
            y = estanteria.y

            distancia = abs(x-ex) + abs(y-ey)

            freq = self.frecuencias.get(producto,1)

            costo += distancia * freq

        return costo


    # -------------------
    # generar individuo
    # -------------------

    def generar_individuo(self):

        estanterias = self.mapa.estanterias.copy()

        random.shuffle(estanterias)

        layout = {}

        productos = list(self.frecuencias.keys())

        for p,e in zip(productos,estanterias):

            layout[p] = e

        return layout


    # -------------------
    # mutación
    # -------------------

    def mutar(self,layout):

        p1,p2 = random.sample(list(layout.keys()),2)

        layout[p1],layout[p2] = layout[p2],layout[p1]


    # -------------------
    # algoritmo genético
    # -------------------

    def optimizar(self):

        poblacion = [self.generar_individuo() for _ in range(50)]

        for _ in range(200):

            poblacion.sort(key=lambda x: self.fitness(x))

            poblacion = poblacion[:20]

            nuevos = []

            while len(nuevos) < 30:

                padre = random.choice(poblacion)

                hijo = padre.copy()

                if random.random() < 0.3:
                    self.mutar(hijo)

                nuevos.append(hijo)

            poblacion.extend(nuevos)

        mejor = min(poblacion,key=lambda x: self.fitness(x))

        return mejor