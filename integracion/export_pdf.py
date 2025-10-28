from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, 
                                Spacer, PageBreak, KeepTogether, Image, HRFlowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF
import json
from datetime import datetime

class ModernHeaderCanvas(canvas.Canvas):
    """Canvas personalizado con header/footer modernos"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        page_count = len(self.pages)
        for page_num, page in enumerate(self.pages, 1):
            self.__dict__.update(page)
            if page_num > 1:  # No header en portada
                self.draw_header_footer(page_num, page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def draw_header_footer(self, page_num, page_count):
        """Dibuja header y footer modernos"""
        # Header con gradiente simulado
        self.setFillColor(colors.HexColor('#1e40af'))
        self.rect(0, A4[1] - 40, A4[0], 40, fill=True, stroke=False)
        
        self.setFillColor(colors.white)
        self.setFont("Helvetica-Bold", 11)
        self.drawString(30, A4[1] - 25, "CryptJAD - Criptoanálisis de Baby AES")
        
        # Footer
        self.setFillColor(colors.HexColor('#64748b'))
        self.setFont("Helvetica", 8)
        self.drawRightString(A4[0] - 30, 20, f"Página {page_num} de {page_count}")
        self.drawString(30, 20, datetime.now().strftime("%d/%m/%Y"))

class ExportPdf:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
        # Paleta de colores moderna
        self.colors = {
            'primary': '#2563eb',      # Azul vibrante
            'secondary': '#8b5cf6',    # Púrpura
            'success': '#10b981',      # Verde
            'warning': '#f59e0b',      # Naranja
            'danger': '#ef4444',       # Rojo
            'info': '#06b6d4',         # Cyan
            'dark': '#1e293b',         # Gris oscuro
            'light': '#f8fafc',        # Gris muy claro
            'accent': '#ec4899',       # Rosa
        }
        
        # ========== ESTILOS MODERNOS ==========
        
        # Título principal (portada)
        self.styles.add(ParagraphStyle(
            name='ModernTitle',
            parent=self.styles['Title'],
            fontName='Helvetica-Bold',
            fontSize=32,
            textColor=colors.HexColor(self.colors['primary']),
            spaceAfter=12,
            alignment=TA_CENTER,
            leading=38
        ))
        
        # Subtítulo portada
        self.styles.add(ParagraphStyle(
            name='ModernSubtitle',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=16,
            textColor=colors.HexColor(self.colors['secondary']),
            spaceAfter=8,
            alignment=TA_CENTER,
            leading=20
        ))
        
        # Fase (con banner de color)
        self.styles.add(ParagraphStyle(
            name='PhaseTitle',
            parent=self.styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=colors.white,
            spaceAfter=10,
            spaceBefore=10,
            leftIndent=15,
            rightIndent=15,
            leading=20
        ))
        
        # Descripción de fase
        self.styles.add(ParagraphStyle(
            name='PhaseDescription',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor(self.colors['dark']),
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leftIndent=10,
            rightIndent=10,
            leading=14
        ))
        
        # Título de paso (con ícono)
        self.styles.add(ParagraphStyle(
            name='StepTitle',
            parent=self.styles['Heading3'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=colors.HexColor(self.colors['primary']),
            spaceAfter=6,
            spaceBefore=10,
            leftIndent=20
        ))
        
        # Contenido técnico
        self.styles.add(ParagraphStyle(
            name='TechContent',
            parent=self.styles['Normal'],
            fontName='Courier',
            fontSize=8,
            textColor=colors.HexColor(self.colors['dark']),
            leftIndent=30,
            rightIndent=30,
            spaceAfter=4,
            backColor=colors.HexColor(self.colors['light']),
            borderPadding=8,
            leading=11
        ))
        
        # Caja de información destacada
        self.styles.add(ParagraphStyle(
            name='InfoBox',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            textColor=colors.HexColor('#0c4a6e'),
            leftIndent=15,
            rightIndent=15,
            spaceAfter=10,
            spaceBefore=6,
            backColor=colors.HexColor('#e0f2fe'),
            borderPadding=10,
            borderColor=colors.HexColor(self.colors['info']),
            borderWidth=2,
            leading=12
        ))
        
        # Caja de éxito
        self.styles.add(ParagraphStyle(
            name='SuccessBox',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.HexColor('#065f46'),
            leftIndent=15,
            rightIndent=15,
            spaceAfter=10,
            spaceBefore=6,
            backColor=colors.HexColor('#d1fae5'),
            borderPadding=10,
            borderColor=colors.HexColor(self.colors['success']),
            borderWidth=2,
            leading=13
        ))
        
        # Caja de advertencia
        self.styles.add(ParagraphStyle(
            name='WarningBox',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            textColor=colors.HexColor('#78350f'),
            leftIndent=15,
            rightIndent=15,
            spaceAfter=10,
            spaceBefore=6,
            backColor=colors.HexColor('#fef3c7'),
            borderPadding=10,
            borderColor=colors.HexColor(self.colors['warning']),
            borderWidth=2,
            leading=12
        ))
        
        # Subtítulo de sección
        self.styles.add(ParagraphStyle(
            name='SectionSubtitle',
            parent=self.styles['Heading4'],
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.HexColor(self.colors['secondary']),
            spaceAfter=4,
            spaceBefore=8,
            leftIndent=25
        ))

    def create_phase_banner(self, phase_name, color):
        """Crea un banner visual para las fases"""
        drawing = Drawing(6.5*inch, 45)
        
        # Rectángulo de fondo con gradiente simulado
        rect = Rect(0, 0, 6.5*inch, 45, 
                   fillColor=colors.HexColor(color),
                   strokeColor=None)
        drawing.add(rect)
        
        # Texto
        text = String(15, 15, phase_name,
                     fontName='Helvetica-Bold',
                     fontSize=14,
                     fillColor=colors.white)
        drawing.add(text)
        
        return drawing

    def create_metric_card(self, label, value, icon="📊"):
        """Crea una tarjeta de métrica visual"""
        table_data = [[f"{icon}  {label}", value]]
        t = Table(table_data, colWidths=[2.5*inch, 3*inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor('#eff6ff')),
            ("BACKGROUND", (1, 0), (1, 0), colors.white),
            ("TEXTCOLOR", (0, 0), (0, 0), colors.HexColor(self.colors['primary'])),
            ("TEXTCOLOR", (1, 0), (1, 0), colors.HexColor(self.colors['dark'])),
            ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, 0), "Courier-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, -1), 2, colors.HexColor(self.colors['primary'])),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        return t

    def create_modern_table(self, data, headers=None, color_scheme='primary'):
        """Crea una tabla con diseño moderno"""
        if not data:
            return None
        
        if headers:
            table_data = [headers] + data
        else:
            table_data = data
        
        num_cols = len(table_data[0])
        col_width = 6.5 * inch / num_cols
        
        t = Table(table_data, colWidths=[col_width] * num_cols, repeatRows=1)
        
        header_color = colors.HexColor(self.colors.get(color_scheme, self.colors['primary']))
        
        t.setStyle(TableStyle([
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), header_color),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            
            # Body
            ("FONTNAME", (0, 1), (-1, -1), "Courier"),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("ALIGN", (0, 1), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            
            # Bordes y colores alternados
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), 
             [colors.white, colors.HexColor('#f8fafc')]),
            
            # Padding
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        return t

    def create_key_value_cards(self, data_dict, max_items=None):
        """Crea tarjetas key-value modernas"""
        elements = []
        count = 0
        
        for key, value in data_dict.items():
            if max_items and count >= max_items:
                break
            
            formatted_value = self.format_value(value)
            card = self.create_metric_card(key, formatted_value)
            elements.append(card)
            elements.append(Spacer(1, 4))
            count += 1
        
        return elements

    def format_value(self, value):
        """Formatea valores para mostrar"""
        if isinstance(value, float):
            if abs(value) < 0.001:
                return f"{value:.8f}"
            return f"{value:.6f}"
        elif isinstance(value, list):
            if len(value) == 0:
                return "[]"
            elif len(value) <= 4:
                return ", ".join(str(v) for v in value)
            else:
                return f"[{value[0]}, ..., {value[-1]}] ({len(value)} items)"
        else:
            return str(value)

    def qtable_to_list(self, qtable):
        """Convierte QTableWidget a lista"""
        rows = qtable.rowCount()
        cols = qtable.columnCount()
        data = []
        headers = [qtable.horizontalHeaderItem(c).text() if qtable.horizontalHeaderItem(c) else f"Col{c}" 
                   for c in range(cols)]
        data.append(headers)
        for r in range(rows):
            row_data = []
            for c in range(cols):
                item = qtable.item(r, c)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data

    def create_cover_page(self, metadata):
        """Crea portada moderna"""
        elements = []
        
        elements.append(Spacer(1, 1.5*inch))
        
        # Título principal
        elements.append(Paragraph("REPORTE DE<br/>CRIPTOANÁLISIS", self.styles["ModernTitle"]))
        elements.append(Spacer(1, 0.2*inch))
        
        # Subtítulo
        attack_type = metadata.get('Tipo de ataque', 'Criptográfico')
        elements.append(Paragraph(f"Ataque {attack_type} en Baby AES", self.styles["ModernSubtitle"]))
        elements.append(Spacer(1, 0.4*inch))
        
        # Línea divisoria
        elements.append(HRFlowable(width="80%", thickness=2, 
                                   color=colors.HexColor(self.colors['primary']),
                                   spaceAfter=0.3*inch, spaceBefore=0.3*inch))
        
        # Información clave en tarjetas
        key_info = {
            'Algoritmo': metadata.get('Algoritmo', 'Baby AES'),
            'Rondas': metadata.get('Número de rondas', 'N/A'),
            'Fecha': datetime.now().strftime("%d de %B, %Y")
        }
        
        for key, value in key_info.items():
            card = self.create_metric_card(key, value, "🔐")
            elements.append(card)
            elements.append(Spacer(1, 8))
        
        elements.append(Spacer(1, 0.8*inch))
        
        # Pie de portada
        elements.append(Paragraph(
            "Documento generado automáticamente por CryptJAD<br/>"
            "Herramienta Educativa de Criptoanálisis",
            self.styles["Normal"]
        ))
        
        return elements

    def format_phase(self, phase_data, phase_num):
        """Formatea una fase completa con diseño moderno"""
        elements = []
        
        phase_name = phase_data.get("phase", f"Fase {phase_num}")
        phase_desc = phase_data.get("description", "")
        
        # Colores por fase
        phase_colors = [
            self.colors['primary'],
            self.colors['secondary'], 
            self.colors['info'],
            self.colors['success'],
            self.colors['accent']
        ]
        color = phase_colors[phase_num % len(phase_colors)]
        
        # Banner de fase
        banner = self.create_phase_banner(phase_name, color)
        elements.append(banner)
        elements.append(Spacer(1, 10))
        
        # Descripción
        if phase_desc:
            elements.append(Paragraph(
                f"📋 {phase_desc}",
                self.styles["PhaseDescription"]
            ))
            elements.append(Spacer(1, 12))
        
        # Procesar pasos
        steps = phase_data.get("steps", [])
        for step_idx, step_data in enumerate(steps, 1):
            step_elements = self.format_step(step_data, step_idx, color)
            elements.extend(step_elements)
        
        elements.append(Spacer(1, 20))
        return elements

    def format_step(self, step_data, step_num, phase_color):
        """Formatea un paso con diseño moderno"""
        elements = []
        
        step_title = step_data.get("step", f"Paso {step_num}")
        description = step_data.get("description", "")
        
        # Título del paso con ícono
        if step_title:
            icon = "▶️" if isinstance(step_title, str) else f"{step_num}️⃣"
            elements.append(Paragraph(
                f"{icon} <b>{step_title}</b>",
                self.styles["StepTitle"]
            ))
        
        # Descripción
        if description:
            elements.append(Paragraph(description, self.styles["PhaseDescription"]))
            elements.append(Spacer(1, 6))
        
        # Notas especiales
        note = step_data.get("note", "")
        if note:
            elements.append(Paragraph(f"💡 <b>Nota:</b> {note}", self.styles["InfoBox"]))
        
        interpretation = step_data.get("interpretation", "")
        if interpretation:
            elements.append(Paragraph(f"📊 <b>Análisis:</b> {interpretation}", self.styles["InfoBox"]))
        
        conclusion = step_data.get("conclusion", "")
        if conclusion:
            elements.append(Paragraph(f"✅ <b>Resultado:</b> {conclusion}", self.styles["SuccessBox"]))
        
        # Datos simples en tarjetas
        simple_data = {}
        complex_keys = ["substeps", "step", "description", "note", "interpretation", 
                       "conclusion", "rounds", "pairs_analyzed", "key_tests", "top_candidates",
                       "mask_selections", "correlation_details", "sbox_values", "sbox_hex"]
        
        for key, value in step_data.items():
            if key not in complex_keys and not isinstance(value, (list, dict)):
                simple_data[key] = value
        
        if simple_data:
            cards = self.create_key_value_cards(simple_data)
            elements.extend(cards)
        
        # Substeps
        substeps = step_data.get("substeps", [])
        if substeps:
            for substep in substeps:
                elements.append(Spacer(1, 8))
                elements.extend(self.format_substep(substep))
        
        # Tablas complejas
        if "rounds" in step_data and isinstance(step_data["rounds"], list):
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("📈 <b>Detalle por Ronda</b>", self.styles["SectionSubtitle"]))
            
            rounds_data = step_data["rounds"]
            if rounds_data:
                # Simplificar datos para tabla
                simple_rounds = []
                for r in rounds_data:
                    simple_rounds.append([
                        str(r.get('round', '')),
                        r.get('input_mask', '')[:20] + '...' if len(r.get('input_mask', '')) > 20 else r.get('input_mask', ''),
                        r.get('output_mask', '')[:20] + '...' if len(r.get('output_mask', '')) > 20 else r.get('output_mask', ''),
                        f"{r.get('correlation', 0):.4f}" if 'correlation' in r else '',
                        f"{r.get('accumulated_corr', 0):.6f}" if 'accumulated_corr' in r else ''
                    ])
                
                table = self.create_modern_table(
                    simple_rounds,
                    headers=['Ronda', 'Máscara Entrada', 'Máscara Salida', 'Corr', 'Corr Acum'],
                    color_scheme='secondary'
                )
                if table:
                    elements.append(table)
        
        if "top_candidates" in step_data and isinstance(step_data["top_candidates"], list):
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("🏆 <b>Top Candidatos</b>", self.styles["SectionSubtitle"]))
            
            candidates = step_data["top_candidates"][:10]  # Solo top 10
            if candidates:
                cand_data = []
                for c in candidates:
                    cand_data.append([
                        str(c.get('rank', '')),
                        c.get('key_hex', c.get('key_binary', ''))[:12],
                        str(c.get('score', c.get('abs_score', ''))),
                        f"{c.get('estimated_bias', c.get('bias', 0)):.4f}" if 'estimated_bias' in c or 'bias' in c else ''
                    ])
                
                table = self.create_modern_table(
                    cand_data,
                    headers=['Rank', 'Clave', 'Score', 'Sesgo'],
                    color_scheme='success'
                )
                if table:
                    elements.append(table)
        
        elements.append(Spacer(1, 12))
        return elements

    def format_substep(self, substep_data):
        """Formatea un substep"""
        elements = []
        
        operation = substep_data.get("operation", "")
        if operation:
            elements.append(Paragraph(
                f"→ <b>{operation}</b>",
                self.styles["SectionSubtitle"]
            ))
        
        # Datos del substep
        for key, value in substep_data.items():
            if key in ["operation", "mask_selections", "correlation_details"]:
                continue
            
            if not isinstance(value, (list, dict)):
                elements.append(Paragraph(
                    f"<b>{key}:</b> {self.format_value(value)}",
                    self.styles["TechContent"]
                ))
        
        elements.append(Spacer(1, 4))
        return elements

    def export(self, filename, qtables: list, top_candidates: list, 
              metadata: dict = None, trace_path: str = None):
        """Exporta PDF con diseño moderno"""
        
        doc = SimpleDocTemplate(
            filename, 
            pagesize=A4,
            topMargin=50,
            bottomMargin=50,
            leftMargin=40,
            rightMargin=40
        )
        
        elements = []

        # ========== PORTADA ==========
        if metadata:
            cover_elements = self.create_cover_page(metadata)
            elements.extend(cover_elements)
            elements.append(PageBreak())

        # ========== TRAZA COMPLETA ==========
        if trace_path:
            try:
                with open(trace_path, 'r', encoding='utf-8') as f:
                    trace_data = json.load(f)
                
                # Título de sección
                title_banner = self.create_phase_banner(
                    "TRAZA DETALLADA DEL ATAQUE", 
                    self.colors['dark']
                )
                elements.append(title_banner)
                elements.append(Spacer(1, 15))
                
                elements.append(Paragraph(
                    "Este reporte documenta cada fase del criptoanálisis ejecutado. "
                    "Incluye los cálculos intermedios, decisiones algorítmicas y "
                    "resultados parciales que conducen a la recuperación de la subclave.",
                    self.styles["PhaseDescription"]
                ))
                elements.append(Spacer(1, 20))
                
                # Procesar fases
                phases = trace_data.get("phases", [])
                for phase_num, phase in enumerate(phases, 1):
                    phase_elements = self.format_phase(phase, phase_num)
                    elements.extend(phase_elements)
                    
                    if phase_num < len(phases):
                        elements.append(PageBreak())
                
            except Exception as e:
                print(f"❌ Error al cargar traza: {e}")
                elements.append(Paragraph(
                    f"⚠️ Error al procesar la traza: {str(e)}",
                    self.styles["WarningBox"]
                ))

        # ========== TABLAS DE DISTRIBUCIÓN ==========
        if qtables and any(qt.rowCount() > 0 for qt in qtables):
            elements.append(PageBreak())
            banner = self.create_phase_banner("TABLAS DE DISTRIBUCIÓN", self.colors['info'])
            elements.append(banner)
            elements.append(Spacer(1, 12))
            
            for idx, qtable in enumerate(qtables, 1):
                if qtable.rowCount() == 0:
                    continue
                
                elements.append(Paragraph(f"📊 Tabla {idx}", self.styles["StepTitle"]))
                elements.append(Spacer(1, 6))
                
                data = self.qtable_to_list(qtable)
                table = self.create_modern_table(data[1:], headers=data[0], color_scheme='info')
                if table:
                    elements.append(table)
                    elements.append(Spacer(1, 16))

        # ========== CANDIDATOS ==========
        if top_candidates and any(tc.rowCount() > 0 for tc in top_candidates):
            elements.append(PageBreak())
            banner = self.create_phase_banner("CANDIDATOS DE SUBCLAVE", self.colors['success'])
            elements.append(banner)
            elements.append(Spacer(1, 12))
            
            for idx, top_c in enumerate(top_candidates, 1):
                if top_c.rowCount() == 0:
                    continue
                
                data = self.qtable_to_list(top_c)
                table = self.create_modern_table(data[1:], headers=data[0], color_scheme='success')
                if table:
                    elements.append(table)
                    elements.append(Spacer(1, 16))

        # ========== GENERAR PDF ==========
        doc.build(elements, canvasmaker=ModernHeaderCanvas)
        print(f"✅ PDF moderno generado: {filename}")