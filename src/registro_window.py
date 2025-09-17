import sys
import json, os
from firebase_serv import register_user, get_user
from PyQt6 import QtWidgets, QtGui, QtCore

USER_DB = "users.json"


def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(USER_DB, "w") as file:
        json.dump(users, file, indent=4)


class RegistroWindow(QtWidgets.QWidget):
    go_to_login = QtCore.pyqtSignal()
    go_to_inicio = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD - Registro")
        self.setGeometry(100, 100, 1000, 700)
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- HEADER ---
        header_frame = QtWidgets.QFrame(self)
        header_frame.setObjectName("navbar")
        header_layout = QtWidgets.QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)

        logo_label = QtWidgets.QLabel("CryptJAD")
        logo_label.setObjectName("logo")
        header_layout.addWidget(logo_label)
        header_layout.addStretch()

        buttons_info = {
            "Inicio": ("inicioButton", self.go_to_inicio.emit),
            "Iniciar sesión": ("loginButton", self.go_to_login.emit)
        }
        for name, (object_name, callback) in buttons_info.items():
            btn = QtWidgets.QPushButton(name)
            btn.setObjectName(object_name)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(callback)
            header_layout.addWidget(btn)

        main_layout.addWidget(header_frame)

        # --- CONTENIDO CENTRAL ---
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.addStretch(1)

        # Logo o imagen lateral
        logo_area = QtWidgets.QLabel("LOGO")
        logo_area.setFixedSize(280, 280)
        logo_area.setObjectName("sideLogo")
        logo_area.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(logo_area, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        content_layout.addSpacing(60)

        # --- FORMULARIO ---
        form_frame = QtWidgets.QFrame(self)
        form_frame.setObjectName("formCard")
        form_frame.setFixedSize(400, 520)

        form_layout = QtWidgets.QVBoxLayout(form_frame)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(18)

        form_title = QtWidgets.QLabel("Crear cuenta")
        form_title.setObjectName("formTitle")
        form_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        form_layout.addWidget(form_title)

        self.email_input = self._create_input("Correo")
        self.names_input = self._create_input("Nombres")
        self.lastnames_input = self._create_input("Apellidos")
        self.password_input = self._create_input("Contraseña", echo_mode=QtWidgets.QLineEdit.EchoMode.Password)
        self.confirm_password_input = self._create_input("Confirmación de Contraseña", echo_mode=QtWidgets.QLineEdit.EchoMode.Password)
        self.dob_input = self._create_input("Fecha de nacimiento")

        for widget in [
            self.email_input, self.names_input, self.lastnames_input,
            self.password_input, self.confirm_password_input, self.dob_input
        ]:
            form_layout.addWidget(widget)

        form_layout.addSpacing(20)

        create_account_btn = QtWidgets.QPushButton("Crear cuenta")
        create_account_btn.setObjectName("ctaButton")
        create_account_btn.clicked.connect(self.register_account)
        form_layout.addWidget(create_account_btn, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        form_layout.addStretch(1)
        content_layout.addWidget(form_frame, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        content_layout.addStretch(1)
        main_layout.addLayout(content_layout)

        # Footer simple
        footer_label = QtWidgets.QLabel("© 2025 CryptJAD – Todos los derechos reservados")
        footer_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        footer_label.setObjectName("footer")
        main_layout.addWidget(footer_label)

        # --- STYLES ---
        self.setStyleSheet("""
        #navbar { background-color: #2C3E50; }
        #logo { color: white; font-size: 20px; font-weight: bold; }
        QPushButton#inicioButton, QPushButton#loginButton {
            background-color: transparent;
            color: white;
            padding: 6px 14px;
            border-radius: 5px;
        }
        QPushButton#inicioButton:hover, QPushButton#loginButton:hover {
            background-color: #1ABC9C;
        }

        #sideLogo {
            background-color: #000;
            color: white;
            font-size: 28px;
            border-radius: 12px;
        }

        #formCard {
            background-color: white;
            border-radius: 16px;
            border: 1px solid #e0e0e0;
        }
        #formTitle {
            font-size: 26px;
            font-weight: bold;
            margin-bottom: 10px;
        }

        QLineEdit {
            border: 1px solid #D3D3D3;
            border-radius: 6px;
            padding: 8px 12px;
            background-color: #F9FAFB;
            font-size: 14px;
        }
        QLineEdit:focus {
            border: 2px solid #219EBC;
            background-color: #fff;
        }

        QPushButton#ctaButton {
            background-color: #e42c1f;
            color: white;
            border-radius: 25px;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
        }
        QPushButton#ctaButton:hover {
            background-color: #c9302c;
        }

        #footer { font-size: 12px; color: #777; margin-top: 15px; }
        """)

    def _create_input(self, placeholder_text, echo_mode=QtWidgets.QLineEdit.EchoMode.Normal):
        line_edit = QtWidgets.QLineEdit(self)
        line_edit.setPlaceholderText(placeholder_text)
        line_edit.setFixedHeight(40)
        line_edit.setEchoMode(echo_mode)
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

        if get_user(email):
            QtWidgets.QMessageBox.warning(self, "Error", "Este correo ya está registrado.")
            return

        register_user(email, password, names, lastnames, dob)
        QtWidgets.QMessageBox.information(self, "Éxito", "Registro exitoso. ¡Ahora puedes iniciar sesión!")
        self.go_to_login.emit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RegistroWindow()
    window.show()
    sys.exit(app.exec())