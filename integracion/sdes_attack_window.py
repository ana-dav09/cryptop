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


class SDESLinearWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD - Ataque Lineal S-DES")
        self.resize(1400, 850)

        # Configurar rutas - AJUSTAR SEGÚN TU SISTEMA
        self.SCRIPT_DIR = "/mnt/c/Users/hp/Desktop/diseno/integracion"
        # Usar '/' manualmente para compatibilidad con WSL
        self.SDES_SCRIPT = self.SCRIPT_DIR + "/sdes_lineal.py"
        self.OUTPUT_DIR = self.SCRIPT_DIR + "/sdes_linear_outputs"

        # ----------------- Layout Principal -----------------
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        if SidebarWidget:
            self.sidebar = SidebarWidget(self)
            main_layout.addWidget(self.sidebar)
        else:
            spacer = QtWidgets.QFrame()
            spacer.setFixedWidth(12)
            main_layout.addWidget(spacer)

        # Área de contenido
        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(12)

        # Header
        header = QtWidgets.QLabel("CryptJAD · Ataque Lineal S-DES")
        header.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Weight.Bold))
        header.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #0f172a;")
        content_layout.addWidget(header)

        # ----------------- Parámetros -----------------
        params_box = QtWidgets.QGroupBox("Configuración del Ataque")
        params_box.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        form = QtWidgets.QFormLayout()
        form.setSpacing(10)

        self.pairsSpin = QtWidgets.QSpinBox()
        self.pairsSpin.setRange(100, 50000)
        self.pairsSpin.setValue(5000)
        self.pairsSpin.setStyleSheet("padding: 6px;")

        self.topApproxSpin = QtWidgets.QSpinBox()
        self.topApproxSpin.setRange(1, 15)
        self.topApproxSpin.setValue(6)
        self.topApproxSpin.setToolTip("Número de aproximaciones por S-box a considerar")
        self.topApproxSpin.setStyleSheet("padding: 6px;")

        self.topCandidatesSpin = QtWidgets.QSpinBox()
        self.topCandidatesSpin.setRange(1, 16)
        self.topCandidatesSpin.setValue(8)
        self.topCandidatesSpin.setToolTip("Top candidatos de cada S-box a combinar")
        self.topCandidatesSpin.setStyleSheet("padding: 6px;")

        form.addRow("Número de pares:", self.pairsSpin)
        form.addRow("Aproximaciones/S-box:", self.topApproxSpin)
        form.addRow("Top candidatos:", self.topCandidatesSpin)

        params_box.setLayout(form)
        content_layout.addWidget(params_box)

        # ----------------- Botón de Ejecución -----------------
        btn_row = QtWidgets.QHBoxLayout()
        self.runButton = QtWidgets.QPushButton("▶ Ejecutar Ataque Lineal")
        self.runButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.runButton.setFixedHeight(46)
        self.runButton.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border-radius: 10px;
                font-weight: 600;
                font-size: 14px;
                padding: 10px 24px;
            }
            QPushButton:hover { background-color: #357ABD; }
            QPushButton:pressed { background-color: #2c5a8a; }
        """)
        
        self.exportButton = QtWidgets.QPushButton("📄 Exportar PDF")
        self.exportButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.exportButton.setFixedHeight(46)
        self.exportButton.setEnabled(False)  # Deshabilitado hasta que haya resultados
        self.exportButton.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border-radius: 10px;
                font-weight: 600;
                font-size: 14px;
                padding: 10px 24px;
            }
            QPushButton:hover { background-color: #27AE60; }
            QPushButton:pressed { background-color: #1e8449; }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #ecf0f1;
            }
        """)
        
        btn_row.addWidget(self.runButton)
        btn_row.addWidget(self.exportButton)
        btn_row.addStretch()
        content_layout.addLayout(btn_row)

        # ----------------- Área de Resultados -----------------
        results_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        
        # Panel izquierdo: Tablas LAT
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        left_layout.setSpacing(8)

        # Tabs para S0 y S1
        self.lat_tabs = QtWidgets.QTabWidget()
        
        # S0 Tables
        s0_widget = QtWidgets.QWidget()
        s0_layout = QtWidgets.QVBoxLayout(s0_widget)
        
        self.s0_agreement_table = QtWidgets.QTableWidget()
        self.s0_correlation_table = QtWidgets.QTableWidget()
        
        s0_layout.addWidget(QtWidgets.QLabel("Tabla de Acuerdo (LAT)"))
        s0_layout.addWidget(self.s0_agreement_table)
        s0_layout.addWidget(QtWidgets.QLabel("Correlaciones"))
        s0_layout.addWidget(self.s0_correlation_table)
        
        # S1 Tables
        s1_widget = QtWidgets.QWidget()
        s1_layout = QtWidgets.QVBoxLayout(s1_widget)
        
        self.s1_agreement_table = QtWidgets.QTableWidget()
        self.s1_correlation_table = QtWidgets.QTableWidget()
        
        s1_layout.addWidget(QtWidgets.QLabel("Tabla de Acuerdo (LAT)"))
        s1_layout.addWidget(self.s1_agreement_table)
        s1_layout.addWidget(QtWidgets.QLabel("Correlaciones"))
        s1_layout.addWidget(self.s1_correlation_table)
        
        self.lat_tabs.addTab(s0_widget, "S-box 0")
        self.lat_tabs.addTab(s1_widget, "S-box 1")
        
        left_layout.addWidget(self.lat_tabs)
        results_splitter.addWidget(left_widget)

        # Panel derecho: Candidatos y resumen
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setSpacing(12)

        # Tabs para candidatos individuales
        candidates_tabs = QtWidgets.QTabWidget()
        
        # S0 candidates
        self.s0_candidates_table = QtWidgets.QTableWidget()
        self.s0_candidates_table.setColumnCount(4)
        self.s0_candidates_table.setHorizontalHeaderLabels(["k4 (4 bits)", "Desviación", "Count=0", "N"])
        self.s0_candidates_table.horizontalHeader().setStretchLastSection(True)
        
        # S1 candidates
        self.s1_candidates_table = QtWidgets.QTableWidget()
        self.s1_candidates_table.setColumnCount(4)
        self.s1_candidates_table.setHorizontalHeaderLabels(["k4 (4 bits)", "Desviación", "Count=0", "N"])
        self.s1_candidates_table.horizontalHeader().setStretchLastSection(True)
        
        candidates_tabs.addTab(self.s0_candidates_table, "Candidatos S0")
        candidates_tabs.addTab(self.s1_candidates_table, "Candidatos S1")
        
        right_layout.addWidget(QtWidgets.QLabel("Candidatos por S-box"))
        right_layout.addWidget(candidates_tabs)

        # Tabla de subkey2 combinadas
        self.subkey2_table = QtWidgets.QTableWidget()
        self.subkey2_table.setColumnCount(3)
        self.subkey2_table.setHorizontalHeaderLabels(["Subkey2 (8 bits)", "Score", "Detalles"])
        self.subkey2_table.horizontalHeader().setStretchLastSection(True)
        self.subkey2_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        
        right_layout.addWidget(QtWidgets.QLabel("Top Candidatos Subkey2"))
        right_layout.addWidget(self.subkey2_table)

        # Resumen JSON
        self.summaryBox = QtWidgets.QTextEdit()
        self.summaryBox.setReadOnly(True)
        self.summaryBox.setFixedHeight(180)
        self.summaryBox.setStyleSheet("""
            QTextEdit {
                background-color: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        
        right_layout.addWidget(QtWidgets.QLabel("Resumen del Ataque"))
        right_layout.addWidget(self.summaryBox)

        results_splitter.addWidget(right_widget)
        results_splitter.setStretchFactor(0, 2)
        results_splitter.setStretchFactor(1, 1)
        
        content_layout.addWidget(results_splitter)

        # ----------------- Barra de Progreso -----------------
        bottom_row = QtWidgets.QHBoxLayout()
        self.statusLabel = QtWidgets.QLabel("Listo")
        self.statusLabel.setStyleSheet("color: #64748b; font-weight: 500;")
        
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e2e8f0;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4A90E2;
            }
        """)
        
        bottom_row.addWidget(self.statusLabel)
        bottom_row.addStretch()
        bottom_row.addWidget(self.progress)
        content_layout.addLayout(bottom_row)

        main_layout.addWidget(content, stretch=1)

        # Conectar señales
        self.runButton.clicked.connect(self.on_run_linear_attack)
        self.exportButton.clicked.connect(self.on_export_pdf)
        
        # Variables para almacenar datos del último ataque
        self.last_summary = None

    def on_run_linear_attack(self):
        """Ejecuta el script de ataque lineal S-DES usando Sage."""
        sage_path = "/usr/bin/sage"
        script_path = self.SDES_SCRIPT

        # Mostrar progreso
        self.statusLabel.setText("Ejecutando ataque lineal S-DES... (puede tardar)")
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)  # Indeterminate
        QtWidgets.QApplication.processEvents()

        try:
            # Ejecutar con WSL y Sage (sin cwd porque WSL maneja rutas diferentes)
            result = subprocess.run(
                ["wsl", "-d", "debian", sage_path, "-python", script_path],
                capture_output=True,
                text=True
            )

            self.progress.setVisible(False)
            self.progress.setRange(0, 100)
            self.progress.setValue(100)

            if result.returncode != 0:
                QtWidgets.QMessageBox.critical(
                    self, 
                    "Error ejecutando Sage", 
                    f"Código de salida: {result.returncode}\n\n{result.stderr}"
                )
                self.statusLabel.setText("Error en ejecución")
                print("STDERR:", result.stderr)
                return

            # Cargar resultados
            self.load_results()
            self.statusLabel.setText("Ataque completado exitosamente")
            self.exportButton.setEnabled(True)  # Habilitar exportación

        except Exception as e:
            self.progress.setVisible(False)
            QtWidgets.QMessageBox.critical(
                self, 
                "Error ejecutando ataque", 
                str(e)
            )
            self.statusLabel.setText("Error")
            print("Excepción:", str(e))

    def load_results(self):
        """Carga todos los archivos CSV y JSON generados por el ataque."""
        try:
            # Convertir ruta WSL a Windows para leer archivos localmente
            # /mnt/c/Users/... -> C:/Users/...
            output_dir_windows = self.OUTPUT_DIR.replace("/mnt/c/", "C:/").replace("/mnt/", "")
            
            # Cargar summary JSON
            summary_path = output_dir_windows + "/linear_attack_summary.json"
            if os.path.exists(summary_path):
                with open(summary_path, 'r', encoding='utf-8') as f:
                    summary = json.load(f)
                
                # Guardar para exportación
                self.last_summary = summary
                
                # Mostrar resumen formateado
                summary_text = (
                    f"=== ATAQUE LINEAL S-DES ===\n\n"
                    f"Pares utilizados: {summary.get('pairs_used', 'N/A')}\n"
                    f"Clave real (10 bits): {summary.get('random_key', 'N/A')}\n"
                    f"Subkey2 real (8 bits): {summary.get('subkey2_real', 'N/A')}\n"
                    f"Subkey2 recuperada: {summary.get('subkey2_best_guess', 'N/A')}\n"
                    f"Score: {summary.get('best_guess_score', 'N/A')}\n\n"
                    f"S0: α={summary.get('s0_best_alpha', 'N/A')} "
                    f"β={summary.get('s0_best_beta', 'N/A')} LAT={summary.get('s0_lat', 'N/A')}\n"
                    f"S1: α={summary.get('s1_best_alpha', 'N/A')} "
                    f"β={summary.get('s1_best_beta', 'N/A')} LAT={summary.get('s1_lat', 'N/A')}"
                )
                self.summaryBox.setText(summary_text)

                # Cargar candidatos S0 y S1
                self._load_sbox_candidates(summary.get('s0_top_candidates', []), self.s0_candidates_table)
                self._load_sbox_candidates(summary.get('s1_top_candidates', []), self.s1_candidates_table)

            # Cargar matrices LAT (convertir rutas)
            self._load_lat_table(output_dir_windows + "/s0_agreement.csv", self.s0_agreement_table)
            self._load_lat_table(output_dir_windows + "/s0_correlation.csv", self.s0_correlation_table)
            self._load_lat_table(output_dir_windows + "/s1_agreement.csv", self.s1_agreement_table)
            self._load_lat_table(output_dir_windows + "/s1_correlation.csv", self.s1_correlation_table)

        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, 
                "Advertencia al cargar resultados", 
                f"Algunos archivos no pudieron cargarse:\n{str(e)}"
            )

    def _load_sbox_candidates(self, candidates, table_widget):
        """Llena tabla de candidatos de S-box."""
        table_widget.setRowCount(len(candidates))
        for row, cand in enumerate(candidates):
            table_widget.setItem(row, 0, QtWidgets.QTableWidgetItem(cand.get('k4', '')))
            table_widget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(cand.get('deviation', ''))))
            table_widget.setItem(row, 2, QtWidgets.QTableWidgetItem(str(cand.get('count_zero', ''))))
            table_widget.setItem(row, 3, QtWidgets.QTableWidgetItem(str(cand.get('N', ''))))
        table_widget.resizeColumnsToContents()

    def _load_lat_table(self, csv_path, table_widget):
        """Carga una matriz LAT desde CSV a una tabla."""
        if not os.path.exists(csv_path):
            return

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            if len(rows) < 2:
                return

            # Convertir a matriz (agrupar por alpha)
            data = {}
            for row in rows[1:]:  # Skip header
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

    def on_export_pdf(self):
        """Exporta los resultados del ataque a un archivo PDF."""
        if not ExportPdf:
            QtWidgets.QMessageBox.warning(
                self,
                "Módulo no disponible",
                "El módulo export_pdf no está disponible.\n"
                "Asegúrate de tener reportlab instalado y el archivo export_pdf.py en la ruta correcta."
            )
            return
        
        if not self.last_summary:
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
            "resultados_ataque_sdes.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not filename:
            return  # Usuario canceló
        
        try:
            pdf = ExportPdf()
            
            # Preparar metadata
            metadata = {
                "Algoritmo": "Simplified DES (S-DES)",
                "Número de rondas": "2",
                "Pares usados": str(self.last_summary.get('pairs_used', 'N/A')),
                "Clave real (10 bits)": self.last_summary.get('random_key', 'N/A'),
                "Subkey2 real (8 bits)": self.last_summary.get('subkey2_real', 'N/A'),
                "Subkey2 recuperada": self.last_summary.get('subkey2_best_guess', 'N/A'),
                "Score del mejor candidato": str(self.last_summary.get('best_guess_score', 'N/A')),
                "S0 mejor aproximación": f"α={self.last_summary.get('s0_best_alpha', 'N/A')} β={self.last_summary.get('s0_best_beta', 'N/A')} LAT={self.last_summary.get('s0_lat', 'N/A')}",
                "S1 mejor aproximación": f"α={self.last_summary.get('s1_best_alpha', 'N/A')} β={self.last_summary.get('s1_best_beta', 'N/A')} LAT={self.last_summary.get('s1_lat', 'N/A')}",
            }
            
            # Tablas LAT (puedes elegir cuáles incluir)
            lat_tables = [
                self.s0_correlation_table,
                self.s1_correlation_table
            ]
            
            # Tablas de candidatos
            candidate_tables = [
                self.s0_candidates_table,
                self.s1_candidates_table,
                self.subkey2_table
            ]
            
            # Exportar
            pdf.export(
                filename,
                lat_tables,
                candidate_tables,
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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = SDESLinearWindow()
    w.show()
    sys.exit(app.exec())