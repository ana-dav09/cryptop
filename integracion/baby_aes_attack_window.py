import os
import sys
import json
import subprocess
from fractions import Fraction

from PyQt6 import QtWidgets, QtGui, QtCore

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from export_pdf import ExportPdf
from helpers import SageRunner

import pandas as pd
import numpy as np

try:
    from barra_lateral import SidebarWidget
except Exception:
    SidebarWidget = None


# =============================================================================
# PANTALLA 1: SELECCIÓN DE ATAQUE
# =============================================================================
class AttackSelectionScreen(QtWidgets.QWidget):
    """Pantalla inicial para configurar parámetros generales y elegir tipo de ataque"""
    
    attack_selected = QtCore.pyqtSignal(str)  # Señal: "differential", "linear", "algebraic"
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        # Header
        header = QtWidgets.QLabel("Configuración del Ataque Baby AES")
        header.setFont(QtGui.QFont("Segoe UI", 22, QtGui.QFont.Weight.Bold))
        header.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #0f172a; margin-bottom: 20px;")
        layout.addWidget(header)
        
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
        
        self.roundsSpin = QtWidgets.QSpinBox()
        self.roundsSpin.setRange(1, 10)
        self.roundsSpin.setValue(3)
        self.roundsSpin.setMinimumWidth(200)
        
        self.pairsSpin = QtWidgets.QSpinBox()
        self.pairsSpin.setRange(100, 100000)
        self.pairsSpin.setSingleStep(500)
        self.pairsSpin.setValue(5000)
        self.pairsSpin.setMinimumWidth(200)
        
        label_rounds = QtWidgets.QLabel("Número de rondas:")
        label_rounds.setStyleSheet("font-size: 14px; color: #334155;")
        
        label_pairs = QtWidgets.QLabel("Número de pares:")
        label_pairs.setStyleSheet("font-size: 14px; color: #334155;")
        
        form.addRow(label_rounds, self.roundsSpin)
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
        
        self.diff_card = self._create_attack_card(
            "🔷 Diferencial",
            "Explota diferencias en pares de textos planos",
            "#3b82f6"
        )
        self.linear_card = self._create_attack_card(
            "🔶 Lineal",
            "Utiliza aproximaciones lineales de la S-Box",
            "#8b5cf6"
        )
        self.algebraic_card = self._create_attack_card(
            "🔸 Algebraico",
            "Resuelve sistema de ecuaciones con SAT solver",
            "#ec4899"
        )
        
        buttons_layout.addWidget(self.diff_card)
        buttons_layout.addWidget(self.linear_card)
        buttons_layout.addWidget(self.algebraic_card)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        # Conectar señales
        self.diff_card.clicked.connect(lambda: self.attack_selected.emit("differential"))
        self.linear_card.clicked.connect(lambda: self.attack_selected.emit("linear"))
        self.algebraic_card.clicked.connect(lambda: self.attack_selected.emit("algebraic"))
    
    def _create_attack_card(self, title: str, description: str, color: str):
        """Crea una tarjeta clickeable para cada tipo de ataque"""
        card = QtWidgets.QPushButton()
        card.setMinimumHeight(180)
        card.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
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
        card_layout.addStretch()
        
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
        
        return card
    
    def get_params(self):
        """Retorna los parámetros generales configurados"""
        return {
            "rounds": self.roundsSpin.value(),
            "pairs": self.pairsSpin.value()
        }


