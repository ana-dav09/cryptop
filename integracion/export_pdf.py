from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class ExportPdf:
    def __init__(self):
        self.styles = getSampleStyleSheet()

    def qtable_to_list(self, qtable):
        """
        Convierte un QTableWidget en lista de listas (para ReportLab).
        Incluye encabezados.
        """
        rows = qtable.rowCount()
        cols = qtable.columnCount()
        data = []

        # Encabezados
        headers = [qtable.horizontalHeaderItem(c).text() for c in range(cols)]
        data.append(headers)

        # Filas
        for r in range(rows):
            row_data = []
            for c in range(cols):
                item = qtable.item(r, c)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        return data

    def export(self, filename, qtables: list, top_candidates: list, resumen: str = None):
        """
        Exporta varias QTableWidgets y un resumen opcional a PDF.
        """
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []

        # Título
        elements.append(Paragraph("Resultados de Ataques - CryptJAD", self.styles["Title"]))
        elements.append(Spacer(1, 12))

        # Tablas de QTableWidget
        for idx, qtable in enumerate(qtables, 1):
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
            elements.append(Paragraph(f"Tabla {idx}", self.styles["Heading2"]))
            elements.append(table)
            elements.append(Spacer(1, 12))

        # Candidatos en tabla
        for idx, top_c in enumerate(top_candidates, 1):
            data = self.qtable_to_list(top_c)
            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2ECC71")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            elements.append(Paragraph(f"Top Candidatos", self.styles["Heading2"]))
            elements.append(table)
            elements.append(Spacer(1, 12))

        # Resumen en texto
        if resumen:
            elements.append(Paragraph("Resumen del Ataque", self.styles["Heading2"]))
            elements.append(Paragraph(resumen.replace("\n", "<br/>"), self.styles["Normal"]))

        doc.build(elements)
