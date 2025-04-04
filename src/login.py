import sys
import json
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


# 📂 ARCHIVO DONDE SE GUARDAN LOS USUARIOS
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


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - CryptJAD")
        self.setGeometry(100, 100, 400, 500)
        self.initUI()
        self.load_stylesheet("style.qss")

    def initUI(self):
        layout = QVBoxLayout()

        # 🟦 HEADER
        title = QLabel("Bienvenido a CryptJAD")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Inicia sesión para continuar")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 🟦 CAMPOS DE ENTRADA
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo electrónico")
        self.email_input.setObjectName("inputField")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setObjectName("inputField")

        # 🟦 BOTÓN DE LOGIN
        login_button = QPushButton("Iniciar Sesión")
        login_button.setObjectName("loginButton")
        login_button.clicked.connect(self.login)

        # 🟦 REGISTRO
        register_label = QLabel("¿No tienes cuenta?")
        register_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        register_button = QPushButton("Regístrate aquí")
        register_button.setObjectName("registerLink")
        register_button.clicked.connect(self.open_register)

        # 📌 ORGANIZACIÓN
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addSpacing(10)
        layout.addWidget(login_button)
        layout.addSpacing(20)

        reg_layout = QHBoxLayout()
        reg_layout.addWidget(register_label)
        reg_layout.addWidget(register_button)

        layout.addLayout(reg_layout)
        self.setLayout(layout)

    def login(self):
        """ Valida el login con la base de datos JSON """
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        users = load_users()
        if email in users and users[email]["password"] == password:
            QMessageBox.information(self, "Éxito", "Inicio de sesión correcto. ¡Bienvenido!")
            self.close()  # Cierra la ventana de login
            python_exe = sys.executable  
            subprocess.Popen([python_exe, "C:\\Users\\hp\\Desktop\\diseño\\src\\carr.py"])
        else:
            QMessageBox.warning(self, "Error", "Correo o contraseña incorrectos.")

    def open_register(self):
        """ Abre la ventana de registro """
        self.close()
        self.reg_window = RegisterWindow()
        self.reg_window.show()

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


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registro - CryptJAD")
        self.setGeometry(100, 100, 400, 500)
        self.initUI()
        self.load_stylesheet("style.qss")

    def initUI(self):
        layout = QVBoxLayout()

        # 🟦 HEADER
        title = QLabel("Crea tu cuenta")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Únete a CryptJAD")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 🟦 CAMPOS DE ENTRADA
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre completo")
        self.name_input.setObjectName("inputField")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo electrónico")
        self.email_input.setObjectName("inputField")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setObjectName("inputField")

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirmar contraseña")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setObjectName("inputField")

        # 🟦 BOTÓN DE REGISTRO
        register_button = QPushButton("Registrarse")
        register_button.setObjectName("registerButton")
        register_button.clicked.connect(self.register)

        # 🟦 LOGIN
        login_label = QLabel("¿Ya tienes cuenta?")
        login_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        login_button = QPushButton("Inicia sesión")
        login_button.setObjectName("registerLink")
        login_button.clicked.connect(self.open_login)

        # 📌 ORGANIZACIÓN
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addWidget(self.name_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_password_input)
        layout.addSpacing(10)
        layout.addWidget(register_button)
        layout.addSpacing(20)

        login_layout = QHBoxLayout()
        login_layout.addWidget(login_label)
        login_layout.addWidget(login_button)

        layout.addLayout(login_layout)
        self.setLayout(layout)

    def register(self):
        """ Registra un nuevo usuario en JSON """
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()

        if not name or not email or not password:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
            return

        users = load_users()
        if email in users:
            QMessageBox.warning(self, "Error", "Este correo ya está registrado.")
            return

        users[email] = {"name": name, "password": password}
        save_users(users)
        QMessageBox.information(self, "Éxito", "Registro exitoso. ¡Ahora puedes iniciar sesión!")
        self.open_login()

    def open_login(self):
        """ Abre la ventana de login """
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()

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
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
