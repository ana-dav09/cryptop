import os
import sys
import json
import subprocess
import csv
from fractions import Fraction

from PyQt6 import QtWidgets, QtGui, QtCore

# Agregar paths necesarios
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

try:
    from export_pdf import ExportPdf
except ImportError:
    ExportPdf = None

try:
    from barra_lateral import SidebarWidget
except Exception:
    SidebarWidget = None


# =============================================================================
# PANTALLA 1: SELECCIÓN DE ATAQUE S-DES
# =============================================================================
class SDESAttackSelectionScreen(QtWidgets.QWidget):
    """Pantalla inicial para configurar parámetros generales y elegir tipo de ataque"""
    
    attack_selected = QtCore.pyqtSignal(str)  # "linear", "differential", "bruteforce"
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        # Header
        header = QtWidgets.QLabel("Configuración del Ataque S-DES")
        header.setFont(QtGui.QFont("Segoe UI", 22, QtGui.QFont.Weight.Bold))
        header.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #0f172a; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Info de S-DES
        info = QtWidgets.QLabel("Simplified Data Encryption Standard (10-bit key, 2 rounds)")
        info.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #64748b; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(info)
        
        # Parámetros generales
        params_box = QtWidgets.QGroupBox("Parámetros Generales")
        params_box.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 16px;
                margin-top: 16px;
                font-weight: 600;
                font-size: 15px;
                padding: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: #0f172a;
            }
        """)
        
        form = QtWidgets.QFormLayout()
        form.setSpacing(16)
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        
        self.pairsSpin = QtWidgets.QSpinBox()
        self.pairsSpin.setRange(100, 50000)
        self.pairsSpin.setSingleStep(500)
        self.pairsSpin.setValue(5000)
        self.pairsSpin.setMinimumWidth(200)
        
        label_pairs = QtWidgets.QLabel("Número de pares:")
        label_pairs.setStyleSheet("font-size: 14px; color: #334155;")
        
        form.addRow(label_pairs, self.pairsSpin)
        
        params_box.setLayout(form)
        layout.addWidget(params_box)
        
        # Espacio
        layout.addSpacing(20)
        
        # Selección de tipo de ataque
        attack_label = QtWidgets.QLabel("Seleccione el tipo de ataque:")
        attack_label.setFont(QtGui.QFont("Segoe UI", 16, QtGui.QFont.Weight.DemiBold))
        attack_label.setStyleSheet("color: #1e293b; margin-top: 10px;")
        attack_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(attack_label)
        
        # Botones de ataque (tarjetas grandes)
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        self.linear_card = self._create_attack_card(
            "🔶 Lineal",
            "Aproximaciones lineales de las S-boxes",
            "#8b5cf6",
            available=True
        )
        self.diff_card = self._create_attack_card(
            "🔷 Diferencial",
            "Análisis de diferencias en pares",
            "#3b82f6",
            available=False
        )
        self.brute_card = self._create_attack_card(
            "🔸 Fuerza Bruta",
            "Búsqueda exhaustiva (2¹⁰ claves)",
            "#ec4899",
            available=False
        )
        
        buttons_layout.addWidget(self.linear_card)
        buttons_layout.addWidget(self.diff_card)
        buttons_layout.addWidget(self.brute_card)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        # Conectar señales
        self.linear_card.clicked.connect(lambda: self.attack_selected.emit("linear"))
        self.diff_card.clicked.connect(lambda: self._show_not_available("Diferencial"))
        self.brute_card.clicked.connect(lambda: self._show_not_available("Fuerza Bruta"))
    
    def _create_attack_card(self, title: str, description: str, color: str, available: bool = True):
        """Crea una tarjeta clickeable para cada tipo de ataque"""
        card = QtWidgets.QPushButton()
        card.setMinimumHeight(180)
        card.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor if available else QtCore.Qt.CursorShape.ForbiddenCursor))
        
        # Layout interno
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(24, 24, 24, 24)
        
        # Título
        title_label = QtWidgets.QLabel(title)
        title_label.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Weight.Bold))
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        
        # Descripción
        desc_label = QtWidgets.QLabel(description)
        desc_label.setFont(QtGui.QFont("Segoe UI", 12))
        desc_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #64748b;")
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(desc_label)
        
        # Badge de disponibilidad
        if not available:
            badge = QtWidgets.QLabel("🔒 Próximamente")
            badge.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Weight.Bold))
            badge.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            badge.setStyleSheet("color: #94a3b8; margin-top: 8px;")
            card_layout.addWidget(badge)
        
        card_layout.addStretch()
        
        if available:
            card.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    border: 3px solid {color};
                    border-radius: 16px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    color: white;
                }}
                QPushButton:hover QLabel {{
                    color: white !important;
                }}
            """)
        else:
            card.setStyleSheet(f"""
                QPushButton {{
                    background-color: #f8fafc;
                    border: 3px solid #cbd5e1;
                    border-radius: 16px;
                    text-align: center;
                    opacity: 0.6;
                }}
            """)
        
        return card
    
    def _show_not_available(self, attack_name: str):
        """Muestra mensaje de ataque no disponible"""
        QtWidgets.QMessageBox.information(
            self,
            "Ataque no disponible",
            f"El ataque {attack_name} aún no está implementado.\n\n"
            "Por favor, seleccione el Ataque Lineal."
        )
    
    def get_params(self):
        """Retorna los parámetros generales configurados"""
        return {
            "pairs": self.pairsSpin.value()
        }