# =============================================================================
# PANTALLA 2: CONFIGURACIÓN ESPECÍFICA (LINEAL)
# =============================================================================
class LinearConfigScreen(QtWidgets.QWidget):
    """Configuración específica para ataque lineal"""
    
    execute_attack = QtCore.pyqtSignal(dict)  # Señal con parámetros completos
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
        header = QtWidgets.QLabel("⚙️ Configuración: Ataque Lineal")
        header.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Weight.Bold))
        header.setStyleSheet("color: #0f172a;")
        layout.addWidget(header)
        
        # Info general
        info_text = f"Rondas: {self.general_params['rounds']} | Pares: {self.general_params['pairs']}"
        info_label = QtWidgets.QLabel(info_text)
        info_label.setStyleSheet("color: #64748b; font-size: 13px;")
        layout.addWidget(info_label)
        
        # Parámetros específicos
        params_box = QtWidgets.QGroupBox("Parámetros del Ataque Lineal")
        form = QtWidgets.QFormLayout()
        form.setSpacing(16)
        
        self.maskEdit = QtWidgets.QLineEdit("0010,0000,0000,1000")
        self.maskEdit.setPlaceholderText("Ej: 0010,0000,0000,1000")
        
        self.topkSpin = QtWidgets.QSpinBox()
        self.topkSpin.setRange(1, 100)
        self.topkSpin.setValue(20)
        
        form.addRow("Máscara inicial (a₁):", self.maskEdit)
        form.addRow("Top-K candidatos:", self.topkSpin)
        
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
            "mask": self.maskEdit.text(),
            "topk": self.topkSpin.value()
        }
        self.execute_attack.emit(params)


# =============================================================================
# PANTALLA 2: CONFIGURACIÓN ESPECÍFICA (DIFERENCIAL)
# =============================================================================
class DifferentialConfigScreen(QtWidgets.QWidget):
    """Configuración específica para ataque diferencial"""
    
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
        header = QtWidgets.QLabel("⚙️ Configuración: Ataque Diferencial")
        header.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Weight.Bold))
        header.setStyleSheet("color: #0f172a;")
        layout.addWidget(header)
        
        # Info general
        info_text = f"Rondas: {self.general_params['rounds']} | Pares: {self.general_params['pairs']}"
        info_label = QtWidgets.QLabel(info_text)
        info_label.setStyleSheet("color: #64748b; font-size: 13px;")
        layout.addWidget(info_label)
        
        # Parámetros específicos
        params_box = QtWidgets.QGroupBox("Parámetros del Ataque Diferencial")
        form = QtWidgets.QFormLayout()
        form.setSpacing(16)
        
        self.du1Edit = QtWidgets.QLineEdit("0001,0000,0000,0001")
        self.du1Edit.setPlaceholderText("Ej: 0001,0000,0000,0001")
        
        self.du3Edit = QtWidgets.QLineEdit()
        self.du3Edit.setPlaceholderText("Dejar vacío para calcular automáticamente")
        
        form.addRow("Diferencia entrada (Δu₁):", self.du1Edit)
        form.addRow("Diferencia salida (Δu₃):", self.du3Edit)
        
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
                background-color: #3b82f6;
                color: white;
                border-radius: 10px;
                font-weight: 600;
                padding: 10px 24px;
                font-size: 15px;
            }
            QPushButton:hover { background-color: #2563eb; }
        """)
        
        btn_layout.addWidget(self.back_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.execute_btn)
        
        layout.addLayout(btn_layout)
        
        # Conectar señales
        self.back_btn.clicked.connect(self.go_back.emit)
        self.execute_btn.clicked.connect(self._on_execute)
    
    def _on_execute(self):
        params = {
            **self.general_params,
            "du1": self.du1Edit.text(),
            "du3": self.du3Edit.text() if self.du3Edit.text() else None
        }
        self.execute_attack.emit(params)


# =============================================================================
# PANTALLA 2: CONFIGURACIÓN ESPECÍFICA (ALGEBRAICO)
# =============================================================================
class AlgebraicConfigScreen(QtWidgets.QWidget):
    """Configuración específica para ataque algebraico"""
    
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
        header = QtWidgets.QLabel("⚙️ Configuración: Ataque Algebraico")
        header.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Weight.Bold))
        header.setStyleSheet("color: #0f172a;")
        layout.addWidget(header)
        
        # Info general
        info_text = f"Rondas: {self.general_params['rounds']}"
        info_label = QtWidgets.QLabel(info_text)
        info_label.setStyleSheet("color: #64748b; font-size: 13px;")
        layout.addWidget(info_label)
        
        # Parámetros específicos
        params_box = QtWidgets.QGroupBox("Parámetros del Ataque Algebraico")
        form = QtWidgets.QFormLayout()
        form.setSpacing(16)
        
        self.plaintextEdit = QtWidgets.QLineEdit()
        self.plaintextEdit.setPlaceholderText("Ej: 1234 (hexadecimal)")
        
        self.ciphertextEdit = QtWidgets.QLineEdit()
        self.ciphertextEdit.setPlaceholderText("Ej: ABCD (hexadecimal)")
        
        self.solverCombo = QtWidgets.QComboBox()
        self.solverCombo.addItems(["cryptominisat", "glucose", "lingeling"])
        
        form.addRow("Texto plano conocido:", self.plaintextEdit)
        form.addRow("Texto cifrado conocido:", self.ciphertextEdit)
        form.addRow("SAT Solver:", self.solverCombo)
        
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
                background-color: #ec4899;
                color: white;
                border-radius: 10px;
                font-weight: 600;
                padding: 10px 24px;
                font-size: 15px;
            }
            QPushButton:hover { background-color: #db2777; }
        """)
        
        btn_layout.addWidget(self.back_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.execute_btn)
        
        layout.addLayout(btn_layout)
        
        # Conectar señales
        self.back_btn.clicked.connect(self.go_back.emit)
        self.execute_btn.clicked.connect(self._on_execute)
    
    def _on_execute(self):
        params = {
            **self.general_params,
            "plaintext": self.plaintextEdit.text(),
            "ciphertext": self.ciphertextEdit.text(),
            "solver": self.solverCombo.currentText()
        }
        self.execute_attack.emit(params)


