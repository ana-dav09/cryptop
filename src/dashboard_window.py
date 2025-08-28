import sys
from PyQt6 import QtWidgets, QtGui, QtCore
from barra_lateral import SidebarWidget

class DashboardWindow(QtWidgets.QWidget):
    new_analysis_requested = QtCore.pyqtSignal()
    project_selection_requested = QtCore.pyqtSignal()
    history_requested = QtCore.pyqtSignal()
    settings_requested = QtCore.pyqtSignal()
    logout_requested = QtCore.pyqtSignal()
    information_requested = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD - Dashboard")
        self.setGeometry(50, 50, 1200, 800)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: #F5F6FA;")
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # --- Sidebar ---
        self.sidebar = SidebarWidget(self)
        main_layout.addWidget(self.sidebar)

        # --- Contenido Principal ---
        content_area = QtWidgets.QFrame(self)
        content_area.setStyleSheet("background-color: #F8F9FA;")
        content_layout = QtWidgets.QVBoxLayout(content_area)
        content_layout.setContentsMargins(40,30,40,30)
        content_layout.setSpacing(25)

        # Bienvenida
        welcome_label = QtWidgets.QLabel("Bienvenido, [Nombre de Usuario]")
        welcome_label.setFont(QtGui.QFont("Segoe UI", 26, QtGui.QFont.Weight.Bold))
        welcome_label.setStyleSheet("color: #1F3C88;")
        content_layout.addWidget(welcome_label, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        status_label = QtWidgets.QLabel("Gestiona tus proyectos y realiza nuevos análisis de manera eficiente.")
        status_label.setFont(QtGui.QFont("Segoe UI", 16))
        status_label.setStyleSheet("color: #555;")
        content_layout.addWidget(status_label, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        # --- Estadísticas rápidas ---
        stats_layout = QtWidgets.QHBoxLayout()
        stats_layout.setSpacing(20)
        stats_data = [
            ("Total Proyectos", "12"),
            ("Proyectos Activos", "5"),
            ("Análisis Completados", "7"),
            ("Análisis Pendientes", "3")
        ]
        for title, value in stats_data:
            card = QtWidgets.QFrame()
            card.setFixedSize(220,100)
            card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 15px;
                    border: 1px solid #D3D3D3;
                }
            """)
            card_layout = QtWidgets.QVBoxLayout(card)
            card_layout.setContentsMargins(15,15,15,15)
            lbl_value = QtWidgets.QLabel(value)
            lbl_value.setFont(QtGui.QFont("Segoe UI", 24, QtGui.QFont.Weight.Bold))
            lbl_value.setStyleSheet("color: #219EBC;")
            lbl_title = QtWidgets.QLabel(title)
            lbl_title.setFont(QtGui.QFont("Segoe UI", 12))
            lbl_title.setStyleSheet("color: #555;")
            card_layout.addWidget(lbl_value)
            card_layout.addWidget(lbl_title)
            stats_layout.addWidget(card)
        content_layout.addLayout(stats_layout)

        # --- Accesos rápidos ---
        quick_layout = QtWidgets.QHBoxLayout()
        quick_layout.setSpacing(20)
        quick_actions = [
            ("Nuevo Análisis", self.new_analysis_requested.emit, "#219EBC"),
            ("Tus Proyectos", self.project_selection_requested.emit, "#1F7A8C"),
            ("Historial", self.history_requested.emit, "#264653"),
            ("Configuración", self.settings_requested.emit, "#6A0572")
        ]
        for text, callback, color in quick_actions:
            btn = QtWidgets.QPushButton(text)
            btn.setFixedSize(180, 50)
            btn.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Weight.Bold))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border-radius: 25px;
                }}
                QPushButton:hover {{
                    background-color: #167DAB;
                }}
            """)
            btn.clicked.connect(callback)
            quick_layout.addWidget(btn)
        content_layout.addLayout(quick_layout)

        # --- Proyectos recientes como tarjetas ---
        recent_label = QtWidgets.QLabel("Proyectos Recientes")
        recent_label.setFont(QtGui.QFont("Segoe UI", 22, QtGui.QFont.Weight.Bold))
        recent_label.setStyleSheet("color: #333;")
        content_layout.addWidget(recent_label)

        recent_layout = QtWidgets.QHBoxLayout()
        recent_layout.setSpacing(20)
        dummy_projects = [
            "AES - 20/06/2024",
            "DES Diferencial - 15/06/2024",
            "Algoritmo Custom - 01/06/2024",
            "RSA Avanzado - 10/05/2024"
        ]
        for proj in dummy_projects:
            card = QtWidgets.QFrame()
            card.setFixedSize(220,140)
            card.setFont(QtGui.QFont("Segoe UI", 14, QtGui.QFont.Weight.Bold))
            card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 12px;
                    border: 1px solid #D3D3D3;
                }
                QFrame:hover {
                    border: 2px solid #219EBC;
                }
            """)
            card_layout = QtWidgets.QVBoxLayout(card)
            lbl_name = QtWidgets.QLabel(proj)
            lbl_name.setFont(QtGui.QFont("Segoe UI", 14, QtGui.QFont.Weight.Bold))
            lbl_name.setStyleSheet("color: #333;")
            card_layout.addWidget(lbl_name)
            card_layout.addStretch(1)
            recent_layout.addWidget(card)
        content_layout.addLayout(recent_layout)

        # --- Log de actividad ---
        log_label = QtWidgets.QLabel("Últimas Actividades")
        log_label.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Weight.Bold))
        log_label.setStyleSheet("color: #333;")
        content_layout.addWidget(log_label)

        log_widget = QtWidgets.QListWidget()
        log_widget.addItems([
            "Proyecto AES creado",
            "Análisis DES completado",
            "Nuevo usuario registrado"
        ])
        log_widget.setFont(QtGui.QFont("Segoe UI", 12))
        log_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #E0E0E0;
                border-radius: 12px;
                background-color: white;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #F0F0F0;
            }
            QListWidget::item:hover {
                background-color: #E0F2F7;
            }
        """)
        content_layout.addWidget(log_widget, stretch=1)

        content_layout.addStretch(1)
        main_layout.addWidget(content_area, stretch=1)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())
