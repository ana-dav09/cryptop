# cryptjad_attack_window.py
import subprocess, json, sys, os
from PyQt6 import QtWidgets, QtGui, QtCore

# Importamos la barra lateral (ajustar la ruta si está en otra carpeta)
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from barra_lateral import SidebarWidget


class AttackWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD - Ataques Criptoanalíticos")
        self.resize(1100, 650)

        # Layout principal con barra lateral
        mainLayout = QtWidgets.QHBoxLayout(self)

        # Barra lateral
        self.sidebar = SidebarWidget(self)
        mainLayout.addWidget(self.sidebar)

        # Contenido principal
        contentLayout = QtWidgets.QVBoxLayout()

        # Título
        title = QtWidgets.QLabel("Módulo de Ataques Criptoanalíticos")
        title.setFont(QtGui.QFont("Arial", 18, QtGui.QFont.Weight.Bold))
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        contentLayout.addWidget(title)

        # Botones de ataque
        buttonLayout = QtWidgets.QHBoxLayout()

        self.diffButton = QtWidgets.QPushButton("Ejecutar Ataque Diferencial")
        self.diffButton.setStyleSheet("padding: 10px; font-size: 14px;")
        self.diffButton.clicked.connect(self.run_differential)

        self.linearButton = QtWidgets.QPushButton("Ejecutar Ataque Lineal")
        self.linearButton.setStyleSheet("padding: 10px; font-size: 14px;")
        self.linearButton.clicked.connect(self.run_linear)

        buttonLayout.addWidget(self.diffButton)
        buttonLayout.addWidget(self.linearButton)

        contentLayout.addLayout(buttonLayout)

        # Cuadro de resultados
        self.resultBox = QtWidgets.QTextEdit()
        self.resultBox.setReadOnly(True)
        self.resultBox.setStyleSheet("background-color: #f5f5f5; font-family: Consolas; font-size: 13px;")
        contentLayout.addWidget(self.resultBox)

        mainLayout.addLayout(contentLayout)

    # -------------------------------
    # Ejecutar ataque diferencial
    # -------------------------------
    def run_differential(self):
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
                self.resultBox.setText(msg)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error ejecutando ataque", str(e))
            print(str(e))
    # -------------------------------
    # Ejecutar ataque lineal
    # -------------------------------
    def run_linear(self):
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
            self.resultBox.setText(msg)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error ejecutando ataque lineal", str(e))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AttackWindow()
    window.show()
    sys.exit(app.exec())
