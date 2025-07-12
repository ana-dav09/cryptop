import sys
from PyQt6 import QtWidgets, QtGui, QtCore
from barra_lateral import SidebarWidget

class DashboardWindow(QtWidgets.QWidget):
    # Señales para la navegación del Dashboard
    new_analysis_requested = QtCore.pyqtSignal()
    load_project_requested = QtCore.pyqtSignal()
    history_requested = QtCore.pyqtSignal()
    settings_requested = QtCore.pyqtSignal()
    logout_requested = QtCore.pyqtSignal()
    information_requested = QtCore.pyqtSignal() # Nueva señal para la pantalla de información

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD - Dashboard")
        self.setGeometry(50, 50, 1000, 700)
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Sidebar (Barra Lateral) ---
        self.sidebar = SidebarWidget(self) # Creamos una instancia de nuestra barra lateral reusable
        main_layout.addWidget(self.sidebar)

        # --- Contenido Principal del Dashboard ---
        content_area = QtWidgets.QFrame(self)
        content_area.setStyleSheet("background-color: #F8F9FA;")
        content_layout = QtWidgets.QVBoxLayout(content_area)
        content_layout.setContentsMargins(40, 30, 40, 30)
        content_layout.setSpacing(20)

        # Título de bienvenida (primero)
        welcome_label = QtWidgets.QLabel("Bienvenido, [Nombre de Usuario]")
        welcome_label.setFont(QtGui.QFont("Arial", 24, QtGui.QFont.Weight.Bold))
        welcome_label.setStyleSheet("color: #333;")
        content_layout.addWidget(welcome_label, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

        status_label = QtWidgets.QLabel("Aquí puedes gestionar tus proyectos y realizar nuevos análisis.")
        status_label.setFont(QtGui.QFont("Arial", 16))
        status_label.setStyleSheet("color: #555;")
        content_layout.addWidget(status_label)

        # --- Botones de Acción (Nuevo Análisis y Cargar Proyecto) ---
        action_buttons_layout = QtWidgets.QHBoxLayout()
        action_buttons_layout.setSpacing(40) # Espacio entre los botones

        new_analysis_btn = QtWidgets.QPushButton("Nuevo Análisis")
        new_analysis_btn.setFixedSize(220, 60)
        new_analysis_btn.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Weight.Bold))
        new_analysis_btn.setStyleSheet("""
             QPushButton {
                background-color: #219EBC;
                color: white;
                border-radius: 25px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #167DAB;
            }
        """)
        new_analysis_btn.clicked.connect(self.new_analysis_requested.emit)
        action_buttons_layout.addWidget(new_analysis_btn)

        load_project_btn = QtWidgets.QPushButton("Tus proyectos")
        load_project_btn.setFixedSize(220, 60)
        load_project_btn.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Weight.Bold))
        load_project_btn.setStyleSheet("""
             QPushButton {
                background-color: #219EBC;
                color: white;
                border-radius: 25px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #167DAB;
            }
        """)
        load_project_btn.clicked.connect(self.load_project_requested.emit)
        action_buttons_layout.addWidget(load_project_btn)

        action_buttons_layout.addStretch(1) # Empuja los botones a la izquierda

        content_layout.addLayout(action_buttons_layout)
        content_layout.addSpacing(30) # Espacio entre botones de acción y proyectos recientes

        # Sección de "Últimos Proyectos" (debajo de los botones de acción)
        latest_projects_label = QtWidgets.QLabel("Últimos Proyectos")
        latest_projects_label.setFont(QtGui.QFont("Arial", 24, QtGui.QFont.Weight.Bold))
        latest_projects_label.setContentsMargins(0, 0, 0, 10) # Ajuste de margen
        content_layout.addWidget(latest_projects_label)

        projects_list_widget = QtWidgets.QListWidget(self)
        projects_list_widget.addItem("Proyecto Criptoanálisis AES - 20/06/2024")
        projects_list_widget.addItem("Análisis Diferencial DES - 15/06/2024")
        projects_list_widget.addItem("Prueba Algoritmo Personalizado - 01/06/2024")
        projects_list_widget.setFont(QtGui.QFont("Arial", 14))
        projects_list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #D3D3D3;
                border-radius: 8px;
                background-color: white;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #EDEDED;
            }
            QListWidget::item:hover {
                background-color: #E0F2F7;
            }
        """)
        content_layout.addWidget(projects_list_widget, stretch=1)

        content_layout.addStretch(1)

        main_layout.addWidget(content_area, stretch=1)

    def _add_sidebar_button(self, layout, text, connection_slot):
        btn = QtWidgets.QPushButton(text, self)
        btn.clicked.connect(connection_slot)
        layout.addWidget(btn)