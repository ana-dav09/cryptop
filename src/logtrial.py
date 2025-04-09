from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QStackedWidget, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect
from PyQt6.QtGui import QFont
import sys, json, os

USER_DB = "users.json"

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(USER_DB, "w") as file:
        json.dump(users, file, indent=4)

class LoginWidget(QWidget):
    def __init__(self, switch_to_register):
        super().__init__()
        self.switch_to_register = switch_to_register
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        title = QLabel("Bienvenido a CryptJAD")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.email_input = QLineEdit(placeholderText="Correo electrónico")
        self.password_input = QLineEdit(placeholderText="Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        loginButton = QPushButton("Iniciar sesión")
        loginButton.clicked.connect(self.login)

        switch_btn = QPushButton("Regístrate aquí")
        switch_btn.clicked.connect(self.switch_to_register)

        layout.addWidget(title)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(loginButton)
        layout.addWidget(switch_btn)
        self.setLayout(layout)

    def login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        users = load_users()
        if email in users and users[email]["password"] == password:
            QMessageBox.information(self, "Éxito", "Inicio de sesión correcto.")
        else:
            QMessageBox.warning(self, "Error", "Correo o contraseña incorrectos.")

class RegisterWidget(QWidget):
    def __init__(self, switch_to_login):
        super().__init__()
        self.switch_to_login = switch_to_login
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        title = QLabel("Crea tu cuenta")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_input = QLineEdit(placeholderText="Nombre completo")
        self.email_input = QLineEdit(placeholderText="Correo electrónico")
        self.password_input = QLineEdit(placeholderText="Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input = QLineEdit(placeholderText="Confirmar contraseña")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        registerButton = QPushButton("Registrarse")
        registerButton.clicked.connect(self.register)

        switch_btn = QPushButton("Inicia sesión")
        switch_btn.clicked.connect(self.switch_to_login)

        layout.addWidget(title)
        layout.addWidget(self.name_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_password_input)
        layout.addWidget(registerButton)
        layout.addWidget(switch_btn)
        self.setLayout(layout)

    def register(self):
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
        QMessageBox.information(self, "Éxito", "Registro exitoso.")
        self.switch_to_login()

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD Auth")
        self.setGeometry(100, 100, 400, 500)

        self.stack = QStackedWidget()
        self.login_widget = LoginWidget(self.animate_to_register)
        self.register_widget = RegisterWidget(self.animate_to_login)

        self.stack.addWidget(self.login_widget)
        self.stack.addWidget(self.register_widget)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)
        self.load_stylesheet("style.qss")  # << Aquí se carga

    def load_stylesheet(self, file_path):
        try:
            with open(file_path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"❌ No se encontró {file_path}")

    def animate_to_register(self):
        self.animate_transition(0, 1)

    def animate_to_login(self):
        self.animate_transition(1, 0)

    def animate_transition(self, from_index, to_index):
        from_widget = self.stack.widget(from_index)
        to_widget = self.stack.widget(to_index)

        self.stack.setCurrentIndex(to_index)
        to_widget.move(self.stack.width(), 0)

        anim = QPropertyAnimation(to_widget, b"pos", self)
        anim.setDuration(500)
        anim.setStartValue(to_widget.pos())
        anim.setEndValue(from_widget.pos())
        anim.start()

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec())
