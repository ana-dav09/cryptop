from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Critoanalisis")
        self.setGeometry(100, 100, 900, 600)

        # Aplicar el estilo desde el archivo QSS
        self.setStyleSheet(open("styletry.qss", "r").read())

        # --- Barra superior ---
        header = QHBoxLayout()
        header_container = QWidget()
        header_container.setObjectName("header")

        logo = QLabel("LOGO")
        logo.setObjectName("logo")

        menu_btn = QPushButton("Menú")
        search_btn = QPushButton("Búsqueda")
        filter_btn = QPushButton("Filtros")
        user_btn = QPushButton("ID")
        user_btn.setObjectName("userButton")

        header.addWidget(logo)
        header.addStretch()
        header.addWidget(menu_btn)
        header.addWidget(search_btn)
        header.addWidget(filter_btn)
        header.addWidget(user_btn)

        header_container.setLayout(header)

        # --- Sección Principal (Template) ---
        main_layout = QGridLayout()
        main_container = QWidget()
        main_container.setObjectName("mainSection")

        text_section = QLabel("Texto")
        text_section.setObjectName("textBlock")

        image_detail = QLabel("Imagen\nDescripción")
        image_detail.setObjectName("imageDetail")

        view_btn = QPushButton("Visualizar proyecto")
        view_btn.setObjectName("viewButton")

        explore_btn = QPushButton("Explorar otros proyectos")

        image_container = QVBoxLayout()
        image_container.addWidget(image_detail)
        image_container.addWidget(view_btn)
        image_container.addWidget(explore_btn)

        main_layout.addWidget(text_section, 0, 0)
        main_layout.addLayout(image_container, 0, 1)

        main_container.setLayout(main_layout)

        # --- Plantillas Similares ---
        similar_layout = QHBoxLayout()
        similar_container = QWidget()
        similar_container.setObjectName("similarSection")

        for i in range(4):
            item = QVBoxLayout()
            img = QLabel(f"Imagen\nDescripcion {i+1}")
            img.setObjectName("similarImage")

            title = QLabel(f"Nombre proyecto\nCifrado {i+1}")
            title.setObjectName("similarTitle")

            item.addWidget(img)
            item.addWidget(title)
            similar_layout.addLayout(item)

        similar_container.setLayout(similar_layout)

        # --- Layout Principal ---
        layout = QVBoxLayout()
        layout.addWidget(header_container)
        layout.addWidget(QLabel("Template"))
        layout.addWidget(main_container)
        layout.addWidget(QLabel("Otros cifrados"))
        layout.addWidget(similar_container)

        self.setLayout(layout)

# Ejecutar aplicación
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
