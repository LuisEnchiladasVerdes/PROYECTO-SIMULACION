import requests
import numpy as np
from tkinter import Tk, Label, Button, Entry, messagebox, Canvas, Frame
from simulacion2d import Simulacion2D
from reporte import Reporte
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os
import subprocess
import sys

class Interfaz:
    def __init__(self, clave_api, ubicacion):
        self.clave_api = clave_api
        self.ubicacion = ubicacion
        self.tamaño_bosque = None
        self.pasos_tiempo = None
        self.tamaño_celula = None
        self.R = None
        self.datos_simulacion = None
        self.T = None
        self.RH = None
        self.v = None
        self.phi = None
        self.theta = 0.1
        self.KS = 1
        self.Kr = 1

        self.ventana = Tk()
        self.ventana.title("Simulación de la Propagacion Incendios Forestales")
        pantalla_ancho = self.ventana.winfo_screenwidth()
        pantalla_alto = self.ventana.winfo_screenheight()
        self.ventana.geometry(f"{pantalla_ancho}x{pantalla_alto}")

        self.lblBG = Label(self.ventana, bd=1, relief='solid')
        self.lblBG.place(relx=0, rely=0, relwidth=0.16, relheight=1)

        self.lbl1 = Label(self.ventana, text='Ingrese el largo del bosque')
        self.lbl1.place(x=10, y=10, width=150, height=25)
        self.txt1 = Entry(self.ventana, bg="gray")
        self.txt1.place(x=10, y=50, width=100, height=30)

        self.lbl2 = Label(self.ventana, text='Ingrese la cantidad de minutos')
        self.lbl2.place(x=10, y=90, width=180, height=25)
        self.txt2 = Entry(self.ventana, bg="gray")
        self.txt2.place(x=10, y=130, width=100, height=30)

        self.lbl3 = Label(self.ventana, text='Ingrese el tamaño de la célula')
        self.lbl3.place(x=10, y=170, width=160, height=25)
        self.txt3 = Entry(self.ventana, bg="gray")
        self.txt3.place(x=10, y=210, width=100, height=30)

        self.valor = False

        btnIniciar = Button(self.ventana, text='Iniciar Simulación', command=self.iniciarSimulacion)
        btnIniciar.place(relx=0.08, rely=0.90, anchor='center')

        btnGenerar = Button(self.ventana, text='Generar reporte', command=self.generar)
        btnGenerar.place(relx=0.08, rely=0.96, anchor='center')

        self.canvas_frame = Frame(self.ventana)
        self.canvas_frame.place(relx=0.17, rely=0, relwidth=0.83, relheight=1)

    def iniciarSimulacion(self):
        try:
            valor1 = self.txt1.get().strip()
            valor2 = self.txt2.get().strip()
            valor3 = self.txt3.get().strip()

            if valor1 == "" or valor2 == "" or valor3 == "":
                messagebox.showerror("Error", "Todos los campos deben estar llenos.")
                return  

            self.tamaño_bosque = int(valor1)
            self.pasos_tiempo = int(valor2)
            self.tamaño_celula = int(valor3)

            try:
                int(valor1)
                int(valor2)
                int(valor3)
            except ValueError:
                messagebox.showerror("Error", "Todos los campos deben contener valores numéricos enteros.")
                self.txt1.delete(0, 'end')
                self.txt2.delete(0, 'end')
                self.txt3.delete(0, 'end')
                return 
            
            self.valor = True
            
            T, RH, v, phi = self.obtener_datos_meteorológicos()
            if T is not None:
                self.T = T
                self.RH = RH
                self.v = v
                self.phi = phi
                self.R = self.calcular_velocidad_propagacion(T, v, RH, phi, self.theta, self.KS, self.Kr)
                tiempo_propagacion = self.calcular_tiempo_propagacion(self.tamaño_celula, self.R)
                print(f"Tiempo estimado de propagación entre células: {tiempo_propagacion:.2f} minutos")
                print(f"Variables del clima: Temperatura = {T}°C, Humedad = {RH}%, Velocidad del viento = {v} m/s, Dirección del viento = {phi} radianes")
                print(f"Velocidad de propagación del incendio (R): {self.R:.2f} m/min")

                simulacion2d = Simulacion2D(self.tamaño_bosque, self.pasos_tiempo, self.R)
                self.datos_simulacion = simulacion2d.simular([(self.tamaño_bosque//2, self.tamaño_bosque//2), (self.tamaño_bosque//4, self.tamaño_bosque//4)])

                self.mostrar_grafico(simulacion2d)
            else:
                print("No se pudo iniciar la simulación debido a la falta de datos meteorológicos.")

            self.txt1.delete(0, 'end')
            self.txt2.delete(0, 'end')
            self.txt3.delete(0, 'end')

        except ValueError:
            messagebox.showerror("Error", "Todos los campos deben contener valores numéricos enteros.")
            self.txt1.delete(0, 'end')
            self.txt2.delete(0, 'end')
            self.txt3.delete(0, 'end')

    def obtener_datos_meteorológicos(self):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={self.ubicacion}&appid={self.clave_api}&units=metric"
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            temperatura = datos['main']['temp']
            humedad = datos['main']['humidity']
            velocidad_viento = datos['wind']['speed']
            direccion_viento = datos['wind']['deg'] * np.pi / 180  # Convertir a radianes
            return temperatura, humedad, velocidad_viento, direccion_viento
        else:
            print(f"Error: No se pudo obtener los datos meteorológicos. Código de estado: {respuesta.status_code}")
            return None, None, None, None

    def calcular_velocidad_propagacion(self, T, v, RH, phi, theta, indice_inflamabilidad, coeficiente_correccion):
        a = 0.03  # Constante de temperatura
        b = 0.05  # Constante de velocidad del viento
        c = 0.01  # Constante de humedad
        d = 0.3   # Constante base de la velocidad de propagación
        theta = 0.1  # Pendiente en radianes
        indice_inflamabilidad = 1  # Índice de inflamabilidad
        coeficiente_correccion = 1  # Coeficiente de corrección temporal
        
        W = (v / 0.836)**(2/3)
        R0_val = a * T + b * W + c * (100 - RH) - d
        Kphi_val = np.exp(0.1783 * v * np.cos(phi))
        Ktheta_val = np.exp(3.553 * np.sin(theta))
        R = R0_val * Kphi_val * Ktheta_val * indice_inflamabilidad * coeficiente_correccion
        return R

    def calcular_tiempo_propagacion(self, tamaño_celula, R):
        return tamaño_celula / R

    def mostrar_grafico(self, simulacion2d):
        self.limpiar_canvas()
        fig, ax = plt.subplots()
        cax = ax.imshow(simulacion2d.bosque, cmap='hot', interpolation='nearest')
        ax.set_title(f'Estado del bosque tras {simulacion2d.pasos_tiempo} minutos')
        fig.colorbar(cax)
        
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def limpiar_canvas(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()


    def generar(self):
        if self.valor == True and self.R is not None and self.datos_simulacion is not None:
            archivo_pdf = "informe_simulacion_incendio.pdf"
            reporte = Reporte(
                archivo_pdf,
                self.tamaño_bosque,
                self.R,
                self.datos_simulacion[1],
                self.T,
                self.RH,
                self.v,
                self.phi,
                self.theta,
                self.KS,
                self.Kr,
                self.ubicacion  
            )
            reporte.generar_pdf()
            self.valor = False
            self.abrir_pdf(archivo_pdf)

            self.txt1.delete(0, 'end')
            self.txt2.delete(0, 'end')
            self.txt3.delete(0, 'end')
        else:
            messagebox.showerror("Error", "Primero se debe generar una simulación.")


    def abrir_pdf(self, archivo_pdf):
        try:
            if os.name == 'nt':  # Windows
                os.startfile(archivo_pdf)
            elif os.name == 'posix':  # macOS y Linux
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', archivo_pdf])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo PDF: {e}")


    def iniciar(self):
        self.ventana.mainloop()



app = Interfaz(clave_api='bd5e378503939ddaee76f12ad7a97608', ubicacion='Oaxaca, Mexico')
app.iniciar()