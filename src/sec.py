import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect
from PyQt6.QtGui import QFont


class SidebarMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú de Navegación Lateral")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()
        self.load_stylesheet("style.qss")

    def initUI(self):
        self.main_layout = QHBoxLayout(self)
        
        # 🟦 Menú lateral (oculto por defecto)
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(0)  # Inicialmente oculto
        self.sidebar_layout = QVBoxLayout()
        
        self.sidebar_label = QLabel("Menú")
        self.sidebar_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.sidebar_layout.addWidget(self.sidebar_label)
        
        self.buttons = []
        for text in ["Inicio", "Análisis", "Configuración", "Cerrar Sesión"]:
            btn = QPushButton(text)
            btn.setObjectName("menuButton")
            self.sidebar_layout.addWidget(btn)
            self.buttons.append(btn)

        self.sidebar_layout.addStretch()
        self.sidebar.setLayout(self.sidebar_layout)
        
        # 🟦 Botón de menú hamburguesa
        self.menu_button = QPushButton("☰")
        self.menu_button.setObjectName("menuButton")
        self.menu_button.clicked.connect(self.toggle_sidebar)
        
        # 🟦 Contenido principal
        self.main_content = QStackedWidget()
        self.main_content.setObjectName("mainContent")
        self.main_content.addWidget(QLabel("Bienvenido a CryptJAD"))
        
        # 🟦 Animación
        self.animation = QPropertyAnimation(self.sidebar, b"geometry")
        
        # 📌 Organización
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.menu_button)
        self.main_layout.addWidget(self.main_content)
        self.setLayout(self.main_layout)
        
    def toggle_sidebar(self):
        """Muestra u oculta el menú con animación."""
        width = self.sidebar.width()
        new_width = 200 if width == 0 else 0
        
        self.animation.setDuration(300)
        self.animation.setStartValue(QRect(self.sidebar.x(), self.sidebar.y(), width, self.sidebar.height()))
        self.animation.setEndValue(QRect(self.sidebar.x(), self.sidebar.y(), new_width, self.sidebar.height()))
        self.animation.start()

    def load_stylesheet(self, file_path):
        """Carga una hoja de estilos externa."""
        try:
            with open(file_path, "r") as file:
                qss = file.read()
                self.setStyleSheet(qss)
        except FileNotFoundError:
            print(f"❌ No se encontró {file_path}")
        except Exception as e:
            print(f"❌ Error al cargar el QSS: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SidebarMenu()
    window.show()
    sys.exit(app.exec())
