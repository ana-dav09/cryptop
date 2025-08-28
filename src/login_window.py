import sys, os, json, subprocess
from PyQt6 import QtWidgets, QtGui, QtCore
import firebase_serv

USER_DB = "users.json"


def load_users():
    """ Carga la base de datos de usuarios desde el archivo JSON """
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as file:
            return json.load(file)
    return {}


class LoginWindow(QtWidgets.QWidget):
    # Señales para la navegación:
    # go_to_dashboard: para cuando el login es exitoso
    # go_to_register: para el enlace "Crear cuenta"
    # go_to_recover_password: para "Olvidé mi contraseña"
    # go_to_inicio: para el botón de "Volver a inicio" (si hay uno explícito)
    go_to_dashboard = QtCore.pyqtSignal()
    go_to_register = QtCore.pyqtSignal()
    go_to_recover_password = QtCore.pyqtSignal()
    go_to_inicio = QtCore.pyqtSignal() # Asumiendo un botón "Volver" implícito o en header

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD - Iniciar Sesión")
        self.setGeometry(100, 100, 1000, 700) # Mantener el mismo tamaño para coherencia
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
            "Inicio": ("loginButton", self.request_login),
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

        # --- Contenido Central: Formulario de Login ---
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.addStretch(1)
        
        # Área para el LOGO grande (izquierda)
        logo_area = QtWidgets.QLabel("LOGO")
        logo_area.setFixedSize(300, 300)
        logo_area.setStyleSheet("background-color: black; color: white; font-size: 36px; text-align: center;")
        logo_area.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(logo_area, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addSpacing(50)

        # Formulario de Inicio de Sesión (derecha)
        form_frame = QtWidgets.QFrame(self)
        form_frame.setFixedSize(400, 350) # Ajusta el tamaño del formulario
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
            }
        """)
        form_layout = QtWidgets.QVBoxLayout(form_frame)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(15)

        form_title = QtWidgets.QLabel("Inicio de sesión")
        form_title.setFont(QtGui.QFont("Arial", 28, QtGui.QFont.Weight.Bold))
        form_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        form_layout.addWidget(form_title)

        # Enlace "Crear cuenta"
        create_account_link = QtWidgets.QLabel("<a href='#'>Crear cuenta</a>")
        create_account_link.setFont(QtGui.QFont("Arial", 12))
        create_account_link.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        create_account_link.setOpenExternalLinks(False) # Para que no abra en navegador
        create_account_link.linkActivated.connect(self.request_register) # Conecta al enlace
        form_layout.addWidget(create_account_link)

        # Campos de texto
        self.email_input = self._create_input("Correo")
        self.password_input = self._create_input("Contraseña", echo_mode=QtWidgets.QLineEdit.EchoMode.Password)

        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.password_input)

        # Enlace "¿Olvidé mi contraseña?"
        forgot_password_link = QtWidgets.QLabel("<a href='#'>Olvidé mi contraseña</a>")
        forgot_password_link.setFont(QtGui.QFont("Arial", 12))
        forgot_password_link.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        forgot_password_link.setOpenExternalLinks(False)
        forgot_password_link.linkActivated.connect(self.go_to_recover_password.emit)
        form_layout.addWidget(forgot_password_link)

        form_layout.addSpacing(20)

        # Botón "Iniciar sesión"
        login_btn = QtWidgets.QPushButton("Iniciar sesión")
        login_btn.setFixedSize(180, 50)
        login_btn.setFont(QtGui.QFont("Arial", 16))
        login_btn.setStyleSheet("""
            QPushButton {
            background-color: #e42c1f;
            color: white;
            border-radius: 25px;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #c9302c;
        }
        """)
        login_btn.clicked.connect(self.login_account)
        form_layout.addWidget(login_btn, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        form_layout.addStretch(1)

        content_layout.addWidget(form_frame, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        content_layout.addStretch(1)
        main_layout.addLayout(content_layout)

        # *** ESTA ES LA CLAVE PARA EL TAMAÑO DEL HEADER ***
        # Añade un stretch al final del layout principal vertical.
        # Esto hará que el espacio restante en la ventana sea tomado por este stretch,
        # obligando a los widgets superiores (como el header) a ocupar solo el espacio necesario.
        main_layout.addStretch(1)

    def _create_input(self, placeholder_text, echo_mode=QtWidgets.QLineEdit.EchoMode.Normal):
        """Helper para crear QLineEdits con estilo."""
        line_edit = QtWidgets.QLineEdit(self)
        line_edit.setPlaceholderText(placeholder_text)
        line_edit.setFixedSize(300, 40)
        line_edit.setFont(QtGui.QFont("Arial", 12))
        line_edit.setEchoMode(echo_mode)
        line_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #D3D3D3;
                border-radius: 5px;
                padding: 5px 10px;
                background-color: #F8F9FA;
            }
            QLineEdit:focus {
                border: 2px solid #219EBC;
            }
        """)
        return line_edit

    def login_account(self):
        """Lógica para iniciar sesión."""
        email = self.email_input.text()
        password = self.password_input.text()

        if not email or not password:
            QtWidgets.QMessageBox.warning(self, "Error de Login", "Por favor, ingrese su correo y contraseña.")
            return

        # --- Aquí iría tu lógica de validación con Firebase ---
        print(f"Intentando iniciar sesión con: {email}")
        # firebase_service.authenticate_user(email, password)

        # Si la validación es exitosa:
        #if email == "test@example.com" and password == "password": # Ejemplo
        #    QtWidgets.QMessageBox.information(self, "Login Exitoso", "¡Bienvenido a CryptJAD!")
        #    self.go_to_dashboard.emit() # Redirige al Dashboard 
        #else:
        #    QtWidgets.QMessageBox.critical(self, "Error de Login", "Correo o contraseña incorrectos.")

        """ Valida el login con la base de datos JSON """
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if firebase_serv.authenticate_user(email, password):
            QtWidgets.QMessageBox.information(self, "Éxito", "Inicio de sesión correcto. ¡Bienvenido!")
            self.go_to_dashboard.emit()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Correo o contraseña incorrectos.")

    # --- Métodos para emitir señales de navegación ---
    def request_login(self):
        """Emite una señal para indicar que se desea ir a la pantalla de login."""
        self.go_to_inicio.emit()

    def request_register(self):
        """Emite una señal para indicar que se desea ir a la pantalla de registro."""
        self.go_to_register.emit()