# =============================================================================
# PANTALLA 3: RESULTADOS
# =============================================================================
class ResultsScreen(QtWidgets.QWidget):
    """Pantalla de resultados del ataque"""
    
    new_attack = QtCore.pyqtSignal()
    export_pdf = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.last_attack_data = None
        self.attack_type = None
        self._init_ui()
    
    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header con botones
        header_layout = QtWidgets.QHBoxLayout()
        
        self.title_label = QtWidgets.QLabel("📊 Resultados del Ataque")
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
        
        # Contenido principal con splitter horizontal
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        
        # Panel izquierdo: Tablas/Matrices
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        left_layout.setSpacing(8)
        
        self.matrix_label = QtWidgets.QLabel("Matriz de Correlaciones")
        self.matrix_label.setStyleSheet("font-weight: 600; color: #334155;")
        
        self.count_table = QtWidgets.QTableWidget()
        self.count_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #cbd5e1;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            }
            QHeaderView::section {
                background-color: #f1f5f9;
                padding: 6px;
                border: none;
                font-weight: 600;
            }
        """)
        
        left_layout.addWidget(self.matrix_label)
        left_layout.addWidget(self.count_table)
        
        # Panel derecho: Resultados y candidatos
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setSpacing(12)
        
        # Resumen JSON
        summary_label = QtWidgets.QLabel("Resumen del Ataque")
        summary_label.setStyleSheet("font-weight: 600; color: #334155;")
        
        self.jsonBox = QtWidgets.QTextEdit()
        self.jsonBox.setReadOnly(True)
        self.jsonBox.setMaximumHeight(180)
        self.jsonBox.setStyleSheet("""
            QTextEdit {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        
        # Tabla de candidatos
        candidates_label = QtWidgets.QLabel("Top Candidatos")
        candidates_label.setStyleSheet("font-weight: 600; color: #334155;")
        
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Index", "Counter", "Key"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setStyleSheet("""
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
            }
        """)
        
        right_layout.addWidget(summary_label)
        right_layout.addWidget(self.jsonBox)
        right_layout.addWidget(candidates_label)
        right_layout.addWidget(self.table)
        
        splitter.addWidget(left_widget)
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
                background-color: #3b82f6;
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
    
    def set_attack_type(self, attack_type: str):
        """Actualiza el título según el tipo de ataque"""
        self.attack_type = attack_type
        titles = {
            "linear": "📊 Resultados: Ataque Lineal",
            "differential": "📊 Resultados: Ataque Diferencial",
            "algebraic": "📊 Resultados: Ataque Algebraico"
        }
        self.title_label.setText(titles.get(attack_type, "📊 Resultados del Ataque"))
    
    def show_progress(self, message: str):
        """Muestra barra de progreso indeterminada"""
        self.status_label.setText(message)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
    
    def hide_progress(self):
        """Oculta barra de progreso"""
        self.progress.setVisible(False)
        self.progress.setRange(0, 100)
    
    def load_linear_results(self, json_path: str):
        """Carga resultados del ataque lineal"""
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.last_attack_data = data
            
            # Resumen JSON
            best_key_str = " ".join(data["best_key"])
            corr = data["correlation"]
            top_count = data["top_count"]
            
            summary = (
                f"Máscara inicial (a₁): {', '.join(data['a1'])}\n"
                f"Máscara final (a₃): {', '.join(data['a3'])}\n"
                f"Correlación: {corr:.4f}\n"
                f"Mejor llave: {best_key_str}\n"
                f"Apariciones: {top_count}"
            )
            self.jsonBox.setText(summary)
            
            # Tabla de candidatos
            top_candidates = data.get("top_candidates", [])
            self.table.setRowCount(len(top_candidates))
            for row_idx, candidate in enumerate(top_candidates):
                self.table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(candidate["index"])))
                self.table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(str(candidate["counter"])))
                key_str = " ".join(candidate["key"])
                self.table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(key_str))
            
            self.table.resizeColumnsToContents()
            
            # Cargar matriz de correlaciones
            base_dir = os.path.dirname(json_path)
            corr_path = os.path.join(base_dir, "corr_matrix.csv")
            if os.path.exists(corr_path):
                self._load_correlation_matrix(corr_path)
            
            self.status_label.setText("Ataque completado exitosamente")
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error cargando resultados:\n{str(e)}")
    
    def _load_correlation_matrix(self, path: str):
        """Carga matriz de correlaciones desde CSV"""
        try:
            matrix = np.loadtxt(path, delimiter=",")
            rows, cols = matrix.shape
            
            self.count_table.setRowCount(rows)
            self.count_table.setColumnCount(cols)
            self.count_table.setHorizontalHeaderLabels([f"b{j}" for j in range(cols)])
            self.count_table.setVerticalHeaderLabels([f"a{i}" for i in range(rows)])
            
            for i in range(rows):
                for j in range(cols):
                    item = QtWidgets.QTableWidgetItem(f"{Fraction(matrix[i,j])}")
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    self.count_table.setItem(i, j, item)
            
            self.count_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error cargando matriz de correlación: {e}")
    
    def _load_ddt_matrix(self, path: str):
        """Carga DDT (Difference Distribution Table) desde CSV"""
        try:
            matrix = np.loadtxt(path, delimiter=",")
            rows, cols = matrix.shape
            
            self.count_table.setRowCount(rows)
            self.count_table.setColumnCount(cols)
            self.count_table.setHorizontalHeaderLabels([f"Δy={j:X}" for j in range(cols)])
            self.count_table.setVerticalHeaderLabels([f"Δx={i:X}" for i in range(rows)])
            
            for i in range(rows):
                for j in range(cols):
                    val = int(matrix[i, j])
                    item = QtWidgets.QTableWidgetItem(str(val))
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    
                    # Colorear celdas con valores altos (diferenciales probables)
                    if val > 8:  # Mayor a 50% de probabilidad
                        item.setBackground(QtGui.QColor("#fee2e2"))  # Rojo suave
                    elif val > 4:
                        item.setBackground(QtGui.QColor("#fef3c7"))  # Amarillo suave
                    
                    self.count_table.setItem(i, j, item)
            
            self.count_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error cargando DDT: {e}")
    
    def load_differential_results(self, json_path: str):
        """Carga resultados del ataque diferencial"""
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.last_attack_data = data
            
            # Resumen
            summary = (
                f"Diferencia entrada (Δu₁): {data.get('du1', 'N/A')}\n"
                f"Diferencia salida (Δu₃): {data.get('du3', 'N/A')}\n"
                f"Ratio de propagación: {data.get('ratio', 'N/A')}\n"
                f"Mejor llave parcial: {data.get('best_key', 'N/A')}\n"
                f"Apariciones: {data.get('top_count', 'N/A')}"
            )
            self.jsonBox.setText(summary)
            
            # Tabla de candidatos
            top_candidates = data.get("top_candidates", [])
            self.table.setRowCount(len(top_candidates))
            for row_idx, candidate in enumerate(top_candidates):
                self.table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(candidate["index"])))
                self.table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(str(candidate["counter"])))
                self.table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(candidate["key"]))
                self.table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(str(candidate["key_binary_compact"])))
                self.table.setItem(row_idx, 4, QtWidgets.QTableWidgetItem(str(candidate["key_binary_spaced"])))
            self.table.resizeColumnsToContents()
            
            # Cargar DDT (Tabla de Distribución de Diferencias)
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            ddt_path = os.path.join(BASE_DIR, "ddt_matrix.csv")
            if os.path.exists(ddt_path):
                self.matrix_label.setText("Tabla de Distribución de Diferencias (DDT)")
                self._load_ddt_matrix(ddt_path)
            
            self.status_label.setText("Ataque diferencial completado")
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error cargando resultados:\n{str(e)}")
    
    def load_algebraic_results(self, data: dict):
        """Carga resultados del ataque algebraico"""
        self.last_attack_data = data
        
        summary = (
            f"Texto plano: {data.get('plaintext', 'N/A')}\n"
            f"Texto cifrado: {data.get('ciphertext', 'N/A')}\n"
            f"Llave recuperada: 0x{data.get('key', 'N/A')}\n"
            f"Tiempo de ejecución: {data.get('time', 'N/A')} segundos\n"
            f"SAT Solver: {data.get('solver', 'N/A')}"
        )
        self.jsonBox.setText(summary)
        self.status_label.setText("Ataque algebraico completado")


# =============================================================================
# VENTANA PRINCIPAL CON STACKED WIDGET
# =============================================================================
class AttackWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD - Ataques en BabyAES")
        self.resize(1200, 780)
        
        # Rutas de scripts
        self.SCRIPT_DIR = "/mnt/c/Users/hp/Desktop/diseno/integracion"
        self.DIFF_SCRIPT = "/mnt/c/Users/hp/Desktop/diseno/integracion/baby_aes_attack.py"
        self.LINEAR_SCRIPT = "/mnt/c/Users/hp/Desktop/diseno/integracion/baby_aes_linear_attack.py"
        self.ALGEBRAIC_SCRIPT = "/mnt/c/Users/hp/Desktop/diseno/integracion/baby_aes_algebraic_attack.sage"
        
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
        self.selection_screen = AttackSelectionScreen()
        self.results_screen = ResultsScreen()
        
        # Agregar al stack
        self.stacked.addWidget(self.selection_screen)  # Index 0
        self.stacked.addWidget(self.results_screen)     # Index 1
        # Indices 2, 3, 4 serán para config screens (se crean dinámicamente)
        
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
            config_screen = LinearConfigScreen(general_params)
        elif attack_type == "differential":
            config_screen = DifferentialConfigScreen(general_params)
        elif attack_type == "algebraic":
            config_screen = AlgebraicConfigScreen(general_params)
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
        self.results_screen.show_progress("Ejecutando ataque... (esto puede tardar)")
        
        # Ejecutar según tipo
        if attack_type == "linear":
            self._run_linear_attack(params)
        elif attack_type == "differential":
            self._run_differential_attack(params)
        elif attack_type == "algebraic":
            self._run_algebraic_attack(params)
    
    def _run_linear_attack(self, params: dict):
        """Ejecuta ataque lineal"""
        sage_path = "/usr/bin/sage"
        script_path = self.LINEAR_SCRIPT
        
        try:
            result = subprocess.run(
                [
                    "wsl", "-d", "debian", "bash", "-lc",
                    f"cd {self.SCRIPT_DIR} && {sage_path} -python {script_path} "
                    f"--rounds {params['rounds']} --pairs {params['pairs']} "
                    f"--mask {params['mask']} --topk {params['topk']}"
                ],
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
                self.results_screen.status_label.setText("Error en la ejecución")
                return
            
            # Cargar resultados
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(BASE_DIR, "linear_attack_result.json")
            self.results_screen.load_linear_results(json_path)
            
        except Exception as e:
            self.results_screen.hide_progress()
            QtWidgets.QMessageBox.critical(self, "Error", f"Error ejecutando ataque:\n{str(e)}")
            self.results_screen.status_label.setText("Error")
    
    def _run_differential_attack(self, params: dict):
        """Ejecuta ataque diferencial"""
        sage_path = "/usr/bin/sage"
        script_path = self.DIFF_SCRIPT
        
        try:
            cmd_parts = [f"cd {self.SCRIPT_DIR} && {sage_path} -python {script_path}"]
            
            # Agregar parámetros
            cmd_parts[0] += f" --rounds {params['rounds']}"
            if params.get("du1"):
                cmd_parts[0] += f" --du1 {params['du1']}"
            
            result = subprocess.run(
                ["wsl", "-d", "debian", "bash", "-lc", cmd_parts[0]],
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
                return
            
            # Cargar resultados desde JSON
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(BASE_DIR, "differential_attack_result.json")
            self.results_screen.load_differential_results(json_path)
            
        except Exception as e:
            self.results_screen.hide_progress()
            QtWidgets.QMessageBox.critical(self, "Error", f"Error:\n{str(e)}")
    
    def _run_algebraic_attack(self, params: dict):
        """Ejecuta ataque algebraico"""
        sage_path = "/usr/bin/sage"
        script_path = self.ALGEBRAIC_SCRIPT
        
        try:
            cmd = (
                f"cd {self.SCRIPT_DIR} && {sage_path} {script_path} "
                f"--plaintext {params['plaintext']} --ciphertext {params['ciphertext']} "
                f"--solver {params['solver']} --rounds {params['rounds']}"
            )
            
            result = subprocess.run(
                ["wsl", "-d", "debian", "bash", "-lc", cmd],
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
                return
            
            # Parsear JSON
            data = json.loads(result.stdout)
            self.results_screen.load_algebraic_results(data)
            
        except Exception as e:
            self.results_screen.hide_progress()
            QtWidgets.QMessageBox.critical(self, "Error", f"Error:\n{str(e)}")
    
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
        if not self.results_screen.last_attack_data:
            QtWidgets.QMessageBox.warning(
                self,
                "Sin datos",
                "No hay resultados para exportar."
            )
            return
        
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Guardar reporte PDF",
            "resultados_ataque_babyaes.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not filename:
            return
        
        try:
            pdf = ExportPdf()

            # Preparar metadata según tipo de ataque
            attack_type = self.results_screen.attack_type
            data = self.results_screen.last_attack_data

            trace_path = None

            if attack_type == "linear":
                best_key_str = " ".join(data["best_key"])
                metadata = {
                    "Tipo de ataque": "Lineal",
                    "Máscara inicial": ", ".join(data["a1"]),
                    "Máscara final": ", ".join(data["a3"]),
                    "Correlación": f"{data['correlation']:.4f}",
                    "Mejor llave": best_key_str,
                    "Apariciones": str(data['top_count'])
                }

                # Traza generada por el script linear -> linear_attack_trace.json
                BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                potential_trace = os.path.join(BASE_DIR, "linear_attack_trace.json")
                if os.path.exists(potential_trace):
                    trace_path = potential_trace

            elif attack_type == "differential":
                # Convertir ratio correctamente
                ratio_value = data.get('ratio', 'N/A')
                if ratio_value != 'N/A':
                    try:
                        if isinstance(ratio_value, str):
                            if '/' in ratio_value:
                                num, den = ratio_value.split('/')
                                ratio_str = f"{float(num)/float(den):.8f}"
                            else:
                                ratio_str = f"{float(ratio_value):.8f}"
                        else:
                            ratio_str = f"{float(ratio_value):.8f}"
                    except:
                        ratio_str = str(ratio_value)
                else:
                    ratio_str = "N/A"

                metadata = {
                    "Tipo de ataque": "Diferencial",
                    "Diferencia entrada (Δu₁)": str(data.get("du1", "N/A")),
                    "Diferencia salida (Δu₃)": str(data.get("du3", "N/A")),
                    "Ratio de propagación": ratio_str,
                    "Mejor llave parcial": str(data.get("best_key", "N/A")),
                    "Mejor llave (binario)": str(data.get("best_key_binary_spaced", "N/A")),
                    "Apariciones": str(data.get("top_count", "N/A"))
                }

                # Si el JSON diferencial contiene "analysis_trace" lo podemos guardar en un temporal
                # pero ExportPdf puede leer un archivo de traza tipo JSON; intentamos encontrar uno.
                BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                potential_trace = os.path.join(BASE_DIR, "differential_attack_trace.json")
                if os.path.exists(potential_trace):
                    trace_path = potential_trace
                else:
                    # si no existe, quizá la traza está empotrada dentro de differential_attack_result.json
                    # en ese caso, creamos un archivo temporal con 'analysis_trace' extraído.
                    differential_json = os.path.join(BASE_DIR, "differential_attack_result.json")
                    try:
                        if os.path.exists(differential_json):
                            with open(differential_json, 'r', encoding='utf-8') as df:
                                dj = json.load(df)
                            if dj.get("analysis_trace"):
                                tmp_trace_path = os.path.join(BASE_DIR, "differential_attack_trace.json")
                                with open(tmp_trace_path, 'w', encoding='utf-8') as tf:
                                    # Empaquetamos en la forma aceptada: {"steps": [...]} o {"phases": [...]}
                                    json.dump({"steps": dj["analysis_trace"]}, tf, indent=2)
                                trace_path = tmp_trace_path
                    except Exception:
                        trace_path = None

            else:  # algebraic
                metadata = {
                    "Tipo de ataque": "Algebraico",
                    "Texto plano": data.get("plaintext", "N/A"),
                    "Texto cifrado": data.get("ciphertext", "N/A"),
                    "Llave recuperada": f"0x{data.get('key', 'N/A')}",
                    "Tiempo": f"{data.get('time', 'N/A')} s"
                }

            # Llamada al exportador: pasamos la tabla de distribución (count_table),
            # la tabla de candidatos (self.table), metadata y trace_path (si existe)
            pdf.export(
                filename,
                [self.results_screen.count_table],
                [self.results_screen.table],
                metadata,
                trace_path
            )
            
            QtWidgets.QMessageBox.information(
                self,
                "Exportación exitosa",
                f"El reporte se guardó en:\n{filename}"
            )
            
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
                border: 2px solid #3b82f6;
                outline: none;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AttackWindow()
    window.show()
    sys.exit(app.exec())