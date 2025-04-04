import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QSizePolicy, QStackedWidget
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect
from PyQt6.QtGui import QFont, QPixmap

class SidebarMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú de Navegación Lateral")
        self.setGeometry(100, 100, 900, 600)
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
        
        # 📌 Organización
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.menu_button)

    def toggle_sidebar(self):
        """Muestra u oculta el menú con animación."""
        width = self.sidebar.width()
        new_width = 200 if width == 0 else 0
        
        self.animation = QPropertyAnimation(self.sidebar, b"geometry")
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


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD")
        self.setGeometry(100, 100, 900, 600)
        self.initUI()
        self.load_stylesheet("style.qss")

    def initUI(self):
        main_layout = QVBoxLayout()
        
        # 🟦 NAVBAR
        navbar = QFrame()
        navbar.setObjectName("navbar")
        navbar_layout = QHBoxLayout()
        navbar_layout.setContentsMargins(10, 10, 10, 10)
        navbar_layout.setSpacing(15)

        logo = QLabel("CryptJAD")
        logo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        logo.setObjectName("logo")
        navbar_layout.addWidget(logo)

        sections = ["Home", "About", "Services", "Contact"]
        for section in sections:
            btn = QPushButton(section)
            btn.setObjectName("navButton")
            navbar_layout.addWidget(btn)

        navbar_layout.addStretch()

        sign_in = QPushButton("Sign In")
        sign_in.setObjectName("signIn")
        navbar_layout.addWidget(sign_in)

        sign_up = QPushButton("Sign Up")
        sign_up.setObjectName("signUp")
        navbar_layout.addWidget(sign_up)

        navbar.setLayout(navbar_layout)

        # 🟦 ENCABEZADO
        header_layout = QVBoxLayout()
        header = QLabel("Analizador criptográfico")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subheader = QLabel("¿Tu algoritmo es seguro?\nDescúbrelo con nosotros")
        subheader.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_layout.addWidget(header)
        header_layout.addWidget(subheader)

        # 🔹 CARRUSEL
        self.carousel = QStackedWidget()
        self.carousel.setObjectName("carousel")

        self.cards = []
        items = [
            ("Personaliza", "Modifica parámetros de un algoritmo precargado", "img1.png"),
            ("Crea", "Diseña un algoritmo propio", "img2.png"),
            ("Visualiza", "Observa los resultados de los análisis", "img3.png"),
        ]

        for title, desc, img_path in items:
            card = self.create_card(title, desc, img_path)
            self.carousel.addWidget(card)
            self.cards.append(card)

        btn_prev = QPushButton("◀")
        btn_next = QPushButton("▶")
        btn_prev.setObjectName("carouselBtn")
        btn_next.setObjectName("carouselBtn")
        btn_prev.setFixedSize(20, 20)
        btn_next.setFixedSize(20, 20)

        btn_prev.clicked.connect(self.prev_card)
        btn_next.clicked.connect(self.next_card)

        carousel_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_prev)
        btn_layout.addWidget(btn_next)
        
        carousel_layout.addWidget(self.carousel, alignment=Qt.AlignmentFlag.AlignCenter)
        carousel_layout.addLayout(btn_layout)

        # 🟦 SECCIÓN "¿Qué deseas hacer?"
        whattodo_label = QLabel("¿Qué deseas hacer?")
        whattodo_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        whattodo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        whattodo_layout = QVBoxLayout()
        whattodo_layout.addWidget(whattodo_label)

        # 🟦 ORGANIZACIÓN DEL LAYOUT
        main_layout.addWidget(navbar)
        self.sidebar = SidebarMenu()
        main_layout.addWidget(self.sidebar)
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(carousel_layout) 
        main_layout.addSpacing(20)
        main_layout.addLayout(whattodo_layout)


        self.setLayout(main_layout)

    def create_card(self, title, desc, img_path):
        """ Crea una tarjeta con título, descripción e imagen """
        card = QWidget()
        layout = QVBoxLayout(card)

        img_label = QLabel()
        pixmap = QPixmap(img_path).scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(title)
        desc_label = QLabel(desc)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card.setObjectName("carouselCard")
        title_label.setObjectName("carouselTitle")
        desc_label.setObjectName("carouselDesc")

        layout.addWidget(img_label)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        return card

    def next_card(self):
        """ Mueve al siguiente elemento del carrusel """
        current_index = self.carousel.currentIndex()
        next_index = (current_index + 1) % len(self.cards)
        self.carousel.setCurrentIndex(next_index)

    def prev_card(self):
        """ Mueve al elemento anterior del carrusel """
        current_index = self.carousel.currentIndex()
        prev_index = (current_index - 1) % len(self.cards)
        self.carousel.setCurrentIndex(prev_index)

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
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
