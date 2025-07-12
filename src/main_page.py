import sys
from PyQt6 import QtWidgets, QtCore

from inicio_window import InicioWindow
from registro_window import RegistroWindow
from login_window import LoginWindow
from dashboard_window import DashboardWindow
from information_window import InformationWindow

class RecuperarPasswordWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recuperar Contraseña")
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Pantalla de Recuperar Contraseña"))

class NuevoAnalisisWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nuevo Análisis")
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Pantalla de Nuevo Análisis (aquí se configuran los tipos de análisis)"))

class LoadProjectWindow(QtWidgets.QWidget): #"Cargar Proyecto"
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cargar Proyecto")
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Pantalla de Cargar Proyecto"))

class HistoryWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Historial")
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Pantalla de Historial de Análisis"))

class SettingsWindow(QtWidgets.QWidget): #  "Configuración"
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuración")
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Pantalla de Configuración"))



class MainApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD")
        self.setGeometry(100, 100, 1000, 700)

        self.stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Instanciar las pantallas
        self.inicio_screen = InicioWindow()
        self.register_screen = RegistroWindow()
        self.login_screen = LoginWindow()
        self.dashboard_screen = DashboardWindow() # Instancia del Dashboard
        self.recover_password_screen = RecuperarPasswordWindow()
        self.new_analysis_screen = NuevoAnalisisWindow()
        self.load_project_screen = LoadProjectWindow()
        self.history_screen = HistoryWindow()
        self.settings_screen = SettingsWindow()
        self.information_screen = InformationWindow()

        #Conectar pantallas
        self.inicio_screen.login_requested.connect(self.show_login_screen)
        self.inicio_screen.register_requested.connect(self.show_register_screen)
        
        self.register_screen.go_to_inicio.connect(self.show_inicio_screen)
        self.register_screen.go_to_login.connect(self.show_login_screen)
        
        self.login_screen.go_to_inicio.connect(self.show_inicio_screen)
        self.login_screen.go_to_register.connect(self.show_register_screen)
        self.login_screen.go_to_dashboard.connect(self.show_dashboard_screen)
        #self.login_screen.go_to_recover_password.connect(self.show_recover_password_screen)

        # CONECTAR LAS SEÑALES DIRECTAMENTE DEL SIDEBAR DEL DASHBOARD
        #self.dashboard_screen.sidebar.new_analysis_requested.connect(self.show_new_analysis_screen)
        #self.dashboard_screen.sidebar.load_project_requested.connect(self.show_load_project_screen)
        #self.dashboard_screen.sidebar.history_requested.connect(self.show_history_screen)
        #self.dashboard_screen.sidebar.settings_requested.connect(self.show_settings_screen)
        self.dashboard_screen.sidebar.information_requested.connect(self.show_information_screen)
        self.dashboard_screen.sidebar.logout_requested.connect(self.show_inicio_screen) # Cerrar sesión


        # Añadir las pantallas al QStackedWidget
        self.stacked_widget.addWidget(self.inicio_screen)      # Index 0
        self.stacked_widget.addWidget(self.register_screen)    # Index 1
        self.stacked_widget.addWidget(self.login_screen)       # Index 2
        self.stacked_widget.addWidget(self.dashboard_screen)
        self.stacked_widget.addWidget(self.information_screen)

        self.show_inicio_screen() # Mostrar la pantalla de inicio al arrancar

    def show_inicio_screen(self):
        self.stacked_widget.setCurrentWidget(self.inicio_screen)

    def show_register_screen(self):
        self.stacked_widget.setCurrentWidget(self.register_screen)

    def show_login_screen(self):
        self.stacked_widget.setCurrentWidget(self.login_screen)
    
    def show_dashboard_screen(self):
        self.stacked_widget.setCurrentWidget(self.dashboard_screen)

    def show_information_screen(self):
        self.stacked_widget.setCurrentWidget(self.information_screen)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_app = MainApplicationWindow()
    main_app.show()
    with open("style.qss", "r") as file:
            style = file.read()
            app.setStyleSheet(style)
    sys.exit(app.exec())