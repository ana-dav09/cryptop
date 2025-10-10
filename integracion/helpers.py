import os, sys, json, subprocess, time
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6 import QtWidgets

from PyQt6 import QtWidgets, QtGui, QtCore
from matplotlib.table import Table
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))


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

