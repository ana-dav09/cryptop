import sys
from PyQt6 import QtWidgets, QtGui, QtCore

class InicioWindow(QtWidgets.QWidget):
    # Señales personalizadas para notificar a la ventana principal sobre la navegación
    login_requested = QtCore.pyqtSignal()
    register_requested = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD - Analizador Criptográfico")
        self.setGeometry(100, 100, 1000, 700) # Ajusta el tamaño según tu diseño
        self.init_ui()


    def init_ui(self):
        # Layout principal para la ventana de inicio
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0) # Quitar márgenes si el header es de borde a borde

        # --- Header (Barra Superior) ---
        header_frame = QtWidgets.QFrame(self)
        header_frame.setStyleSheet("background-color: #2C3E50;") # Color de fondo azul oscuro
        header_layout = QtWidgets.QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10) # Margen interno

        # Logo del sistema [cite: 5]
        logo_label = QtWidgets.QLabel("CryptJAD")
        logo_label.setStyleSheet("color: white; font-weight: bold; font-size: 20px;")
        header_layout.addWidget(logo_label)

        # Botones de navegación superior (pueden ser QPushButtons o QLabels con eventos de clic)
        nav_buttons_layout = QtWidgets.QHBoxLayout()
        nav_buttons_layout.addStretch(1) # Empuja los botones a la derecha

        header_layout.addLayout(nav_buttons_layout)


        buttons_info = {
            "Iniciar sesión": ("loginButton", self.request_login),
            "Registro": ("registerButton", self.request_register)
        }

        for name, (object_name, callback) in buttons_info.items():
            btn = QtWidgets.QPushButton(name)
            btn.setObjectName(object_name)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #34495E;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color:  #1ABC9C;
                }
            """)
            btn.clicked.connect(callback)
            header_layout.addWidget(btn)



        main_layout.addWidget(header_frame)

        # --- Contenido Central (Analizador criptográfico) ---
        content_layout = QtWidgets.QVBoxLayout()
        content_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter) # Centrar contenido verticalmente
        content_layout.setSpacing(30)

        # Título: 'Analizador criptográfico' [cite: 3]
        title_label = QtWidgets.QLabel("Analizador criptográfico")
        title_label.setFont(QtGui.QFont("Arial", 28, QtGui.QFont.Weight.Bold))
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title_label)

        subtitle_label = QtWidgets.QLabel("¿Tu algoritmo es seguro?")
        subtitle_label.setFont(QtGui.QFont("Arial", 18))
        subtitle_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(subtitle_label)

        # Botón "Regístrate" grande [cite: 7]
        register_main_btn = QtWidgets.QPushButton("Regístrate")
        register_main_btn.setFixedSize(200, 50)
        register_main_btn.setFont(QtGui.QFont("Arial", 16))
        register_main_btn.setStyleSheet("""
            QPushButton {
                background-color: #e42c1f; /* Naranja */
                color: white;
                border-radius: 25px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #E76F51; /* Naranja más oscuro al pasar el ratón */
            }
        """)
        register_main_btn.clicked.connect(self.request_register) # Conecta al mismo método
        content_layout.addWidget(register_main_btn, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        # Sección de "Personaliza" con imagen (Placeholder) [cite: 3]
        personalize_frame = QtWidgets.QFrame(self)
        personalize_frame.setFixedSize(500, 300)
        personalize_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #2A9D8F; /* Verde azulado */
                border-radius: 10px;
                background-color: #F8F9FA; /* Fondo claro */
            }
        """)
        personalize_layout = QtWidgets.QVBoxLayout(personalize_frame)
        personalize_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        image_placeholder = QtWidgets.QLabel("Imagen")
        image_placeholder.setFixedSize(150, 100)
        image_placeholder.setStyleSheet("background-color: #D3D3D3; border: 1px solid #A9A9A9; text-align: center;")
        image_placeholder.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        personalize_layout.addWidget(image_placeholder, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        personalize_title = QtWidgets.QLabel("Personaliza")
        personalize_title.setFont(QtGui.QFont("Arial", 18, QtGui.QFont.Weight.Bold))
        personalize_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        personalize_layout.addWidget(personalize_title)

        personalize_subtitle = QtWidgets.QLabel("Modifica parámetros para un algoritmo preestablecido")
        personalize_subtitle.setFont(QtGui.QFont("Arial", 12))
        personalize_subtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        personalize_layout.addWidget(personalize_subtitle)

        content_layout.addWidget(personalize_frame, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        # Botones de navegación inferiores (flechas) [cite: 3]
        bottom_nav_layout = QtWidgets.QHBoxLayout()
        left_arrow_btn = QtWidgets.QPushButton("<")
        right_arrow_btn = QtWidgets.QPushButton(">")
        left_arrow_btn.setFixedSize(200, 60)
        right_arrow_btn.setFixedSize(200, 60)
        left_arrow_btn.setFont(QtGui.QFont("Arial", 24))
        right_arrow_btn.setFont(QtGui.QFont("Arial", 24))
        left_arrow_btn.setStyleSheet("""
            QPushButton {
                background-color: #219EBC; /* Azul */
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #167DAB;
            }
        """)
        right_arrow_btn.setStyleSheet("""
            QPushButton {
                background-color: #219EBC;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #167DAB;
            }
        """)
        bottom_nav_layout.addWidget(left_arrow_btn, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        bottom_nav_layout.addSpacing(50) # Espacio entre flechas
        bottom_nav_layout.addWidget(right_arrow_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        content_layout.addLayout(bottom_nav_layout)

        # Título "¿Qué deseas hacer?" [cite: 3]
        what_to_do_label = QtWidgets.QLabel("¿Qué deseas hacer?")
        what_to_do_label.setFont(QtGui.QFont("Arial", 24, QtGui.QFont.Weight.Bold))
        what_to_do_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(what_to_do_label)

        main_layout.addLayout(content_layout)

    # --- Métodos para emitir señales de navegación ---
    def request_login(self):
        """Emite una señal para indicar que se desea ir a la pantalla de login."""
        self.login_requested.emit()

    def request_register(self):
        """Emite una señal para indicar que se desea ir a la pantalla de registro."""
        self.register_requested.emit()
