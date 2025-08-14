import sys
import json, os, subprocess
from firebase_serv import register_user, get_user
from PyQt6 import QtWidgets, QtGui, QtCore

USER_DB = "users.json"


def load_users():
    """ Carga la base de datos de usuarios desde el archivo JSON """
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    """ Guarda la base de datos de usuarios en el archivo JSON """
    with open(USER_DB, "w") as file:
        json.dump(users, file, indent=4)


class RegistroWindow(QtWidgets.QWidget):
    # Señales para la navegación:
    # go_to_login: para cuando el registro es exitoso y se debe ir al login
    # go_to_inicio: para el botón de "Volver a inicio"
    go_to_login = QtCore.pyqtSignal()
    go_to_inicio = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD - Registro")
        self.setGeometry(100, 100, 1000, 700) # Mantener el mismo tamaño para coherencia
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

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
            "Inicio": ("inicioButton", self.go_to_inicio.emit),
            "Iniciar sesión": ("loginButton", self.go_to_login.emit)
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

        # --- Contenido Central: Formulario de Registro ---
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.addStretch(1) # Espacio a la izquierda del logo
        
        # Área para el LOGO grande (izquierda)
        logo_area = QtWidgets.QLabel("LOGO")
        logo_area.setFixedSize(300, 300) # Ajusta el tamaño según tu diseño
        logo_area.setStyleSheet("background-color: black; color: white; font-size: 36px; text-align: center;")
        logo_area.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(logo_area, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addSpacing(50) # Espacio entre logo y formulario

        # Formulario de Crear Cuenta (derecha)
        form_frame = QtWidgets.QFrame(self)
        form_frame.setFixedSize(400, 500) # Ajusta el tamaño del formulario
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
            }
        """)
        form_layout = QtWidgets.QVBoxLayout(form_frame)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(15)

        form_title = QtWidgets.QLabel("Crear cuenta")
        form_title.setFont(QtGui.QFont("Arial", 28, QtGui.QFont.Weight.Bold))
        form_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        form_layout.addWidget(form_title)

        # Campos de texto (QLineEdit)
        self.email_input = self._create_input("Correo")
        self.names_input = self._create_input("Nombres")
        self.lastnames_input = self._create_input("Apellidos")
        self.password_input = self._create_input("Contraseña", echo_mode=QtWidgets.QLineEdit.EchoMode.Password)
        self.confirm_password_input = self._create_input("Confirmación de Contraseña", echo_mode=QtWidgets.QLineEdit.EchoMode.Password)
        self.dob_input = self._create_input("Fecha de nacimiento") # O QDateEdit

        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.names_input)
        form_layout.addWidget(self.lastnames_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.confirm_password_input)
        form_layout.addWidget(self.dob_input)

        form_layout.addSpacing(20)

        # Botón "Crear cuenta"
        create_account_btn = QtWidgets.QPushButton("Crear cuenta")
        create_account_btn.setFixedSize(180, 50)
        create_account_btn.setFont(QtGui.QFont("Arial", 16))
        create_account_btn.setStyleSheet("""
            QPushButton {
                background-color: #219EBC; /* Azul */
                color: white;
                border-radius: 25px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #167DAB;
            }
        """)
        create_account_btn.clicked.connect(self.register_account)
        form_layout.addWidget(create_account_btn, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        form_layout.addStretch(1) # Empuja los elementos hacia arriba

        content_layout.addWidget(form_frame, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        content_layout.addStretch(1) # Espacio a la derecha del formulario
        main_layout.addLayout(content_layout)

        # "Más opciones" (si lo necesitas, por ahora solo un QLabel)
        more_options_label = QtWidgets.QLabel("Más opciones")
        more_options_label.setFont(QtGui.QFont("Arial", 12))
        more_options_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(more_options_label)

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


    def register_account(self):
        email = self.email_input.text()
        names = self.names_input.text()
        lastnames = self.lastnames_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        dob = self.dob_input.text()

        if not email or not password or not names or not lastnames or not confirm_password:
            QtWidgets.QMessageBox.warning(self, "Error de Registro", "Por favor, complete todos los campos.")
            return

        if password != confirm_password:
            QtWidgets.QMessageBox.warning(self, "Error de Contraseña", "Las contraseñas no coinciden.")
            return

        # Verificar si ya existe en Firebase
        if get_user(email):
            QtWidgets.QMessageBox.warning(self, "Error", "Este correo ya está registrado.")
            return

        # Guardar en Firebase
        register_user(email, password, names, lastnames, dob)

        QtWidgets.QMessageBox.information(self, "Éxito", "Registro exitoso. ¡Ahora puedes iniciar sesión!")
        self.go_to_login.emit()
