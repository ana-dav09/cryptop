import sys
from PyQt6 import QtWidgets, QtGui, QtCore

class InformationWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD - Información")
        self.setGeometry(50, 50, 1400, 900)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0F172A, stop:1 #1E293B);
            }
        """)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === HEADER MODERNO ===
        header = QtWidgets.QFrame()
        header.setFixedHeight(120)
        header.setStyleSheet("""
            QFrame {
                background: #2C3E50;
                border: none;
            }
        """)
        header_layout = QtWidgets.QVBoxLayout(header)
        header_layout.setContentsMargins(50, 20, 50, 20)

        title_label = QtWidgets.QLabel("⚡ Guía Técnica de Criptoanálisis")
        title_label.setFont(QtGui.QFont("Segoe UI", 32, QtGui.QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; background: transparent;")
        header_layout.addWidget(title_label)

        subtitle_label = QtWidgets.QLabel("Análisis Matemático • Complejidad Computacional • Factores de Éxito")
        subtitle_label.setFont(QtGui.QFont("Segoe UI", 13))
        subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); background: transparent;")
        header_layout.addWidget(subtitle_label)

        main_layout.addWidget(header)

        # === NAVEGACIÓN CON TABS ===
        tab_widget = QtWidgets.QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 0.05);
                color: rgba(255, 255, 255, 0.7);
                padding: 15px 30px;
                margin-right: 5px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-size: 13px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: rgba(99, 102, 241, 0.3);
                color: white;
                border-bottom: 3px solid #6366F1;
            }
            QTabBar::tab:hover:!selected {
                background: rgba(255, 255, 255, 0.1);
            }
        """)

        # TAB 1: Métodos de Ataque
        methods_tab = self.create_methods_tab()
        tab_widget.addTab(methods_tab, "📊 Métodos de Ataque")

        # TAB 2: Complejidad Matemática
        complexity_tab = self.create_complexity_tab()
        tab_widget.addTab(complexity_tab, "🔢 Complejidad Matemática")

        # TAB 3: Rendimiento y Hardware
        performance_tab = self.create_performance_tab()
        tab_widget.addTab(performance_tab, "⚙️ Rendimiento & Hardware")

        # TAB 4: Veracidad y Precisión
        accuracy_tab = self.create_accuracy_tab()
        tab_widget.addTab(accuracy_tab, "🎯 Veracidad de Resultados")

        main_layout.addWidget(tab_widget)

        # === FOOTER CON BOTÓN ===
        footer = QtWidgets.QFrame()
        footer.setFixedHeight(80)
        footer.setStyleSheet("background: rgba(15, 23, 42, 0.8); border: none;")
        footer_layout = QtWidgets.QHBoxLayout(footer)
        footer_layout.setContentsMargins(50, 15, 50, 15)

        close_btn = QtWidgets.QPushButton("← Volver al Dashboard")
        close_btn.setFixedHeight(50)
        close_btn.setFixedWidth(250)
        close_btn.setFont(QtGui.QFont("Segoe UI", 13, QtGui.QFont.Weight.Bold))
        close_btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366F1, stop:1 #8B5CF6);
                color: white;
                border-radius: 25px;
                border: 2px solid rgba(255, 255, 255, 0.1);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4F46E5, stop:1 #7C3AED);
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background: #4338CA;
            }
        """)
        close_btn.clicked.connect(self.close)
        footer_layout.setSpacing(20)
        footer_layout.addStretch()
        footer_layout.addWidget(close_btn)
        footer_layout.addStretch()

        main_layout.addWidget(footer)

    def create_scroll_area(self):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(255, 255, 255, 0.05);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(99, 102, 241, 0.6);
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(99, 102, 241, 0.8);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        return scroll

    def create_methods_tab(self):
        scroll = self.create_scroll_area()
        content = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Criptoanálisis Lineal
        linear_card = self.create_modern_card(
            "Criptoanálisis Lineal",
            "linear",
            """
            <div style='line-height: 1.8;'>
            <p style='font-size: 14px; color: #E2E8F0; margin-bottom: 15px;'>
            Desarrollado por <b>Mitsuru Matsui (1993)</b>, explota aproximaciones lineales entre 
            bits del texto plano, cifrado y la clave secreta.
            </p>
            ...
            </div>
            """,
            "#3B82F6"
        )
        layout.addWidget(linear_card)

        # Criptoanálisis Diferencial
        diff_card = self.create_modern_card(
            "Criptoanálisis Diferencial",
            "differential",
            """
            <div style='line-height: 1.8;'>
            <p style='font-size: 14px; color: #E2E8F0; margin-bottom: 15px;'>
            Creado por <b>Eli Biham y Adi Shamir (1990)</b>, estudia cómo diferencias en entradas
            se propagan a través del cifrado.
            </p>
            ...
            </div>
            """,
            "#10B981"
        )
        layout.addWidget(diff_card)

        # Criptoanálisis Algebraico
        alg_card = self.create_modern_card(
            "Criptoanálisis Algebraico",
            "algebraic",
            """
            <div style='line-height: 1.8;'>
            <p style='font-size: 14px; color: #E2E8F0; margin-bottom: 15px;'>
            Enfoque moderno que modela el cifrado como un <b>sistema de ecuaciones algebraicas</b>
            sobre campos finitos (típicamente GF(2)).</p>
            ...
            </div>
            """,
            "#F59E0B"
        )
        layout.addWidget(alg_card)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    def create_complexity_tab(self):
        scroll = self.create_scroll_area()
        content = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Título de sección
        title = QtWidgets.QLabel("Análisis de Complejidad Computacional")
        title.setFont(QtGui.QFont("Segoe UI", 24, QtGui.QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 10px;")
        layout.addWidget(title)

        # Comparativa de complejidades
        comp_card = self.create_modern_card(
            "Comparativa de Complejidades",
            "comparison",
            """
            <div style='line-height: 1.8;'>
            <p style='font-size: 14px; color: #CBD5E1; margin-bottom: 15px;'>
            <span style='color: #A78BFA; font-weight: bold;'>⚡ Complejidad Temporal vs. Complejidad de Datos</span>
            </p>
            <table style='width: 100%; border-collapse: collapse; margin: 15px 0;'>
            <tr style='background: rgba(139, 92, 246, 0.2);'>
                <th style='padding: 12px; text-align: left; color: #E2E8F0; border-bottom: 2px solid #8B5CF6;'>Método</th>
                <th style='padding: 12px; text-align: left; color: #E2E8F0; border-bottom: 2px solid #8B5CF6;'>Complejidad Temporal</th>
                <th style='padding: 12px; text-align: left; color: #E2E8F0; border-bottom: 2px solid #8B5CF6;'>Complejidad de Datos</th>
                <th style='padding: 12px; text-align: left; color: #E2E8F0; border-bottom: 2px solid #8B5CF6;'>Tipo de Datos</th>
            </tr>
            <tr style='background: rgba(255, 255, 255, 0.03);'>
                <td style='padding: 10px; color: #CBD5E1; border-bottom: 1px solid rgba(255,255,255,0.1);'>
                    <b>Fuerza Bruta</b>
                </td>
                <td style='padding: 10px; color: #FCD34D;'>O(2<sup>k</sup>)</td>
                <td style='padding: 10px; color: #34D399;'>O(1) - mínimo</td>
                <td style='padding: 10px; color: #94A3B8;'>1 par conocido</td>
            </tr>
            ...
            </table>
            </div>
            """,
            "#8B5CF6"
        )
        layout.addWidget(comp_card)

        # Factores que afectan complejidad
        factors_card = self.create_modern_card(
            "Factores de Complejidad del Cifrado",
            "factors",
            """
            <div style='line-height: 1.8;'>
            <p style='font-size: 14px; color: #CBD5E1; margin-bottom: 12px;'>
            <span style='color: #EC4899; font-weight: bold;'>📐 1. Número de Rondas (r)</span><br>
            ...
            </p>
            </div>
            """,
            "#EC4899"
        )
        layout.addWidget(factors_card)

        # Estimaciones cuantitativas
        estimates_card = self.create_modern_card(
            "Estimaciones de Tiempo Real",
            "estimates",
            """
            <div style='line-height: 1.8;'>
            <p style='font-size: 14px; color: #E2E8F0; margin-bottom: 15px;'>
            Asumiendo hardware moderno (CPU multi-core de 3 GHz, capaz de ~10⁹ operaciones/seg):
            </p>
            ...
            </div>
            """,
            "#06B6D4"
        )
        layout.addWidget(estimates_card)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    def create_performance_tab(self):
        scroll = self.create_scroll_area()
        content = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Título
        title = QtWidgets.QLabel("Optimización de Recursos de Hardware")
        title.setFont(QtGui.QFont("Segoe UI", 24, QtGui.QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 10px;")
        layout.addWidget(title)

        # CPU
        cpu_card = self.create_modern_card(
            "Procesador (CPU)",
            "cpu",
            """
            <div style='line-height: 1.8;'>
            <p style='font-size: 14px; color: #CBD5E1; margin-bottom: 12px;'>
            <span style='color: #F472B6; font-weight: bold;'>🔸 Número de Núcleos</span><br>
            ...
            </p>
            </div>
            """,
            "#F472B6"
        )
        layout.addWidget(cpu_card)

        # RAM
        ram_card = self.create_modern_card(
            "Memoria RAM",
            "ram",
            """
            <div style='line-height: 1.8;'>
            <p style='font-size: 14px; color: #CBD5E1; margin-bottom: 12px;'>
            <span style='color: #A78BFA; font-weight: bold;'>🔸 Cantidad de Memoria</span><br>
            ...
            </p>
            </div>
            """,
            "#A78BFA"
        )
        layout.addWidget(ram_card)

        # GPU
        gpu_card = self.create_modern_card(
            "GPU (Procesamiento Paralelo Masivo)",
            "gpu",
            """
            <div style='line-height: 1.8;'>
            <p style='font-size: 14px; color: #CBD5E1; margin-bottom: 12px;'>
            <span style='color: #34D399; font-weight: bold;'>🔸 Arquitectura SIMT</span><br>
            ...
            </p>
            </div>
            """,
            "#34D399"
        )
        layout.addWidget(gpu_card)

        # Almacenamiento
        storage_card = self.create_modern_card(
            "Almacenamiento",
            "storage",
            """
            <div style='line-height: 1.8;'>
            <p style='font-size: 14px; color: #CBD5E1; margin-bottom: 12px;'>
            <span style='color: #FBBF24; font-weight: bold;'>🔸 Datasets Masivos</span><br>
            ...
            </p>
            </div>
            """,
            "#FBBF24"
        )
        layout.addWidget(storage_card)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    def create_accuracy_tab(self):
        scroll = self.create_scroll_area()
        content = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Título
        title = QtWidgets.QLabel("Factores de Precisión y Veracidad")
        title.setFont(QtGui.QFont("Segoe UI", 24, QtGui.QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 10px;")
        layout.addWidget(title)

        # Datos de entrada
        data_card = self.create_modern_card(
            "Calidad de Datos de Entrada",
            "data_quality",
            """
            <div style='line-height: 1.8;'>
            <p style='font-size: 14px; color: #CBD5E1; margin-bottom: 12px;'>
            <span style='color: #FB7185; font-weight: bold;'>🔸 Corrección de Pares</span><br>
            • Un solo par incorrecto en 2⁴³ pares puede sesgar completamente el análisis estadístico<br>
            • <b>Tasa de error crítica:</b> ε<sub>datos</sub> debe ser &lt;&lt; ε<sub>sesgo</sub><br>
            ...
            </p>
            </div>
            """,
            "#FB7185"
        )
        layout.addWidget(data_card)

        # Tamaño de muestra
        sample_card = self.create_modern_card(
            "Suficiencia de Muestras",
            "sample_size",
            """
            <div style='line-height: 1.8;'>
            <p style='font-size: 14px; color: #CBD5E1; margin-bottom: 12px;'>
            <span style='color: #60A5FA; font-weight: bold;'>🔸 Criterios Estadísticos</span><br>
            • <b>Criptoanálisis Lineal:</b> Para confianza del 95%, N ≈ <b>4/ε²</b><br>
            ...
            </p>
            </div>
            """,
            "#60A5FA"
        )
        layout.addWidget(sample_card)

        # Precisión numérica
        precision_card = self.create_modern_card(
            "Precisión Numérica y Errores de Redondeo",
            "numerical_precision",
            """
            <div style='line-height: 1.8;'>
            <p style='font-size: 14px; color: #CBD5E1; margin-bottom: 12px;'>
            <span style='color: #C084FC; font-weight: bold;'>🔸 Aritmética de Punto Flotante</span><br>
            • Calcular probabilidades pequeñas (ε ~ 2⁻²¹) en float32:<br>
            ...
            </p>
            </div>
            """,
            "#C084FC"
        )
        layout.addWidget(precision_card)

        # Recursos y tiempo (terminado)
        resources_card = self.create_modern_card(
            "Impacto de Recursos Limitados",
            "resource_impact",
            """
            <div style='line-height: 1.8;'>
            <p style='font-size: 14px; color: #CBD5E1; margin-bottom: 12px;'>
            <span style='color: #F59E0B; font-weight: bold;'>🔸 Terminación Prematura</span><br>
            • Algoritmos iterativos (SAT solvers, Gröbner bases) pueden requerir <b>horas o días</b><br>
            • Interrumpir antes de convergencia → solución parcial o incorrecta<br>
            • <b>Indicadores de convergencia:</b> Monitorear tasa de cambio de solución<br>
            &nbsp;&nbsp;→ Si Δsolución &lt; ε<sub>threshold</sub> por k iteraciones → probablemente convergió<br>
            • Guardar checkpoints periódicos para reanudar si se interrumpe
            </p>

            <p style='font-size: 14px; color: #CBD5E1; margin-bottom: 12px;'>
            <span style='color: #F59E0B; font-weight: bold;'>🔸 Aproximaciones Agresivas</span><br>
            • Con memoria limitada: aplicar filtros y reducción de espacio de búsqueda (p. ej. Bloom filters) para descartar candidatos improbables<br>
            • Usar sampling estratificado en lugar de procesar todo el dataset a la vez<br>
            • Compensar aproximaciones con validación posterior en un conjunto pequeño y verificado
            </p>

            <p style='font-size: 14px; color: #CBD5E1; margin-bottom: 12px;'>
            <span style='color: #F59E0B; font-weight: bold;'>🔸 Checkpoints & Reintentos</span><br>
            • Implementar checkpoints al finalizar etapas clave (generación de pares, conteos estadísticos, resultados de solver)<br>
            • Registrar métricas de cada checkpoint (tiempo, uso de memoria, tasa de progreso) para análisis posterior<br>
            • Automatizar reintentos con parámetros más conservadores si un intento falla por OOM o timeouts
            </p>

            <p style='font-size: 13px; color: #94A3B8; margin-top: 15px; padding: 12px; 
               background: rgba(245, 158, 11, 0.05); border-left: 3px solid #F59E0B; border-radius: 5px;'>
            <b>✔️ Recomendación:</b> Diseñar la ejecución pensando en degradación suave: que el sistema produzca resultados parciales y guardables en vez de fallar catastróficamente.
            </p>
            </div>
            """,
            "#F59E0B"
        )
        layout.addWidget(resources_card)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    def create_modern_card(self, title, _id, html_content, accent_color="#3B82F6"):
        """
        Crea una tarjeta moderna con título y contenido HTML.
        - title: texto del título
        - _id: identificador (no usado pero reservado)
        - html_content: contenido en HTML (string)
        - accent_color: color principal de la tarjeta (hex)
        """
        card = QtWidgets.QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: rgba(255,255,255,0.02);
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.03);
            }}
        """)
        v = QtWidgets.QVBoxLayout(card)
        v.setContentsMargins(18, 14, 18, 14)
        v.setSpacing(10)

        # Header (icon + title)
        header = QtWidgets.QHBoxLayout()
        dot = QtWidgets.QFrame()
        dot.setFixedSize(12, 12)
        dot.setStyleSheet(f"background: {accent_color}; border-radius: 6px;")
        header.addWidget(dot, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)

        title_lbl = QtWidgets.QLabel(title)
        title_lbl.setFont(QtGui.QFont("Segoe UI", 16, QtGui.QFont.Weight.DemiBold))
        title_lbl.setStyleSheet("color: white; margin-left: 10px;")
        header.addWidget(title_lbl)
        header.addStretch()
        v.addLayout(header)

        # Content (HTML)
        content_lbl = QtWidgets.QLabel()
        content_lbl.setTextFormat(QtCore.Qt.TextFormat.RichText)
        content_lbl.setText(html_content)
        content_lbl.setWordWrap(True)
        content_lbl.setOpenExternalLinks(True)
        content_lbl.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextSelectableByMouse |
            QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        # body style (smaller text, relaxed spacing)
        content_lbl.setStyleSheet("""
            QLabel {
                color: #CBD5E1;
                font-size: 13px;
            }
        """)
        v.addWidget(content_lbl)

        return card

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = InformationWindow()
    window.show()
    sys.exit(app.exec())
