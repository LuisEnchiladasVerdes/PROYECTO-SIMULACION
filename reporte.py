from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors

class Reporte:
    def __init__(self, nombre_archivo, tamaño_bosque, R, celdas_quemadas, T, RH, v, phi, theta, KS, Kr, ciudad):
        self.nombre_archivo = nombre_archivo
        self.tamaño_bosque = tamaño_bosque
        self.R = R
        self.celdas_quemadas = celdas_quemadas
        self.T = T
        self.RH = RH
        self.v = v
        self.phi = phi
        self.theta = theta
        self.KS = KS
        self.Kr = Kr
        self.ciudad = ciudad

    def generar_pdf(self):
        doc = SimpleDocTemplate(self.nombre_archivo, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        self.add_title(elements, styles['Title'])
        self.add_simulation_description(elements, styles['BodyText'])
        self.add_equations_variables(elements, styles['BodyText'])  # Correct method name here
        self.add_variable_table(elements)
        self.add_propagation_time(elements, styles['BodyText'])
        self.add_R_value(elements, styles['BodyText'])
        self.add_graphs_with_descriptions(elements, styles['Heading2'], styles['BodyText'])

        doc.build(elements)

    def add_title(self, elements, style):
        titulo = Paragraph("Informe de Simulación de Propagación de Incendios Forestales", style)
        elements.append(titulo)
        elements.append(Spacer(1, 12))

    def add_simulation_description(self, elements, style):
        descripcion = f"""
        En este informe se presentan los resultados obtenidos de una simulación sobre la propagación de incendios forestales en la ciudad de {self.ciudad}.
        Se utilizaron datos meteorológicos en tiempo real de {self.ciudad}, obtenidos de la API OpenWeatherMap para demostrar cómo se propaga el fuego en un bosque, utilizando
        una cuadrícula de {self.tamaño_bosque} x {self.tamaño_bosque} celdas. Los estados de las celdas son:
        NO_INCENDIDO (0), PRECALENTAMIENTO (1), ARDIENDO (2), y QUEMADO (3). La velocidad de propagación
        del fuego se calcula utilizando una velocidad de {self.R} m/min basada en las condiciones meteorológicas actuales.

        """
        elements.append(Paragraph(descripcion, style))
        elements.append(Spacer(1, 12))

    def add_equations_variables(self, elements, style):
        # Correct this method name if it's called differently elsewhere
        ecuaciones = """
        <b>Ecuaciones Utilizadas:</b><br/>
        <ul>
            <li>Velocidad inicial de propagación del incendio:<br/><i>R_0 = a * T + b * W + c * (100 - RH) - d</i></li>
            <li>Velocidad del viento corregida:<br/><i>W = (v / 0.836)^(2/3)</i></li>
            <li>Coeficiente de corrección del viento:<br/><i>K_ϕ = exp(0.1783 * v * cos(ϕ))</i></li>
            <li>Coeficiente de corrección del terreno:<br/><i>K_θ = exp(3.553 * g * tan(1.2 * θ))</i></li>
            <li>Velocidad de propagación del incendio:<br/><i>R = R_0 * K_ϕ * K_θ * K_S * K_r</i></li>

        </ul>
        """
        elements.append(Paragraph(ecuaciones, style))
        elements.append(Spacer(1, 12))

    def add_variable_table(self, elements):
        variables = [
            ["Variable", "Descripción", "Valor"],
            ["T", "Temperatura del aire (°C)", self.T],
            ["RH", "Humedad relativa (%)", self.RH],
            ["v", "Velocidad del viento (m/s)", self.v],
            ["ϕ", "Dirección del viento (radianes)", self.phi],
            ["θ", "Pendiente del terreno (radianes)", self.theta],
            ["g", "Gravedad", "1"],
            ["a, b, c, d", "Constantes del modelo", "0.03, 0.05, 0.01, 0.3"],
            ["K_S", "Índice de inflamabilidad", self.KS],
            ["K_r", "Coeficiente de corrección del tiempo", self.Kr]
        ]
        table = Table(variables, style=[
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        elements.append(table)
        elements.append(Spacer(1, 12))

    def add_propagation_time(self, elements, style):
        total_time = sum(x > 0 for x in self.celdas_quemadas)  # Assuming each step is one minute
        description = f"Tiempo total de propagación en el bosque: {total_time} minutos."
        elements.append(Paragraph(description, style))
        elements.append(Spacer(1, 12))

    def add_R_value(self, elements, style):
        description = f"Velocidad de propagación del fuego calculada (R): {self.R:.2f} m/min."
        elements.append(Paragraph(description, style))
        elements.append(Spacer(1, 12))

    def add_graphs_with_descriptions(self, elements, title_style, body_style):
        max_burning = max(self.celdas_quemadas)
        time_of_max_burning = self.celdas_quemadas.index(max_burning)
        total_burning_time = len([x for x in self.celdas_quemadas if x > 0])

        # Gráfica de calor final
        description = f"Esta gráfica muestra el estado final del bosque tras la simulación, destacando las áreas más afectadas por el fuego. Siendo las celdas de color negro las que estan en el estado de 'No Incendiadas' y las celdas blancas siendo las 'Quemadas', tambien se observa el comportamiento del fuego en base a las condiciones climaticas."
        self.add_graph_description(elements, "Gráfica de Propagación del Fuego (Calor)", "grafica_propagacion_fuego_final.png", title_style, body_style, description)
        
        # Gráfica de líneas
        description = f"""La gráfica de líneas presentada ilustra la evolución temporal del número de celdas en estado de combustión durante la simulación. En el eje horizontal se representa el tiempo en minutos, mientras que el eje vertical muestra la cantidad de celdas que están ardiendo en cada momento. A lo largo del tiempo, se observa una tendencia creciente en el número de celdas en combustión, alcanzando su punto máximo en el minuto {time_of_max_burning}, momento en el cual se registra un total de {max_burning} celdas en estado de incendio simultáneamente.
                        Este aumento puede interpretarse como un indicio del avance y expansión del fuego, con una propagación más acelerada en la segunda minuto de la simulación. La gráfica permite visualizar cómo el fuego se propaga y afecta a un mayor número de celdas con el paso del tiempo, proporcionando información valiosa sobre el comportamiento y la intensidad del incendio a lo largo de la simulación."""
        
        
        self.add_graph_description(elements, "Gráfica de Propagación del Fuego a lo Largo del Tiempo (Líneas)", "grafica_propagacion_fuego_lineas.png", title_style, body_style, description)
        
        # Gráfica de puntos
        description = """La gráfica de puntos presentada ofrece una representación visual de los cambios discretos en el número de celdas en estado de combustión a lo largo del tiempo durante la simulación. Cada punto en la gráfica indica un valor específico del número de celdas ardiendo en un momento concreto, permitiendo observar la variabilidad y la intensidad fluctuante del fuego en diferentes instantes.
                        A través de la dispersión de puntos, se puede apreciar cómo el número de celdas en combustión experimenta oscilaciones a lo largo de la simulación, lo que refleja la naturaleza no uniforme y dinámica del incendio. Las variaciones en los valores de los puntos proporcionan una visión detallada de los periodos de mayor y menor intensidad del fuego, permitiendo un análisis más profundo de los patrones de propagación y la evolución del incendio en diferentes momentos. """
        self.add_graph_description(elements, "Gráfica de Propagación del Fuego a lo Largo del Tiempo (Puntos)", "grafica_propagacion_fuego_puntos.png", title_style, body_style, description)

    def add_graph_description(self, elements, title, image_path, title_style, body_style, description):
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 12))
        elements.append(Image(image_path, width=400, height=200))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(description, body_style))
        elements.append(Spacer(1, 12))

# Ejemplo de uso
if __name__ == "__main__":
    reporte = Reporte("informe_simulacion_incendio.pdf", 100, 1.5, [100, 200, 300], 25, 40, 5, 0.5, 0.1, 1, 1, "Oaxaca")
    reporte.generar_pdf()
