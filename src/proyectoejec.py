from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QComboBox, QSpinBox,
    QTextEdit, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import sys

class CryptoDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD")
        self.setGeometry(100, 100, 1000, 700)
        #self.setStyleSheet(STYLE_SHEET)
        self.setStyleSheet(open("styletry.qss", "r").read())
        self.setupUI()

    def setupUI(self):
        main_layout = QVBoxLayout()

        # --- Barra Superior ---
        header = QHBoxLayout()
        header_frame = QFrame()
        header_frame.setObjectName("header")
        header_layout = QHBoxLayout(header_frame)

        logo = QLabel("CryptJAD")
        logo.setObjectName("logo")
        header_layout.addWidget(logo)

        header_layout.addStretch()
        for name in ["Inicio", "About Us", "Servicios", "Contacto"]:
            btn = QPushButton(name)
            header_layout.addWidget(btn)

        user_btn = QPushButton("ID")
        user_btn.setObjectName("userButton")
        header_layout.addWidget(user_btn)

        main_layout.addWidget(header_frame)

        # --- Sección Principal ---
        main_section = QFrame()
        main_section.setObjectName("mainSection")
        section_layout = QVBoxLayout(main_section)

        title = QLabel("Proyecto 6")
        title.setFont(QFont("Arial", 18))
        section_layout.addWidget(title)

        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("Algoritmo"), 0, 0)
        self.algorithms = QComboBox()
        self.algorithms.addItems(["Selecciona...", "AES", "DES", "3DES", "Present", "SHA-256"])
        form_layout.addWidget(self.algorithms, 0, 1)

        form_layout.addWidget(QLabel("Parámetros"), 1, 0)
        form_layout.addWidget(QLabel("No. de rondas"), 2, 0)
        self.rounds_spin = QSpinBox()
        self.rounds_spin.setRange(1, 20)
        form_layout.addWidget(self.rounds_spin, 2, 1)
        form_layout.addWidget(QLabel("S-boxes"), 3, 0)
        self.sboxes_spin = QSpinBox()
        self.sboxes_spin.setRange(1, 10)
        form_layout.addWidget(self.sboxes_spin, 3, 1)

        form_layout.addWidget(QLabel("Análisis Lineal"), 0, 2)
        form_layout.addWidget(QLabel("No. de rondas"), 1, 2)
        self.linear_rounds = QSpinBox()
        self.linear_rounds.setRange(1, 10)
        form_layout.addWidget(self.linear_rounds, 1, 3)
        form_layout.addWidget(QLabel("No. de muestras"), 2, 2)
        self.linear_samples = QSpinBox()
        self.linear_samples.setRange(100, 100000)
        form_layout.addWidget(self.linear_samples, 2, 3)
        linear_btn = QPushButton("Generar análisis lineal")
        linear_btn.clicked.connect(lambda: print("[INFO] Análisis lineal ejecutado"))
        form_layout.addWidget(linear_btn, 3, 3)

        form_layout.addWidget(QLabel("Análisis Diferencial"), 0, 4)
        form_layout.addWidget(QLabel("No. de rondas"), 1, 4)
        self.diff_rounds = QSpinBox()
        self.diff_rounds.setRange(1, 10)
        form_layout.addWidget(self.diff_rounds, 1, 5)
        form_layout.addWidget(QLabel("No. de muestras"), 2, 4)
        self.diff_samples = QSpinBox()
        self.diff_samples.setRange(100, 100000)
        form_layout.addWidget(self.diff_samples, 2, 5)
        diff_btn = QPushButton("Generar análisis diferencial")
        diff_btn.clicked.connect(lambda: print("[INFO] Análisis diferencial ejecutado"))
        form_layout.addWidget(diff_btn, 3, 5)

        section_layout.addLayout(form_layout)
        main_layout.addWidget(main_section)

        # --- Proyectos Recientes ---
        recent_title = QLabel("Proyectos recientes")
        recent_title.setFont(QFont("Arial", 16))
        main_layout.addWidget(recent_title)

        recent_frame = QFrame()
        recent_frame.setObjectName("similarSection")
        recent_layout = QHBoxLayout(recent_frame)

        for i in range(4):
            card = QFrame()
            card.setObjectName("similarImage")
            card_layout = QVBoxLayout(card)
            card_layout.addWidget(QLabel("Parámetros"))
            card_layout.addWidget(QLabel("Resultados"))
            project_title = QLabel(f"Proyecto {i+2}")
            project_title.setObjectName("similarTitle")
            card_layout.addWidget(project_title)
            recent_layout.addWidget(card)

        main_layout.addWidget(recent_frame)
        self.setLayout(main_layout)

        # --- Firebase (comentado) ---
        # import firebase_admin
        # from firebase_admin import credentials, firestore
        # cred = credentials.Certificate("path/to/your/firebase-key.json")
        # firebase_admin.initialize_app(cred)
        # db = firestore.client()
        # proyectos = db.collection('proyectos').get()
        # for p in proyectos:
        #     print(p.to_dict())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CryptoDashboard()
    window.show()
    sys.exit(app.exec())
