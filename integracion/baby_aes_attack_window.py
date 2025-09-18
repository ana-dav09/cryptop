
import os
import sys
import json
import subprocess
import time
from typing import Tuple
from fractions import Fraction

from PyQt6 import QtWidgets, QtGui, QtCore

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
            os.path.join(THIS_DIR),  # misma carpeta
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


# ----------------- Helper: Matplotlib canvas -----------------
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)


# ----------------- QThread runner para ejecutar Sage -----------------
class SageRunner(QtCore.QThread):
    finished = QtCore.pyqtSignal(object, str)   

    def __init__(self, cmd_list, script_dir):
        super().__init__()
        self.cmd_list = cmd_list
        self.script_dir = script_dir

    def run(self):
        try:
            # Ejecutar el comando y capturar salida
            proc = subprocess.run(self.cmd_list, capture_output=True, text=True)
        except Exception as e:
            self.finished.emit({"error": str(e)}, self.script_dir)
            return

        if proc.returncode != 0:
            # devolver stderr como error
            self.finished.emit({"error": proc.stderr.strip() or f"Exit code {proc.returncode}"}, self.script_dir)
            return

        # intentar parsear JSON (el script Sage debe imprimir JSON)
        try:
            data = json.loads(proc.stdout)
            self.finished.emit(data, self.script_dir)
        except Exception as e:
            out = proc.stdout.strip()
            err = proc.stderr.strip()
            combined = {"error": f"JSON parse error: {str(e)}", "stdout": out, "stderr": err}
            self.finished.emit(combined, self.script_dir)


