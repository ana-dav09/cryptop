import subprocess, json, sys, os
from PyQt6 import QtWidgets, QtGui, QtCore
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from barra_lateral import SidebarWidget

class DifferentialAttackWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD - Ataque Diferencial BabyAES")
        self.setMinimumSize(1000, 600)

        # === Layout principal (sidebar + contenido) ===
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Barra lateral
        self.sidebar = SidebarWidget()
        main_layout.addWidget(self.sidebar)

        # === Contenido central ===
        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        # Header
        header = QtWidgets.QLabel("⚡ Ataque Diferencial sobre BabyAES")
        header.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Weight.Bold))
        header.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #1E293B;")  # gris oscuro elegante
        content_layout.addWidget(header)

        # Card de ejecución
        card = QtWidgets.QFrame()
        card.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background: #FFFFFF;
                border-radius: 20px;
                padding: 25px;
                border: 1px solid #E2E8F0;
            }
        """)
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setSpacing(15)

        # Botón ejecutar ataque
        self.runButton = QtWidgets.QPushButton("▶ Ejecutar ataque diferencial")
        self.runButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.runButton.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                font-size: 15px;
                font-weight: bold;
                border-radius: 14px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2C5F9E;
            }
        """)
        self.runButton.clicked.connect(self.run_attack)
        card_layout.addWidget(self.runButton)

        # Resultados
        self.resultLabel = QtWidgets.QTextEdit()
        self.resultLabel.setReadOnly(True)
        self.resultLabel.setPlaceholderText("Aquí aparecerán los resultados del ataque diferencial...")
        self.resultLabel.setStyleSheet("""
            QTextEdit {
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
                border-radius: 14px;
                padding: 12px;
                font-family: Consolas, monospace;
                font-size: 13px;
                color: #1E293B;
            }
        """)
        card_layout.addWidget(self.resultLabel)

        content_layout.addWidget(card)
        main_layout.addWidget(content, stretch=1)

    def run_attack(self):
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
                self.resultLabel.setText(msg)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error ejecutando ataque", str(e))
            print(str(e))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DifferentialAttackWindow()
    window.show()
    sys.exit(app.exec())
