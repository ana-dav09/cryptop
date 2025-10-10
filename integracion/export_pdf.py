from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

class ExportPdf:
    def __init__(self):
        self.styles = getSampleStyleSheet()

    def qtable_to_list(self, qtable):
        rows = qtable.rowCount()
        cols = qtable.columnCount()
        data = []
        headers = [qtable.horizontalHeaderItem(c).text() for c in range(cols)]
        data.append(headers)
        for r in range(rows):
            row_data = []
            for c in range(cols):
                item = qtable.item(r, c)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data

    def generar_resumen(self, metadata, top_candidates):
        resumen = []
        resumen.append("El ataque lineal se ejecutó con éxito sobre el algoritmo "
                       f"{metadata.get('Algoritmo', 'N/A')} con {metadata.get('Número de rondas', 'N/A')} rondas.")
        resumen.append(f"Se usaron {metadata.get('Pares usados', 'N/A')} pares de texto plano-cifrado, "
                       f"con un tiempo de ejecución de {metadata.get('Tiempo de ejecución', 'N/A')}.")
        if top_candidates:
            resumen.append("Los resultados muestran que algunas subclaves aparecen repetidamente "
                           "como candidatas más probables. Esto refleja la existencia de una correlación estadística "
                           "que puede explotarse para reducir el espacio de búsqueda.")
        else:
            resumen.append("No se identificaron candidatos claros. Esto puede indicar que la muestra fue insuficiente "
                           "o que el sesgo estadístico es demasiado débil.")
        if metadata.get("Clave real") and metadata.get("Mejor candidato"):
            if metadata["Clave real"] == metadata["Mejor candidato"]:
                resumen.append("El mejor candidato coincide con la clave real: "
                               "el ataque logró recuperar la subclave correctamente.")
            else:
                resumen.append("El mejor candidato no coincide con la clave real: "
                               "aunque hubo correlaciones detectadas, no fueron suficientes para identificar la clave exacta.")
        return "\n".join(resumen)

    def export(self, filename, qtables: list, top_candidates: list, metadata: dict = None):
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []

        # Portada
        elements.append(Paragraph("Reporte Didáctico de Ataques - CryptJAD", self.styles["Title"]))
        elements.append(Spacer(1, 24))
        elements.append(Paragraph(
            "Este documento explica de forma clara y pedagógica los resultados de un ataque lineal. "
            "Cada sección describe qué significan las tablas y cómo deben interpretarse los datos.",
            self.styles["Normal"]
        ))
        elements.append(PageBreak())

        # Metadatos
        if metadata:
            elements.append(Paragraph("1. Información General del Ataque", self.styles["Heading1"]))
            elements.append(Paragraph(
                "Esta sección resume los parámetros de la ejecución del ataque. "
                "Los datos permiten contextualizar la dificultad del análisis.",
                self.styles["Normal"]
            ))
            elements.append(Spacer(1, 6))
            for key, value in metadata.items():
                elements.append(Paragraph(f"<b>{key}:</b> {value}", self.styles["Normal"]))
            elements.append(Spacer(1, 12))

        # LAT
        for idx, qtable in enumerate(qtables, 1):
            elements.append(Paragraph(f"2.{idx} Tabla {idx}: Distribución Lineal (LAT)", self.styles["Heading2"]))
            elements.append(Paragraph(
                "La <b>Linear Approximation Table (LAT)</b> muestra cuán fuerte es la correlación "
                "entre combinaciones de bits de entrada y salida. "
                "En un sistema perfectamente aleatorio, todos los valores deberían estar cercanos a cero. "
                "Los valores altos (positivos o negativos) indican un sesgo aprovechable para el ataque.",
                self.styles["Normal"]
            ))
            elements.append(Spacer(1, 6))
            data = self.qtable_to_list(qtable)
            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4A90E2")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 18))

        # Candidatos
        if top_candidates:
            elements.append(Paragraph("3. Candidatos de Subclave", self.styles["Heading1"]))
            elements.append(Paragraph(
                "En esta sección se muestran los <b>candidatos de subclave</b> que aparecen con mayor frecuencia. "
                "La hipótesis del ataque es que el candidato más repetido o con mayor sesgo corresponde "
                "a la subclave real del cifrado. Este método no garantiza certeza absoluta, pero reduce significativamente el espacio de búsqueda.",
                self.styles["Normal"]
            ))
            elements.append(Spacer(1, 6))
            for idx, top_c in enumerate(top_candidates, 1):
                data = self.qtable_to_list(top_c)
                table = Table(data, repeatRows=1)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2ECC71")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                elements.append(Paragraph(f"Tabla {idx}: Top Candidatos", self.styles["Heading3"]))
                elements.append(table)
                elements.append(Spacer(1, 12))

        # Resumen
        resumen_auto = self.generar_resumen(metadata if metadata else {}, top_candidates)
        elements.append(PageBreak())
        elements.append(Paragraph("4. Conclusiones y Observaciones", self.styles["Heading1"]))
        elements.append(Paragraph(
            "A continuación se presenta una interpretación didáctica de los resultados obtenidos:",
            self.styles["Normal"]
        ))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(resumen_auto.replace("\n", "<br/>"), self.styles["Normal"]))

        doc.build(elements)
