import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QSizePolicy, QMainWindow
)
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor
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
        
        # 🟦 NAVBAR - Barra de navegación superior (actualizada)
        navbar = QFrame()
        navbar.setObjectName("navbar")
        navbar_layout = QHBoxLayout()
        navbar_layout.setContentsMargins(10, 5, 10, 5)
        navbar_layout.setSpacing(10)

        # Logo
        logo = QLabel("CryptJAD")
        logo.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        logo.setObjectName("logo")
        navbar_layout.addWidget(logo)

        # Secciones de navegación
        sections = ["Home", "About", "Services", "Contact"]
        for section in sections:
            btn = QPushButton(section)
            btn.setObjectName("navButton")
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
            navbar_layout.addWidget(btn)

        # Espaciador para empujar los botones de la derecha
        navbar_layout.addStretch()

        # Botón de Sign In
        sign_in = QPushButton("Sign In")
        sign_in.setObjectName("signIn")
        
        navbar_layout.addWidget(sign_in)

        # Botón de Sign Up
        sign_up = QPushButton("Sign Up")
        sign_up.setObjectName("signUp")
        navbar_layout.addWidget(sign_up)


        # Animaciones para ambos botones
        self.apply_animation(sign_in)
        self.apply_animation(sign_up)

        navbar.setLayout(navbar_layout)

        # 🟦 ENCABEZADO
        header = QLabel("Analizador criptográfico")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subheader = QLabel("¿Tu algoritmo es seguro?")
        subheader.setAlignment(Qt.AlignmentFlag.AlignCenter)

        register_button = QPushButton("Register")
        register_button.setObjectName("botonReg")
        register_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        header_layout = QVBoxLayout()
        header_layout.addWidget(header)
        header_layout.addWidget(subheader)
        header_layout.addWidget(register_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # 🟦 FUNCIONES
        whattodo_label = QLabel("¿Qué deseas hacer?")
        whattodo_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        whattodo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        whattodo_layout = QVBoxLayout()
        whattodo_layout.addWidget(whattodo_label)

        # 🟦 CONTENIDO PRINCIPAL
        content = QLabel("Bienvenido a CryptJAD")
        content.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Agregar widgets al layout principal
        main_layout.addWidget(navbar)      # Barra de navegación actualizada
        main_layout.addWidget(content)       # Contenido principal
        main_layout.addLayout(header_layout) # Encabezado
        main_layout.addSpacing(20)
        main_layout.addLayout(whattodo_layout)

        self.setLayout(main_layout)

    def apply_animation(self, button):
        # Crear una animación personalizada para el color de fondo
        self.animation = QPropertyAnimation(button, b"styleSheet")
        self.animation.setDuration(10000)  # Duración de la animación
        self.animation.setStartValue("QPushButton { background-color: white; color: navy; }")
        self.animation.setEndValue("QPushButton { background-color: navy; color: white; }")
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Configurar eventos de hover
        button.enterEvent = self.create_enter_event(self.animation, button)
        button.leaveEvent = self.create_leave_event(self.animation, button)

    def create_enter_event(self, animation, button):
        def enter_event(event):
            animation.start()
        return enter_event

    def create_leave_event(self, animation, button):
        def leave_event(event):
            animation.stop()
            # Restablecer el estilo cuando el ratón salga
            button.setStyleSheet("QPushButton { background-color: white; color: navy; }")
        return leave_event

    def create_leave_event(self, animation, button):
        def leave_event(event):
            animation.stop()
            button.setStyleSheet("""
                QPushButton {
                    border: 2px solid navy;
                    background-color: white;
                    color: navy;
                    padding: 6px 15px;
                    border-radius: 5px;
                }
            """)
        return leave_event
    
    def resizeEvent(self, event):
        """Detecta cambios en el tamaño de la ventana y ajusta la UI."""
        width = self.width()
        if width < 600:
            self.setStyleSheet("QWidget { font-size: 12px; }")  # Fuente menor en pantallas pequeñas
        else:
            self.setStyleSheet("QWidget { font-size: 14px; }")  # Fuente normal en pantallas grandes
        super().resizeEvent(event)

    def load_stylesheet(self, file_path):
        """Carga una hoja de estilos externa."""
        try:
            with open(file_path, "r") as file:
                qss = file.read()
                print("✅ Hoja de estilos cargada correctamente")
                self.setStyleSheet(qss)
        except FileNotFoundError:
            print(f"❌ Error: No se encontró el archivo {file_path}")
        except Exception as e:
            print(f"❌ Error al cargar la hoja de estilos: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Se puede cargar la hoja de estilos desde el archivo style.qss
    try:
        app.setStyleSheet(open("style.qss", "r").read())
    except Exception as e:
        print(f"❌ Error al cargar style.qss: {e}")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
