from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QSizePolicy
)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD")
        self.setGeometry(100, 100, 1100, 700)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Barra superior
        navbar = QFrame()
        navbar.setStyleSheet("background-color: #14406A;")
        navbar.setFixedHeight(60)

        nav_layout = QHBoxLayout(navbar)
        nav_layout.setContentsMargins(20, 0, 20, 0)
        nav_layout.setSpacing(20)

        logo = QLabel("CryptJAD")
        logo.setStyleSheet("color: white; font-weight: bold; font-size: 20px;")
        nav_layout.addWidget(logo)

        for name in ["Inicio", "About Us", "Servicios", "Contacto"]:
            btn = QPushButton(name)
            btn.setStyleSheet("color: white; background-color: transparent; border: none; font-size: 15px;")
            nav_layout.addWidget(btn)

        nav_layout.addStretch()

        for name in ["Inicio", "Búsqueda", "Filtros"]:
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1E5580;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 10px;
                    font-weight: bold;
                }
            """)
            nav_layout.addWidget(btn)

        id_btn = QPushButton("ID")
        id_btn.setStyleSheet("""
            QPushButton {
                background-color: #D63333;
                color: white;
                padding: 10px 20px;
                border-radius: 10px;
                font-weight: bold;
            }
        """)
        nav_layout.addWidget(id_btn)

        main_layout.addWidget(navbar)

        # Contenido principal con panel lateral
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)

        # Panel lateral
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #F8F8F8; border-right: 1px solid #ccc;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        sidebar_layout.setContentsMargins(20, 20, 0, 0)

        sidebar_title = QLabel("Opciones de navegación")
        sidebar_title.setFont(QFont("Arial", 10, QFont.Weight.Normal))
        sidebar_layout.addWidget(sidebar_title)

        for opt in ["Opción 1", "Opción 2", "Opción 3"]:
            lbl = QLabel(opt)
            sidebar_layout.addWidget(lbl)

        content_layout.addWidget(sidebar)

        # Panel principal central
        center_frame = QFrame()
        center_layout = QVBoxLayout(center_frame)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        center_layout.setContentsMargins(0, 60, 0, 0)

        welcome = QLabel("BIENVENIDO")
        welcome.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        center_layout.addWidget(welcome)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(40)
        buttons_layout.setContentsMargins(0, 40, 0, 0)

        for name in ["Tus proyectos", "Crear nuevo proyecto"]:
            btn = QPushButton(name)
            btn.setFixedSize(200, 50)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1E5580;
                    color: white;
                    border-radius: 12px;
                    font-weight: bold;
                }
            """)
            buttons_layout.addWidget(btn)

        center_layout.addLayout(buttons_layout)

        content_layout.addWidget(center_frame)

        main_layout.addLayout(content_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
