import numpy as np
import matplotlib.pyplot as plt

class Simulacion2D:
    def __init__(self, tamaño_bosque, pasos_tiempo, R):
        self.tamaño_bosque = tamaño_bosque
        self.pasos_tiempo = pasos_tiempo
        self.R = R  # Velocidad de propagación en m/min
        self.bosque = np.zeros((tamaño_bosque, tamaño_bosque), dtype=int)
        self.NO_ENCENDIDO = 0
        self.PRECALENTAMIENTO = 1
        self.ARDIENDO = 2
        self.QUEMADO = 3

    def simular(self, puntos_ignicion):
        celdas_ardiendo = []
        for punto in puntos_ignicion:
            self.bosque[punto] = self.ARDIENDO

        # Guardar estado inicial
        plt.imshow(self.bosque, cmap='hot', interpolation='nearest')
        plt.xlabel('Metros')
        plt.ylabel('Metros')
        plt.title('Estado del bosque con puntos de ignición iniciales')
        plt.grid(True)
        plt.colorbar(label='Estado del fuego')
        plt.savefig('grafica_propagacion_fuego_inicial.png')
        plt.close()

        for t in range(self.pasos_tiempo):
            self.actualizar_bosque()
            celdas_ardiendo.append(np.sum(self.bosque == self.ARDIENDO))
            plt.imshow(self.bosque, cmap='hot', interpolation='nearest')
            plt.xlabel('Metros')
            plt.ylabel('Metros')
            plt.title(f'Tiempo: {t} minutos')
            plt.grid(True)
            plt.pause(0.1)

        plt.imshow(self.bosque, cmap='hot', interpolation='nearest')
        plt.xlabel('Metros')
        plt.ylabel('Metros')
        plt.title(f'Estado del bosque tras {self.pasos_tiempo} pasos')
        plt.grid(True)
        plt.colorbar(label='Estado del fuego')
        plt.savefig('grafica_propagacion_fuego_final.png')
        plt.close()

        # Guardar gráfica de líneas
        plt.figure()
        plt.plot(range(len(celdas_ardiendo)), celdas_ardiendo, 'r-', label='Celdas ardiendo')
        plt.xlabel('Tiempo (minutos)')
        plt.ylabel('Número de celdas ardiendo')
        plt.title('Propagación del fuego a lo largo del tiempo (Líneas)')
        plt.legend()
        plt.grid(True)
        plt.savefig('grafica_propagacion_fuego_lineas.png')
        plt.close()

        # Guardar gráfica de puntos
        plt.figure()
        plt.plot(range(len(celdas_ardiendo)), celdas_ardiendo, 'ro', markersize=5, alpha=0.7, label='Celdas ardiendo')
        plt.xlabel('Tiempo (minutos)')
        plt.ylabel('Número de celdas ardiendo')
        plt.title('Propagación del fuego a lo largo del tiempo (Puntos)')
        plt.legend()
        plt.grid(True)
        plt.savefig('grafica_propagacion_fuego_puntos.png')
        plt.close()

        return len(celdas_ardiendo), celdas_ardiendo

    def actualizar_bosque(self):
        nuevo_bosque = self.bosque.copy()
        for i in range(1, self.tamaño_bosque - 1):
            for j in range(1, self.tamaño_bosque - 1):
                if self.bosque[i, j] == self.ARDIENDO:
                    nuevo_bosque[i-1:i+2, j-1:j+2] = np.where(nuevo_bosque[i-1:i+2, j-1:j+2] == self.NO_ENCENDIDO, self.PRECALENTAMIENTO, nuevo_bosque[i-1:i+2, j-1:j+2])
                    nuevo_bosque[i, j] = self.QUEMADO
                elif self.bosque[i, j] == self.PRECALENTAMIENTO:
                    nuevo_bosque[i, j] = self.ARDIENDO
        self.bosque = nuevo_bosque

# Ejemplo de uso
if __name__ == "__main__":
    simulacion = Simulacion2D(10, 5, 1.5)
    simulacion.simular([(0, 0), (9, 9)])
