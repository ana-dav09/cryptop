import sys
from PyQt6 import QtWidgets, QtCore
import firebase_admin
from firebase_admin import credentials, firestore

from inicio_window import InicioWindow
from registro_window import RegistroWindow
from login_window import LoginWindow
from dashboard_window import DashboardWindow
from information_window import InformationWindow
from project_selection_window import ProjectSelectionWindow
from barra_lateral import SidebarWidget
from new_project_window import NewAnalysisWindow

class RecuperarPasswordWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recuperar Contraseña")
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Pantalla de Recuperar Contraseña"))

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
        self.dashboard_screen = DashboardWindow()
        self.recover_password_screen = RecuperarPasswordWindow()
        self.new_analysis_screen = NewAnalysisWindow()
        self.load_project_screen = LoadProjectWindow()
        self.history_screen = HistoryWindow()
        self.project_selection_screen = ProjectSelectionWindow()
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

        # CONECTAR SEÑALES DEL DASHBOARD AL MAINAPP
        self.dashboard_screen.project_selection_requested2.connect(self.show_project_selection_screen)
        self.dashboard_screen.history_requested2.connect(self.show_history_screen)
        self.dashboard_screen.information_requested2.connect(self.show_information_screen)
        self.dashboard_screen.logout_requested2.connect(self.show_inicio_screen)
        self.dashboard_screen.new_analysis_requested2.connect(self.show_new_analysis_screen)

        #CONECTAR LAS SEÑALES DE LA PANTALLA DE NUEVO ANÁLISIS
        self.new_analysis_screen.project_selection_requested2.connect(self.show_project_selection_screen)
        self.dashboard_screen.history_requested2.connect(self.show_history_screen)
        self.dashboard_screen.information_requested2.connect(self.show_information_screen)
        self.dashboard_screen.logout_requested2.connect(self.show_inicio_screen)
        
         # CONECTAR LAS SEÑALES DE LA PANTALLA DE SELECCIÓN DE PROYECTO
        self.project_selection_screen.project_selection_requested2.connect(self.show_project_selection_screen)
        self.project_selection_screen.history_requested2.connect(self.show_history_screen)
        self.project_selection_screen.information_requested2.connect(self.show_information_screen)
        self.project_selection_screen.logout_requested2.connect(self.show_inicio_screen)
        self.project_selection_screen.new_analysis_requested2.connect(self.show_new_analysis_screen)
        self.project_selection_screen.dashboard_screen.connect(self.show_dashboard_screen)

        # Añadir las pantallas al QStackedWidget
        self.stacked_widget.addWidget(self.inicio_screen)
        self.stacked_widget.addWidget(self.register_screen)
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.dashboard_screen)
        self.stacked_widget.addWidget(self.information_screen)
        self.stacked_widget.addWidget(self.history_screen)
        self.stacked_widget.addWidget(self.project_selection_screen)
        self.stacked_widget.addWidget(self.new_analysis_screen)

        self.show_inicio_screen()

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

    def show_history_screen(self):
        self.stacked_widget.setCurrentWidget(self.history_screen)

    def show_project_selection_screen(self):
        self.stacked_widget.setCurrentWidget(self.project_selection_screen)

    def show_new_analysis_screen(self):
        self.stacked_widget.setCurrentWidget(self.new_analysis_screen)

    

    # Método para manejar el proyecto seleccionado
    def _handle_project_selected(self, project_data):
        QtWidgets.QMessageBox.information(self, "Proyecto Cargado",
                                          f"¡Proyecto '{project_data['name']}' listo para trabajar!")
        # Aquí iría la lógica para cargar el proyecto en la siguiente pantalla
        # Por ejemplo: self.analysis_interface_screen.load_project(project_data)
        # self.show_analysis_interface_screen()
        # Por ahora, simplemente volvemos al dashboard
        self.show_dashboard_screen()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_app = MainApplicationWindow()
    main_app.show()
    
    # Si style.qss está en la misma carpeta que main_page.py:
    try:
        with open("style.qss", "r") as file:
            style = file.read()
            app.setStyleSheet(style)
    except FileNotFoundError:
        print("⚠️ Archivo style.qss no encontrado, usando estilos por defecto")
    
    sys.exit(app.exec())