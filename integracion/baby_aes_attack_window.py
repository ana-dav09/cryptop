import os
import sys
import json
import subprocess
import time
from typing import Tuple
from fractions import Fraction

from PyQt6 import QtWidgets, QtGui, QtCore
from matplotlib.table import Table
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from export_pdf import ExportPdf
from helpers import MplCanvas
from helpers import SageRunner

# Matplotlib / pandas / numpy
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

try:
    from barra_lateral import SidebarWidget
except Exception:
    try:
        THIS_DIR = os.path.dirname(os.path.abspath(__file__))
        POSSIBLE = [
            os.path.join(THIS_DIR),
            os.path.join(THIS_DIR, "..", "src"),
            os.path.join(THIS_DIR, "..", "ui"),
            os.path.join(THIS_DIR, ".."),
        ]
        for p in POSSIBLE:
            if os.path.isdir(p) and p not in sys.path:
                sys.path.append(p)
        from barra_lateral import SidebarWidget
    except Exception:
        SidebarWidget = None 


# ----------------- Ventana principal -----------------
class AttackWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD - Ataques en BabyAES")
        self.resize(1200, 780)

        # ---- Configurar rutas y comando Sage ----
        self.SCRIPT_DIR = "/mnt/c/Users/hp/Desktop/diseno/integracion"

        self.SAGE_CMD_TEMPLATE = ["wsl", "-d", "debian", "bash", "-lc", "sage -python {script}"]

        # nombres de scripts que el sistema invocará
        self.DIFF_SCRIPT = os.path.join(self.SCRIPT_DIR, "baby_aes_attack.py")
        self.LINEAR_SCRIPT = os.path.join(self.SCRIPT_DIR, "baby_aes_linear_attack.py")

        # Variable para almacenar últimos datos
        self.last_attack_data = None

        # ----------------- Layout -----------------
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        if SidebarWidget:
            self.sidebar = SidebarWidget(self)
            main_layout.addWidget(self.sidebar)
        else:
            spacer = QtWidgets.QFrame()
            spacer.setFixedWidth(12)
            main_layout.addWidget(spacer)

        # Content area
        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(12)

        # Header
        header = QtWidgets.QLabel("CryptJAD · Ataques en BabyAES")
        header.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Weight.Bold))
        header.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #0f172a;")
        content_layout.addWidget(header)

        # Parámetros de configuración
        params_box = QtWidgets.QGroupBox("Configuración de ataque")
        form = QtWidgets.QFormLayout()

        self.roundsSpin = QtWidgets.QSpinBox()
        self.roundsSpin.setRange(1, 10)
        self.roundsSpin.setValue(3)

        self.pairsSpin = QtWidgets.QSpinBox()
        self.pairsSpin.setRange(100, 100000)
        self.pairsSpin.setValue(5000)

        self.maskEdit = QtWidgets.QLineEdit("0010,0000,0000,1000")

        self.topkSpin = QtWidgets.QSpinBox()
        self.topkSpin.setRange(1, 100)
        self.topkSpin.setValue(20)

        form.addRow("Número de rondas:", self.roundsSpin)
        form.addRow("Número de pares:", self.pairsSpin)
        form.addRow("Máscara inicial:", self.maskEdit)
        form.addRow("Top-K candidatos:", self.topkSpin)

        params_box.setLayout(form)
        content_layout.addWidget(params_box)

        # Botones
        btn_row = QtWidgets.QHBoxLayout()
        self.diffButton = QtWidgets.QPushButton("▶ Ejecutar Ataque Diferencial")
        self.linearButton = QtWidgets.QPushButton("▶ Ejecutar Ataque Lineal")
        self.exportButton = QtWidgets.QPushButton("📄 Exportar PDF")
        
        for b in (self.diffButton, self.linearButton, self.exportButton):
            b.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            b.setFixedHeight(42)
        
        # Estilos específicos
        self.diffButton.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border-radius: 10px;
                font-weight: 600;
                padding: 8px 18px;
            }
            QPushButton:hover { background-color: #357ABD; }
        """)
        self.linearButton.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border-radius: 10px;
                font-weight: 600;
                padding: 8px 18px;
            }
            QPushButton:hover { background-color: #357ABD; }
        """)
        self.exportButton.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border-radius: 10px;
                font-weight: 600;
                padding: 8px 18px;
            }
            QPushButton:hover { background-color: #27AE60; }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #ecf0f1;
            }
        """)
        self.exportButton.setEnabled(False)  # Deshabilitado inicialmente
        
        btn_row.addWidget(self.diffButton)
        btn_row.addWidget(self.linearButton)
        btn_row.addWidget(self.exportButton)
        btn_row.addStretch()
        content_layout.addLayout(btn_row)

        # Area de tabla
        mid_layout = QtWidgets.QHBoxLayout()
        mid_layout.setSpacing(12)

        # Tabla de DL
        tables_widget = QtWidgets.QWidget()
        tables_layout = QtWidgets.QVBoxLayout(tables_widget)
        tables_layout.setSpacing(8)

        self.count_table = QtWidgets.QTableWidget()

        tables_layout.addWidget(QtWidgets.QLabel("Correlaciones lineales"))
        tables_layout.addWidget(self.count_table, stretch=2)

        mid_layout.addWidget(tables_widget, stretch=2)

        # Panel derecho: Resultados y llaves candidatas
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setSpacing(8)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Index", "Counter", "Key"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

        self.jsonBox = QtWidgets.QTextEdit()
        self.jsonBox.setReadOnly(True)
        self.jsonBox.setFixedHeight(200)

        right_layout.addWidget(QtWidgets.QLabel("Top candidatos"))
        right_layout.addWidget(self.table, stretch=1)
        right_layout.addWidget(QtWidgets.QLabel("Resumen (JSON)"))
        right_layout.addWidget(self.jsonBox)

        mid_layout.addWidget(right_widget, stretch=1)
        content_layout.addLayout(mid_layout)

        # Progreso....
        bottom_row = QtWidgets.QHBoxLayout()
        self.statusLabel = QtWidgets.QLabel("Listo")
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.progress.setVisible(False)
        bottom_row.addWidget(self.statusLabel)
        bottom_row.addStretch()
        bottom_row.addWidget(self.progress)
        content_layout.addLayout(bottom_row)

        main_layout.addWidget(content, stretch=1)

        # Señales
        self.diffButton.clicked.connect(self.on_run_differential)
        self.linearButton.clicked.connect(self.on_run_linear)
        self.exportButton.clicked.connect(self.on_export_pdf)

        # Runner holder
        self.runner: SageRunner | None = None

                # --- Estilos globales ---
        self.setStyleSheet("""
            QWidget {
                background-color: #f9fafb;
                font-family: 'Segoe UI';
                color: #1e293b;
            }

            QGroupBox {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
                font-weight: 600;
                padding: 16px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #0f172a;
                font-size: 14px;
            }

            QLabel {
                color: #334155;
                font-size: 14px;
            }

            QTableWidget {
                background-color: white;
                gridline-color: #cbd5e1;
                border-radius: 8px;
                selection-background-color: #dbeafe;
                selection-color: #0f172a;
            }

            QHeaderView::section {
                background-color: #f1f5f9;
                color: #1e293b;
                padding: 6px;
                border: none;
                font-weight: 600;
                border-bottom: 1px solid #cbd5e1;
            }

            QLineEdit, QSpinBox, QTextEdit {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 6px;
                font-size: 13px;
            }

            QLineEdit:focus, QSpinBox:focus, QTextEdit:focus {
                border: 1px solid #3b82f6;
                outline: none;
            }

            QPushButton {
                font-family: 'Segoe UI';
                font-weight: 600;
                border-radius: 10px;
                padding: 8px 18px;
            }

            QPushButton#diffButton {
                background-color: #4A90E2;
                color: white;
            }
            QPushButton#diffButton:hover { background-color: #357ABD; }

            QPushButton#linearButton {
                background-color: #4A90E2;
                color: white;
            }
            QPushButton#linearButton:hover { background-color: #357ABD; }

            QPushButton#exportButton {
                background-color: #2ECC71;
                color: white;
            }
            QPushButton#exportButton:hover { background-color: #27AE60; }
            QPushButton#exportButton:disabled {
                background-color: #95a5a6;
                color: #ecf0f1;
            }

            QProgressBar {
                background-color: #e2e8f0;
                border: none;
                border-radius: 6px;
                height: 10px;
            }

            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 6px;
            }
        """)

        # --- Identificadores para botones (para aplicar estilos por ID) ---
        self.diffButton.setObjectName("diffButton")
        self.linearButton.setObjectName("linearButton")
        self.exportButton.setObjectName("exportButton")

        # Bordes suaves y sombra para cajas
        for box in [params_box, self.count_table, self.table, self.jsonBox]:
            effect = QtWidgets.QGraphicsDropShadowEffect()
            effect.setBlurRadius(15)
            effect.setXOffset(0)
            effect.setYOffset(2)
            effect.setColor(QtGui.QColor(0, 0, 0, 40))
            box.setGraphicsEffect(effect)


    # ----------------- Helpers -----------------
    def _build_sage_cmd(self, script_path: str) -> list:
        template = list(self.SAGE_CMD_TEMPLATE)
        new = []
        for token in template:
            if isinstance(token, str) and "{script}" in token:
                new.append(token.format(script=script_path))
            else:
                new.append(token)
        return new

    def _start_runner(self, script_path: str):
        if not os.path.exists(script_path):
            QtWidgets.QMessageBox.critical(self, "Error", f"Script no encontrado:\n{script_path}")
            return

        cmd = self._build_sage_cmd(script_path)
        self.statusLabel.setText("Ejecutando Sage... (esto puede tardar)")
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)

        # Hilo
        self.runner = SageRunner(cmd, os.path.dirname(script_path))
        self.runner.finished.connect(self.on_runner_finished)
        self.runner.start()

    # ----------------- Para correr ataques -----------------
    def on_run_differential(self):
        sage_path = "/usr/bin/sage"
        script_path = "/mnt/c/Users/hp/Desktop/diseno/integracion/baby_aes_attack.py"

        try:
            result = subprocess.run(
                ["wsl", "-d", "debian", sage_path, "-python", script_path],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                QtWidgets.QMessageBox.critical(self, "Error ejecutando Sage", result.stderr)
                print(result.stderr)
            else:
                # Parseamos JSON
                data = json.loads(result.stdout)
                msg = (
                    f"Δu1: {data['du1']}\n\n"
                    f"Δu3: {data['du3']}\n\n"
                    f"Propagation ratio: {data['ratio']}\n\n"
                    f"Llave parcial recuperada:\n{data['best_key']}\n\n"
                    f"Veces que apareció la mejor llave: {data['top_count']}"
                )
                self.jsonBox.setText(msg)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error ejecutando ataque", str(e))
            print(str(e))

    def on_run_linear(self):
        sage_path = "/usr/bin/sage"
        script_path = "/mnt/c/Users/hp/Desktop/diseno/integracion/baby_aes_linear_attack.py"

        rounds = self.roundsSpin.value()
        pairs = self.pairsSpin.value()
        mask = self.maskEdit.text()
        topk = self.topkSpin.value()

        try:
            result = subprocess.run(
                [
                    "wsl", "-d", "debian", sage_path, "-python", script_path,
                    "--rounds", str(rounds),
                    "--pairs", str(pairs),
                    "--mask", mask,
                    "--topk", str(topk)
                ],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                QtWidgets.QMessageBox.critical(self, "Error ejecutando Sage", result.stderr)
                return

            data = json.loads(result.stdout)
            msg = (
                "=== Ataque Lineal ===\n\n"
                f"a1 (máscara inicial): {data['a1']}\n"
                f"a3 (máscara final): {data['a3']}\n"
                f"|corr(a1||a3)|: {data['correlation']}\n"
                f"Llave parcial recuperada: {data['best_key']}\n"
                f"Veces que apareció: {data['top_count']}\n"
            )
            self.jsonBox.setText(msg)
            self.load_linear_results()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error ejecutando ataque lineal", str(e))
    
    def run_algebraic(self):
        #el comando esta para ejecutarse en linux
        command = ["sage", "baby_aes_algebraic_attack.sage"]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                QtWidgets.QMessageBox.critical(self, "Error ejecutando Sage", result.stderr)
                return

            data = json.loads(result.stdout)
            msg = (
                "=== Ataque algebraico === \n\n"
                f"Texto plano conocido: {data['plaintext']}\n"
                f"Texto cifrado conocido: {data['ciphertext']}\n"
                f"Llave recuperada: 0x{data['key']}\n"
                f"Tiempo de ejecución: {data['time']} segundos\n"
                f"Sat solver utilizado: {data['solver']}\n"
            )
            self.resultBox.setText(msg)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error ejecutando ataque algebraico", str(e))

    def load_linear_results(self):
        """
        Carga los CSV y JSON generados por baby_aes_linear_attack.py
        y actualiza self.table y self.jsonBox
        """
        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(BASE_DIR, "linear_attack_result.json")

            if not os.path.exists(json_path):
                QtWidgets.QMessageBox.critical(self, "Error", f"Archivo no encontrado: {json_path}")
                return

            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Guardar datos para exportación
            self.last_attack_data = data

            # Actualizar JSON summary
            best_key_str = " ".join(data["best_key"])
            corr = data["correlation"]
            top_count = data["top_count"]
            self.jsonBox.setText(
                f"Mejor llave: {best_key_str}\n"
                f"Correlación: {corr:.4f}\n"
                f"Top contador: {top_count}"
            )

            # Llenar tabla top_candidates
            top_candidates = data.get("top_candidates", [])
            self.table.setRowCount(len(top_candidates))
            for row_idx, candidate in enumerate(top_candidates):
                self.table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(candidate["index"])))
                self.table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(str(candidate["counter"])))
                key_str = " ".join(candidate["key"])
                self.table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(key_str))

            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()
            
            # Cargar tabla de correlaciones
            self.load_linear_heatmaps()
            
            # Habilitar botón de exportación
            self.exportButton.setEnabled(True)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error cargando resultados", str(e))

    def load_linear_heatmaps(self):
        """
        Carga corr_matrix.csv y dibuja tabla de correlaciones
        """
        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            corr_path = os.path.join(BASE_DIR, "corr_matrix.csv")
            self.load_matrix_as_table2(corr_path, "Tabla de Correlación")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error cargando heatmaps", str(e))

    def load_matrix_as_table2(self, path, title):
        """
        Carga un CSV y lo muestra como tabla en un QTableWidget.
        """
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

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, f"Error cargando {title}", str(e))

    def on_export_pdf(self):
        """Exporta los resultados del ataque a PDF."""
        if not self.last_attack_data:
            QtWidgets.QMessageBox.warning(
                self,
                "Sin datos",
                "Primero debes ejecutar un ataque antes de exportar."
            )
            return

        # Diálogo para guardar archivo
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Guardar reporte PDF",
            "resultados_ataque_babyaes.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not filename:
            return  # Usuario canceló

        try:
            pdf = ExportPdf()
            
            best_key_str = " ".join(self.last_attack_data["best_key"])
            
            metadata = {
                "Algoritmo": "Baby AES",
                "Número de rondas": str(self.roundsSpin.value()),
                "Pares usados": str(self.pairsSpin.value()),
                "Máscara inicial": self.maskEdit.text(),
                "Clave parcial recuperada": best_key_str,
                "Correlación": f"{self.last_attack_data['correlation']:.4f}",
                "Top contador": str(self.last_attack_data['top_count'])
            }

            pdf.export(
                filename,
                [self.count_table],   # Tabla de correlaciones
                [self.table],         # Tabla de candidatos
                metadata
            )
            
            QtWidgets.QMessageBox.information(
                self,
                "Exportación exitosa",
                f"El reporte se guardó correctamente en:\n{filename}"
            )
            
            self.statusLabel.setText(f"PDF exportado: {os.path.basename(filename)}")

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error al exportar PDF",
                f"Ocurrió un error durante la exportación:\n{str(e)}"
            )
            print("Error en exportación PDF:", e)

    def _clear_plots_and_table(self):
        self.table.setRowCount(0)
        self.jsonBox.clear()
        self.statusLabel.setText("Listo")

    # ----------------- Runner finished handler -----------------
    def on_runner_finished(self, data: dict, script_dir: str):
        self.progress.setVisible(False)
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.load_linear_results()
        self.statusLabel.setText(f"Ataque completado en {self.runner.duration:.2f} segundos")

        if "error" in data:
            err = data.get("error", "Error desconocido")
            stdout = data.get("stdout", "")
            stderr = data.get("stderr", "")
            full = f"{err}\n\nSTDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
            QtWidgets.QMessageBox.critical(self, "Error ejecutando Sage", full)
            self.statusLabel.setText("Error")
            return

        self.statusLabel.setText("Completado")
        pretty = json.dumps(data, indent=2, ensure_ascii=False)
        self.jsonBox.setText(pretty)

        counts_csv = os.path.join(script_dir, "linear_counts.csv")
        corr_csv = os.path.join(script_dir, "corr_matrix.csv")

        if os.path.exists(counts_csv):
            try:
                df = pd.read_csv(counts_csv)
                if 'counter' in df.columns and 'key' in df.columns:
                    df['abs_counter'] = df['counter'].abs()
                    df_sorted = df.sort_values('abs_counter', ascending=False).reset_index(drop=True)
                    self._fill_table(df_sorted)
            except Exception as e:
                print("Error leyendo counts CSV:", e)

        if 'top_candidates' in data and not os.path.exists(counts_csv):
            try:
                t = data['top_candidates']
                df2 = pd.DataFrame(t)
                if 'key' in df2.columns:
                    df2['key'] = df2['key'].apply(lambda k: " ".join(k) if isinstance(k, list) else str(k))
                self._fill_table(df2)
            except Exception as e:
                print("Error llenando tabla desde JSON:", e)

    def _fill_table(self, df_sorted: pd.DataFrame, topK: int = 50):
        topK = min(topK, len(df_sorted))
        self.table.setRowCount(topK)
        for r in range(topK):
            idx = int(df_sorted.loc[r, 'index']) if 'index' in df_sorted.columns else r
            counter = int(df_sorted.loc[r, 'counter']) if 'counter' in df_sorted.columns else 0
            key = df_sorted.loc[r, 'key'] if 'key' in df_sorted.columns else ""
            self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(str(idx)))
            self.table.setItem(r, 1, QtWidgets.QTableWidgetItem(str(counter)))
            self.table.setItem(r, 2, QtWidgets.QTableWidgetItem(str(key)))
        self.table.resizeColumnsToContents()

# ----------------- Ejecutar la ventana -----------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = AttackWindow()
    w.show()
    sys.exit(app.exec())