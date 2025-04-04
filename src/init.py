import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()
        self.load_stylesheet("style.qss")

    def initUI(self):
        main_layout = QVBoxLayout()

        #Encabezado
        header = QLabel("Analizador criptográfico")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subheader = QLabel("¿Tu algoritmo es seguro?")
        subheader.setAlignment(Qt.AlignmentFlag.AlignCenter)

        register_button = QPushButton("Register")

        # Funciones
        whattodo_label = QLabel("¿Qué deseas hacer?")
        whattodo_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        whattodo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layouts
        header_layout = QVBoxLayout()
        header_layout.addWidget(header)
        header_layout.addWidget(subheader)
        header_layout.addWidget(register_button, alignment=Qt.AlignmentFlag.AlignCenter)

        whattodo_layout = QVBoxLayout()
        whattodo_layout.addWidget(whattodo_label)

        # Segmentar Main Layout
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(whattodo_layout)

        self.setLayout(main_layout)

    def load_stylesheet(self, file_path):
        """Carga una hoja de estilos externa."""
        try:
            with open(file_path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {file_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