# =============================================================================
# PANTALLA 2: CONFIGURACIÓN ESPECÍFICA (LINEAL)
# =============================================================================
class SDESLinearConfigScreen(QtWidgets.QWidget):
    """Configuración específica para ataque lineal S-DES"""
    
    execute_attack = QtCore.pyqtSignal(dict)
    go_back = QtCore.pyqtSignal()
    
    def __init__(self, general_params: dict):
        super().__init__()
        self.general_params = general_params
        self._init_ui()
    
    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Header
        header = QtWidgets.QLabel("⚙️ Configuración: Ataque Lineal S-DES")
        header.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Weight.Bold))
        header.setStyleSheet("color: #0f172a;")
        layout.addWidget(header)
        
        # Info general
        info_text = f"Pares: {self.general_params['pairs']} | S-DES: 10-bit key, 2 rounds"
        info_label = QtWidgets.QLabel(info_text)
        info_label.setStyleSheet("color: #64748b; font-size: 13px;")
        layout.addWidget(info_label)
        
        # Parámetros específicos
        params_box = QtWidgets.QGroupBox("Parámetros del Ataque Lineal")
        params_box.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
                padding: 20px;
                font-weight: 600;
            }
        """)
        form = QtWidgets.QFormLayout()
        form.setSpacing(16)
        
        self.topApproxSpin = QtWidgets.QSpinBox()
        self.topApproxSpin.setRange(1, 15)
        self.topApproxSpin.setValue(6)
        self.topApproxSpin.setToolTip("Número de mejores aproximaciones por S-box a considerar")
        
        self.topCandidatesSpin = QtWidgets.QSpinBox()
        self.topCandidatesSpin.setRange(1, 16)
        self.topCandidatesSpin.setValue(8)
        self.topCandidatesSpin.setToolTip("Top candidatos de cada S-box a combinar para encontrar subkey2")
        
        form.addRow("Aproximaciones por S-box:", self.topApproxSpin)
        form.addRow("Top candidatos a combinar:", self.topCandidatesSpin)
        
        # Info adicional
        info_widget = QtWidgets.QLabel(
            "ℹ️ El ataque lineal en S-DES explota las aproximaciones lineales "
            "de las dos S-boxes (S0 y S1) para recuperar bits de la subkey2 (8 bits)."
        )
        info_widget.setWordWrap(True)
        info_widget.setStyleSheet("""
            QLabel {
                background-color: #eff6ff;
                border: 1px solid #bfdbfe;
                border-radius: 8px;
                padding: 12px;
                color: #1e40af;
                font-size: 12px;
            }
        """)
        form.addRow(info_widget)
        
        params_box.setLayout(form)
        layout.addWidget(params_box)
        
        layout.addStretch()
        
        # Botones
        btn_layout = QtWidgets.QHBoxLayout()
        
        self.back_btn = QtWidgets.QPushButton("← Volver")
        self.execute_btn = QtWidgets.QPushButton("▶ Ejecutar Ataque")
        
        self.back_btn.setFixedHeight(44)
        self.execute_btn.setFixedHeight(44)
        
        self.back_btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.execute_btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #64748b;
                color: white;
                border-radius: 10px;
                font-weight: 600;
                padding: 10px 24px;
            }
            QPushButton:hover { background-color: #475569; }
        """)
        
        self.execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border-radius: 10px;
                font-weight: 600;
                padding: 10px 24px;
                font-size: 15px;
            }
            QPushButton:hover { background-color: #7c3aed; }
        """)
        
        btn_layout.addWidget(self.back_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.execute_btn)
        
        layout.addLayout(btn_layout)
        
        # Conectar señales
        self.back_btn.clicked.connect(self.go_back.emit)
        self.execute_btn.clicked.connect(self._on_execute)
    
    def _on_execute(self):
        """Recolecta todos los parámetros y emite señal"""
        params = {
            **self.general_params,
            "top_approx": self.topApproxSpin.value(),
            "top_candidates": self.topCandidatesSpin.value()
        }
        self.execute_attack.emit(params)


# =============================================================================
# PANTALLA 3: RESULTADOS
# =============================================================================
class SDESResultsScreen(QtWidgets.QWidget):
    """Pantalla de resultados del ataque S-DES"""
    
    new_attack = QtCore.pyqtSignal()
    export_pdf = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.last_summary = None
        self.attack_type = None
        self.output_dir = None
        self._init_ui()
    
    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header con botones
        header_layout = QtWidgets.QHBoxLayout()
        
        self.title_label = QtWidgets.QLabel("📊 Resultados del Ataque S-DES")
        self.title_label.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #0f172a;")
        
        self.new_attack_btn = QtWidgets.QPushButton("🔄 Nuevo Ataque")
        self.export_btn = QtWidgets.QPushButton("📄 Exportar PDF")
        
        for btn in [self.new_attack_btn, self.export_btn]:
            btn.setFixedHeight(38)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        self.new_attack_btn.setStyleSheet("""
            QPushButton {
                background-color: #64748b;
                color: white;
                border-radius: 8px;
                font-weight: 600;
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: #475569; }
        """)
        
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border-radius: 8px;
                font-weight: 600;
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: #27AE60; }
        """)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.new_attack_btn)
        header_layout.addWidget(self.export_btn)
        
        layout.addLayout(header_layout)
        
        # Splitter horizontal
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        
        # Panel izquierdo: Tablas LAT
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        left_layout.setSpacing(8)
        
        self.lat_tabs = QtWidgets.QTabWidget()
        
        # S0 Tables
        s0_widget = QtWidgets.QWidget()
        s0_layout = QtWidgets.QVBoxLayout(s0_widget)
        
        self.s0_agreement_table = QtWidgets.QTableWidget()
        self.s0_correlation_table = QtWidgets.QTableWidget()
        
        self._style_table(self.s0_agreement_table)
        self._style_table(self.s0_correlation_table)
        
        s0_layout.addWidget(QtWidgets.QLabel("Tabla de Acuerdo (LAT)"))
        s0_layout.addWidget(self.s0_agreement_table)
        s0_layout.addWidget(QtWidgets.QLabel("Correlaciones"))
        s0_layout.addWidget(self.s0_correlation_table)
        
        # S1 Tables
        s1_widget = QtWidgets.QWidget()
        s1_layout = QtWidgets.QVBoxLayout(s1_widget)
        
        self.s1_agreement_table = QtWidgets.QTableWidget()
        self.s1_correlation_table = QtWidgets.QTableWidget()
        
        self._style_table(self.s1_agreement_table)
        self._style_table(self.s1_correlation_table)
        
        s1_layout.addWidget(QtWidgets.QLabel("Tabla de Acuerdo (LAT)"))
        s1_layout.addWidget(self.s1_agreement_table)
        s1_layout.addWidget(QtWidgets.QLabel("Correlaciones"))
        s1_layout.addWidget(self.s1_correlation_table)
        
        self.lat_tabs.addTab(s0_widget, "S-box 0")
        self.lat_tabs.addTab(s1_widget, "S-box 1")
        
        left_layout.addWidget(self.lat_tabs)
        splitter.addWidget(left_widget)
        
        # Panel derecho: Candidatos y resumen
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setSpacing(12)
        
        # Resumen
        summary_label = QtWidgets.QLabel("Resumen del Ataque")
        summary_label.setStyleSheet("font-weight: 600; color: #334155; font-size: 14px;")
        
        self.summaryBox = QtWidgets.QTextEdit()
        self.summaryBox.setReadOnly(True)
        self.summaryBox.setMaximumHeight(200)
        self.summaryBox.setStyleSheet("""
            QTextEdit {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        
        # Tabs para candidatos
        candidates_tabs = QtWidgets.QTabWidget()
        
        self.s0_candidates_table = QtWidgets.QTableWidget()
        self.s0_candidates_table.setColumnCount(4)
        self.s0_candidates_table.setHorizontalHeaderLabels(["k4 (4 bits)", "Desviación", "Count=0", "N"])
        self._style_table(self.s0_candidates_table)
        
        self.s1_candidates_table = QtWidgets.QTableWidget()
        self.s1_candidates_table.setColumnCount(4)
        self.s1_candidates_table.setHorizontalHeaderLabels(["k4 (4 bits)", "Desviación", "Count=0", "N"])
        self._style_table(self.s1_candidates_table)
        
        candidates_tabs.addTab(self.s0_candidates_table, "Candidatos S0")
        candidates_tabs.addTab(self.s1_candidates_table, "Candidatos S1")
        
        candidates_label = QtWidgets.QLabel("Candidatos por S-box")
        candidates_label.setStyleSheet("font-weight: 600; color: #334155; font-size: 14px;")
        
        right_layout.addWidget(summary_label)
        right_layout.addWidget(self.summaryBox)
        right_layout.addWidget(candidates_label)
        right_layout.addWidget(candidates_tabs)
        
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
        # Barra de progreso
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #e2e8f0;
                border: none;
                border-radius: 6px;
                height: 12px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #8b5cf6;
                border-radius: 6px;
            }
        """)
        
        self.status_label = QtWidgets.QLabel("Listo")
        self.status_label.setStyleSheet("color: #64748b; font-size: 13px;")
        
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(self.status_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.progress)
        
        layout.addLayout(bottom_layout)
        
        # Conectar señales
        self.new_attack_btn.clicked.connect(self.new_attack.emit)
        self.export_btn.clicked.connect(self.export_pdf.emit)
    
    def _style_table(self, table):
        """Aplica estilos a una tabla"""
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #cbd5e1;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            }
            QHeaderView::section {
                background-color: #f1f5f9;
                padding: 8px;
                border: none;
                font-weight: 600;
                color: #334155;
            }
        """)
    
    def set_attack_type(self, attack_type: str):
        """Actualiza el título según el tipo de ataque"""
        self.attack_type = attack_type
        titles = {
            "linear": "📊 Resultados: Ataque Lineal S-DES"
        }
        self.title_label.setText(titles.get(attack_type, "📊 Resultados del Ataque S-DES"))
    
    def show_progress(self, message: str):
        """Muestra barra de progreso"""
        self.status_label.setText(message)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
    
    def hide_progress(self):
        """Oculta barra de progreso"""
        self.progress.setVisible(False)
        self.progress.setRange(0, 100)
    
    def load_linear_results(self, output_dir: str):
        """Carga resultados del ataque lineal S-DES"""
        try:
            self.output_dir = output_dir
            
            # Convertir ruta WSL a Windows si es necesario
            output_dir_windows = output_dir.replace("/mnt/c/", "C:/").replace("/mnt/", "")
            
            # Cargar summary JSON
            summary_path = os.path.join(output_dir_windows, "linear_attack_summary.json")
            if os.path.exists(summary_path):
                with open(summary_path, 'r', encoding='utf-8') as f:
                    self.last_summary = json.load(f)
                
                # Mostrar resumen
                summary_text = (
                    f"=== ATAQUE LINEAL S-DES ===\n\n"
                    f"Pares utilizados: {self.last_summary.get('pairs_used', 'N/A')}\n"
                    f"Clave real (10 bits): {self.last_summary.get('random_key', 'N/A')}\n"
                    f"Subkey2 real (8 bits): {self.last_summary.get('subkey2_real', 'N/A')}\n"
                    f"Subkey2 recuperada: {self.last_summary.get('subkey2_best_guess', 'N/A')}\n"
                    f"Score: {self.last_summary.get('best_guess_score', 'N/A')}\n\n"
                    f"S0: α={self.last_summary.get('s0_best_alpha', 'N/A')} "
                    f"β={self.last_summary.get('s0_best_beta', 'N/A')} LAT={self.last_summary.get('s0_lat', 'N/A')}\n"
                    f"S1: α={self.last_summary.get('s1_best_alpha', 'N/A')} "
                    f"β={self.last_summary.get('s1_best_beta', 'N/A')} LAT={self.last_summary.get('s1_lat', 'N/A')}"
                )
                self.summaryBox.setText(summary_text)
                
                # Cargar candidatos
                self._load_sbox_candidates(
                    self.last_summary.get('s0_top_candidates', []),
                    self.s0_candidates_table
                )
                self._load_sbox_candidates(
                    self.last_summary.get('s1_top_candidates', []),
                    self.s1_candidates_table
                )
            
            # Cargar tablas LAT
            self._load_lat_table(
                os.path.join(output_dir_windows, "s0_agreement.csv"),
                self.s0_agreement_table
            )
            self._load_lat_table(
                os.path.join(output_dir_windows, "s0_correlation.csv"),
                self.s0_correlation_table
            )
            self._load_lat_table(
                os.path.join(output_dir_windows, "s1_agreement.csv"),
                self.s1_agreement_table
            )
            self._load_lat_table(
                os.path.join(output_dir_windows, "s1_correlation.csv"),
                self.s1_correlation_table
            )
            
            self.status_label.setText("Ataque completado exitosamente")
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self,
                "Advertencia",
                f"Error cargando algunos resultados:\n{str(e)}"
            )
    
    def _load_sbox_candidates(self, candidates, table_widget):
        """Llena tabla de candidatos de S-box"""
        table_widget.setRowCount(len(candidates))
        for row, cand in enumerate(candidates):
            table_widget.setItem(row, 0, QtWidgets.QTableWidgetItem(cand.get('k4', '')))
            table_widget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(cand.get('deviation', ''))))
            table_widget.setItem(row, 2, QtWidgets.QTableWidgetItem(str(cand.get('count_zero', ''))))
            table_widget.setItem(row, 3, QtWidgets.QTableWidgetItem(str(cand.get('N', ''))))
        table_widget.resizeColumnsToContents()
    
    def _load_lat_table(self, csv_path, table_widget):
        """Carga una matriz LAT desde CSV"""
        if not os.path.exists(csv_path):
            return
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            if len(rows) < 2:
                return
            
            # Convertir a matriz
            data = {}
            for row in rows[1:]:
                if len(row) < 3:
                    continue
                alpha, beta, val = row[0], row[1], row[2]
                if alpha not in data:
                    data[alpha] = {}
                data[alpha][beta] = val
            
            alphas = sorted(data.keys())
            if not alphas:
                return
            betas = sorted(data[alphas[0]].keys())
            
            table_widget.setRowCount(len(alphas))
            table_widget.setColumnCount(len(betas))
            table_widget.setHorizontalHeaderLabels([f"β={b}" for b in betas])
            table_widget.setVerticalHeaderLabels([f"α={a}" for a in alphas])
            
            for i, alpha in enumerate(alphas):
                for j, beta in enumerate(betas):
                    val = data[alpha].get(beta, '0')
                    try:
                        frac_val = Fraction(float(val)).limit_denominator(100)
                        item = QtWidgets.QTableWidgetItem(str(frac_val))
                    except:
                        item = QtWidgets.QTableWidgetItem(val)
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    table_widget.setItem(i, j, item)
            
            table_widget.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error cargando {csv_path}:", e)


# =============================================================================
# VENTANA PRINCIPAL CON STACKED WIDGET
# =============================================================================
class SDESAttackWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD - Ataques en S-DES")
        self.resize(1400, 850)
        
        # Rutas de scripts
        self.SCRIPT_DIR = "/mnt/c/Users/hp/Desktop/diseno/integracion"
        self.SDES_LINEAR_SCRIPT = "/mnt/c/Users/hp/Desktop/diseno/integracion/sdes_lineal.py"
        self.OUTPUT_DIR = "/mnt/c/Users/hp/Desktop/diseno/integracion/sdes_linear_outputs"
        
        self._init_ui()
        self._apply_styles()
    
    def _init_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar (opcional)
        if SidebarWidget:
            self.sidebar = SidebarWidget(self)
            main_layout.addWidget(self.sidebar)
        
        # Stacked Widget para las pantallas
        self.stacked = QtWidgets.QStackedWidget()
        
        # Crear las pantallas
        self.selection_screen = SDESAttackSelectionScreen()
        self.results_screen = SDESResultsScreen()
        
        # Agregar al stack
        self.stacked.addWidget(self.selection_screen)  # Index 0
        self.stacked.addWidget(self.results_screen)     # Index 1
        
        main_layout.addWidget(self.stacked, stretch=1)
        
        # Conectar señales de pantalla de selección
        self.selection_screen.attack_selected.connect(self._on_attack_selected)
        
        # Conectar señales de pantalla de resultados
        self.results_screen.new_attack.connect(self._on_new_attack)
        self.results_screen.export_pdf.connect(self._on_export_pdf)
    
    def _on_attack_selected(self, attack_type: str):
        """Maneja la selección de tipo de ataque"""
        general_params = self.selection_screen.get_params()
        
        # Crear pantalla de configuración específica
        if attack_type == "linear":
            config_screen = SDESLinearConfigScreen(general_params)
        else:
            return
        
        # Conectar señales
        config_screen.go_back.connect(self._on_config_back)
        config_screen.execute_attack.connect(lambda params: self._execute_attack(attack_type, params))
        
        # Agregar al stack y mostrar
        self.stacked.addWidget(config_screen)
        self.stacked.setCurrentWidget(config_screen)
    
    def _on_config_back(self):
        """Volver a la pantalla de selección"""
        # Remover la pantalla de configuración actual
        current = self.stacked.currentWidget()
        if current not in [self.selection_screen, self.results_screen]:
            self.stacked.removeWidget(current)
            current.deleteLater()
        
        # Mostrar pantalla de selección
        self.stacked.setCurrentWidget(self.selection_screen)
    
    def _execute_attack(self, attack_type: str, params: dict):
        """Ejecuta el ataque según el tipo"""
        # Ir a pantalla de resultados
        self.results_screen.set_attack_type(attack_type)
        self.stacked.setCurrentWidget(self.results_screen)
        self.results_screen.show_progress("Ejecutando ataque lineal S-DES... (puede tardar)")
        
        # Ejecutar según tipo
        if attack_type == "linear":
            self._run_linear_attack(params)
    
    def _run_linear_attack(self, params: dict):
        """Ejecuta ataque lineal S-DES"""
        sage_path = "/usr/bin/sage"
        script_path = self.SDES_LINEAR_SCRIPT
        
        try:
            # Ejecutar con WSL
            result = subprocess.run(
                ["wsl", "-d", "debian", "bash", "-lc", 
                 f"cd {self.SCRIPT_DIR} && {sage_path} -python {script_path}"],
                capture_output=True,
                text=True
            )
            
            self.results_screen.hide_progress()
            
            if result.returncode != 0:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    f"Error ejecutando Sage:\n{result.stderr}"
                )
                self.results_screen.status_label.setText("Error en ejecución")
                return
            
            # Cargar resultados
            self.results_screen.load_linear_results(self.OUTPUT_DIR)
            
        except Exception as e:
            self.results_screen.hide_progress()
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Error ejecutando ataque:\n{str(e)}"
            )
            self.results_screen.status_label.setText("Error")
    
    def _on_new_attack(self):
        """Reinicia el flujo para un nuevo ataque"""
        # Limpiar pantallas de configuración dinámicas
        while self.stacked.count() > 2:
            widget = self.stacked.widget(2)
            self.stacked.removeWidget(widget)
            widget.deleteLater()
        
        # Volver a selección
        self.stacked.setCurrentWidget(self.selection_screen)
    
    def _on_export_pdf(self):
        """Exporta resultados a PDF"""
        if not ExportPdf:
            QtWidgets.QMessageBox.warning(
                self,
                "Módulo no disponible",
                "El módulo export_pdf no está disponible.\n"
                "Asegúrate de tener reportlab instalado."
            )
            return
        
        if not self.results_screen.last_summary:
            QtWidgets.QMessageBox.warning(
                self,
                "Sin datos",
                "No hay resultados para exportar."
            )
            return
        
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Guardar reporte PDF",
            "resultados_ataque_sdes.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not filename:
            return
        
        try:
            pdf = ExportPdf()
            
            # Preparar metadata
            summary = self.results_screen.last_summary
            metadata = {
                "Algoritmo": "Simplified DES (S-DES)",
                "Tipo de ataque": "Lineal",
                "Número de rondas": "2",
                "Pares usados": str(summary.get('pairs_used', 'N/A')),
                "Clave real (10 bits)": summary.get('random_key', 'N/A'),
                "Subkey2 real (8 bits)": summary.get('subkey2_real', 'N/A'),
                "Subkey2 recuperada": summary.get('subkey2_best_guess', 'N/A'),
                "Score": str(summary.get('best_guess_score', 'N/A')),
                "S0 aproximación": f"α={summary.get('s0_best_alpha', 'N/A')} β={summary.get('s0_best_beta', 'N/A')} LAT={summary.get('s0_lat', 'N/A')}",
                "S1 aproximación": f"α={summary.get('s1_best_alpha', 'N/A')} β={summary.get('s1_best_beta', 'N/A')} LAT={summary.get('s1_lat', 'N/A')}"
            }
            
            # Tablas LAT
            lat_tables = [
                self.results_screen.s0_correlation_table,
                self.results_screen.s1_correlation_table
            ]
            
            # Tablas de candidatos
            candidate_tables = [
                self.results_screen.s0_candidates_table,
                self.results_screen.s1_candidates_table
            ]
            
            # Exportar
            pdf.export(filename, lat_tables, candidate_tables, metadata)
            
            QtWidgets.QMessageBox.information(
                self,
                "Exportación exitosa",
                f"El reporte se guardó en:\n{filename}"
            )
            
            self.results_screen.status_label.setText(f"PDF exportado: {os.path.basename(filename)}")
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Error al exportar PDF:\n{str(e)}"
            )
    
    def _apply_styles(self):
        """Aplica estilos globales"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f9fafb;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #1e293b;
            }
            
            QGroupBox {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
                font-weight: 600;
                padding: 16px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: #0f172a;
                font-size: 14px;
            }
            
            QLabel {
                color: #334155;
                font-size: 14px;
            }
            
            QLineEdit, QSpinBox, QComboBox {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                min-height: 24px;
            }
            
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 2px solid #8b5cf6;
                outline: none;
            }
            
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
            }
            
            QTabBar::tab {
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #8b5cf6;
                font-weight: 600;
            }
            
            QTabBar::tab:hover {
                background-color: #e0e7ff;
            }
        """)


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SDESAttackWindow()
    window.show()
    sys.exit(app.exec())