# ----------------- Ventana principal -----------------
class AttackWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD - Ataques (Diferencial / Lineal)")
        self.resize(1200, 780)

        # ---- Configura rutas y comando Sage ----
        self.SCRIPT_DIR = "/mnt/c/Users/hp/Desktop/diseno/integracion"  # ajustar si hace falta

        self.SAGE_CMD_TEMPLATE = ["wsl", "-d", "debian", "bash", "-lc", "sage -python {script}"]

        # nombres de scripts que el sistema invocará
        self.DIFF_SCRIPT = os.path.join(self.SCRIPT_DIR, "baby_aes_attack.py")
        self.LINEAR_SCRIPT = os.path.join(self.SCRIPT_DIR, "baby_aes_linear_attack.py")

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
        header = QtWidgets.QLabel("CryptJAD · Ataques Criptoanalíticos")
        header.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Weight.Bold))
        header.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #0f172a;")
        content_layout.addWidget(header)

        # Botones
        btn_row = QtWidgets.QHBoxLayout()
        self.diffButton = QtWidgets.QPushButton("▶ Ejecutar Ataque Diferencial")
        self.linearButton = QtWidgets.QPushButton("▶ Ejecutar Ataque Lineal")
        for b in (self.diffButton, self.linearButton):
            b.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            b.setFixedHeight(42)
            b.setStyleSheet("""
                QPushButton {
                    background-color: #4A90E2;
                    color: white;
                    border-radius: 10px;
                    font-weight: 600;
                    padding: 8px 18px;
                }
                QPushButton:hover { background-color: #357ABD; }
            """)
        btn_row.addWidget(self.diffButton)
        btn_row.addWidget(self.linearButton)
        btn_row.addStretch()
        content_layout.addLayout(btn_row)

        # Area de tabla
        mid_layout = QtWidgets.QHBoxLayout()
        mid_layout.setSpacing(12)

        # Tabla de DL
        tables_widget = QtWidgets.QWidget()
        tables_layout = QtWidgets.QVBoxLayout(tables_widget)
        tables_layout.setSpacing(8)

        #self.bias_table = QtWidgets.QTableWidget()
        self.count_table = QtWidgets.QTableWidget()

        #tables_layout.addWidget(QtWidgets.QLabel("Distribución lineal"))
        #tables_layout.addWidget(self.bias_table, stretch=2)
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

        # Runner holder
        self.runner: SageRunner | None = None

    # ----------------- Helpers -----------------
    def _build_sage_cmd(self, script_path: str) -> list:
        
        template = list(self.SAGE_CMD_TEMPLATE)  # copia
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

        try:
            result = subprocess.run(
                ["wsl", "-d", "debian", sage_path, "-python", script_path],
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


    def load_linear_results(self):
        """
        Carga los CSV y JSON generados por baby_aes_linear_attack.py
        y actualiza self.table y self.jsonBox
        """
        try:
            # Paths
            #script_dir = "C:/Users\hp\Desktop\diseno\integracion"
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(BASE_DIR, "linear_attack_result.json")

            # Ejecutar Sage para asegurarnos de que el JSON/CSVs estén actualizados
            
            # Ahora intentamos abrir el JSON que el script genera
            if not os.path.exists(json_path):
                QtWidgets.QMessageBox.critical(self, "Error", f"Archivo no encontrado: {json_path}")
                return

            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Actualizar JSON summary (igual que antes)
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
            #Llamar función para la tabla DL
            self.load_linear_heatmaps()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error cargando resultados", str(e))


    def load_linear_heatmaps(self):
        """
        Carga corr_matrix.csv y prob_matrix.csv y dibuja heatmaps en self.heat_canvas
        """
        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            corr_path = os.path.join(BASE_DIR, "corr_matrix.csv")
            prob_path = os.path.join(BASE_DIR, "prob_matrix.csv")

            #Esto es para un gráfico, pero ahorita no
            """
            corr_matrix = np.loadtxt(corr_path, delimiter=",")
            prob_matrix = np.loadtxt(prob_path, delimiter=",")

            # Corr Heatmap
            self.heat_canvas.axes.clear()
            im = self.heat_canvas.axes.imshow(corr_matrix, cmap="coolwarm", interpolation="nearest")
            self.heat_canvas.axes.set_title("Matriz de Correlación")
            self.heat_canvas.axes.set_xlabel("b")
            self.heat_canvas.axes.set_ylabel("a")
            self.heat_canvas.figure.colorbar(im, ax=self.heat_canvas.axes)
            self.heat_canvas.draw()

            # Prob Heatmap en hist_canvas como ejemplo
            self.hist_canvas.axes.clear()
            im2 = self.hist_canvas.axes.imshow(prob_matrix, cmap="viridis", interpolation="nearest")
            self.hist_canvas.axes.set_title("Matriz de Probabilidad")
            self.hist_canvas.axes.set_xlabel("b")
            self.hist_canvas.axes.set_ylabel("a")
            self.hist_canvas.figure.colorbar(im2, ax=self.hist_canvas.axes)
            self.hist_canvas.draw()
            """
            self.load_matrix_as_table2(corr_path, "Tabla de Correlación")
            #self.load_matrix_as_table(prob_path, "Tabla de Probabilidades")


        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error cargando heatmaps", str(e))


    def load_matrix_as_table(self, path, title):
        """
        Carga un CSV y lo muestra como tabla en un QTableWidget.
        """
        try:
            matrix = np.loadtxt(path, delimiter=",")
            rows, cols = matrix.shape

            table = QtWidgets.QTableWidget()
            self.bias_table.setRowCount(rows)
            self.bias_table.setColumnCount(cols)
            self.bias_table.setHorizontalHeaderLabels([f"y{j}" for j in range(cols)])
            self.bias_table.setVerticalHeaderLabels([f"x{i}" for i in range(rows)])

            for i in range(rows):
                for j in range(cols):
                    item = QtWidgets.QTableWidgetItem(f"{Fraction(matrix[i,j])}")
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    self.bias_table.setItem(i, j, item)
                

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, f"Error cargando {title}", str(e))

    #Función para cargar los datos csv a la tabla dl
    def load_matrix_as_table2(self, path, title):
        """
        Carga un CSV y lo muestra como tabla en un QTableWidget.
        """
        try:
            matrix = np.loadtxt(path, delimiter=",")
            rows, cols = matrix.shape

            table = QtWidgets.QTableWidget()
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

    def plot_candidates_bar(self, results):
        """
        Dibuja gráfica de barras con los candidatos.
        """
        self.hist_canvas.axes.clear()

        candidates = [str(r["candidate"]) for r in results]
        scores = [r["score"] for r in results]

        self.hist_canvas.axes.bar(candidates, scores, color="skyblue")
        self.hist_canvas.axes.set_title("Ranking de Candidatos")
        self.hist_canvas.axes.set_xlabel("Candidato")
        self.hist_canvas.axes.set_ylabel("Score")
        self.hist_canvas.draw()


    def run_script(self, script):
        start = time.time()
        proc = subprocess.run([sys.executable, script], capture_output=True, text=True)
        end = time.time()
        duration = end - start
        return proc.stdout, proc.stderr, duration


    def _clear_plots_and_table(self):
        self.hist_canvas.axes.clear(); self.hist_canvas.draw()
        self.heat_canvas.axes.clear(); self.heat_canvas.draw()
        self.table.setRowCount(0)
        self.jsonBox.clear()
        self.statusLabel.setText("Listo")

    # ----------------- Runner finished handler -----------------
    def on_runner_finished(self, data: dict, script_dir: str):
        # hide spinner
        self.progress.setVisible(False)
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.load_linear_results()
        self.statusLabel.setText(f"Ataque completado en {self.runner.duration:.2f} segundos")

        # Error handling
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

        # CSV que contienen la información
        counts_csv = os.path.join(script_dir, "linear_counts.csv")
        corr_csv = os.path.join(script_dir, "corr_matrix.csv")

        # Tabla de candidatos
        if os.path.exists(counts_csv):
            try:
                df = pd.read_csv(counts_csv)
                if 'counter' in df.columns and 'key' in df.columns:
                    df['abs_counter'] = df['counter'].abs()
                    df_sorted = df.sort_values('abs_counter', ascending=False).reset_index(drop=True)
                    self._plot_top_candidates(df_sorted)
                    self._fill_table(df_sorted)
                else:
                   
                    pass
            except Exception as e:
                print("Error leyendo counts CSV:", e)

        if os.path.exists(corr_csv):
            try:
                corr = np.loadtxt(corr_csv, delimiter=',')
                self._plot_corr_heatmap(corr)
            except Exception as e:
                print("Error leyendo corr CSV:", e)

        # Llenado de los candidatos de llave
        if 'top_candidates' in data and not os.path.exists(counts_csv):
            try:
                t = data['top_candidates']
                df2 = pd.DataFrame(t)
                # normalize key representation
                if 'key' in df2.columns:
                    df2['key'] = df2['key'].apply(lambda k: " ".join(k) if isinstance(k, list) else str(k))
                self._fill_table(df2)
            except Exception as e:
                print("Error llenando tabla desde JSON:", e)

    # ----------------- Plot / Table helpers -----------------
    def _plot_top_candidates(self, df_sorted: pd.DataFrame, topN: int = 30):
        topN = min(topN, len(df_sorted))
        top_df = df_sorted.head(topN).iloc[::-1] 

        self.hist_canvas.axes.clear()
        y_positions = np.arange(len(top_df))
        self.hist_canvas.axes.barh(y_positions, top_df['counter'])
        self.hist_canvas.axes.set_yticks(y_positions)
        self.hist_canvas.axes.set_yticklabels(top_df['key'].astype(str))
        self.hist_canvas.axes.set_xlabel("Counter")
        self.hist_canvas.axes.set_title(f"Top {topN} candidatos (por |counter|)")
        self.hist_canvas.draw()

    def _plot_corr_heatmap(self, corr: np.ndarray):
        self.heat_canvas.axes.clear()
        im = self.heat_canvas.axes.imshow(corr, interpolation='nearest', aspect='auto')
        self.heat_canvas.axes.set_title("Correlation matrix (S-box)")
        self.heat_canvas.axes.set_xlabel("Output mask")
        self.heat_canvas.axes.set_ylabel("Input mask")
        self.heat_canvas.figure.colorbar(im, ax=self.heat_canvas.axes)
        self.heat_canvas.draw()

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
