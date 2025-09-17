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
        status_label.setFont(QtGui.QFont("Segoe UI", 15))
        status_label.setStyleSheet("color: #555; margin-bottom:15px;")
        content_layout.addWidget(status_label, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        # --- Área principal dividida ---
        main_split = QtWidgets.QHBoxLayout()
        main_split.setSpacing(30)

        # === Columna izquierda ===
        left_col = QtWidgets.QVBoxLayout()
        left_col.setSpacing(25)

        # Estadísticas rápidas
        stats_label = QtWidgets.QLabel("Resumen")
        stats_label.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Weight.Bold))
        stats_label.setStyleSheet("color:#333;")
        left_col.addWidget(stats_label)

        stats_grid = QtWidgets.QGridLayout()
        stats_grid.setSpacing(15)
        stats_data = [
            ("Total Proyectos", "12"),
            ("Activos", "5"),
            ("Completados", "7"),
            ("Pendientes", "3")
        ]
        for i, (title, value) in enumerate(stats_data):
            card = QtWidgets.QFrame()
            card.setFixedSize(150,90)
            card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 12px;
                    border: 1px solid #D3D3D3;
                }
            """)
            card_layout = QtWidgets.QVBoxLayout(card)
            card_layout.setContentsMargins(10,10,10,10)
            lbl_value = QtWidgets.QLabel(value)
            lbl_value.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Weight.Bold))
            lbl_value.setStyleSheet("color: #219EBC;")
            lbl_title = QtWidgets.QLabel(title)
            lbl_title.setFont(QtGui.QFont("Segoe UI", 11))
            lbl_title.setStyleSheet("color: #555;")
            card_layout.addWidget(lbl_value)
            card_layout.addWidget(lbl_title)
            stats_grid.addWidget(card, i//2, i%2)
        left_col.addLayout(stats_grid)

        # Accesos rápidos
        quick_label = QtWidgets.QLabel("Accesos rápidos")
        quick_label.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Weight.Bold))
        quick_label.setStyleSheet("color:#333; margin-top:20px;")
        left_col.addWidget(quick_label)

        quick_actions = [
            ("Nuevo Análisis", self.new_analysis_requested.emit, "#219EBC"),
            ("Tus Proyectos", self.project_selection_requested.emit, "#1F7A8C"),
            ("Historial", self.history_requested.emit, "#264653"),
            ("Configuración", self.settings_requested.emit, "#6A0572")
        ]
        for text, callback, color in quick_actions:
            btn = QtWidgets.QPushButton(text)
            btn.setFixedHeight(45)
            btn.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Weight.Bold))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border-radius: 20px;
                }}
                QPushButton:hover {{
                    background-color: #167DAB;
                }}
            """)
            btn.clicked.connect(callback)
            left_col.addWidget(btn)

        left_col.addStretch(1)

        # === Columna derecha ===
        right_col = QtWidgets.QVBoxLayout()
        right_col.setSpacing(25)

        # Proyectos recientes
        recent_label = QtWidgets.QLabel("Proyectos Recientes")
        recent_label.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Weight.Bold))
        recent_label.setStyleSheet("color: #333;")
        right_col.addWidget(recent_label)

        recent_list = QtWidgets.QListWidget()
        recent_list.addItems([
            "AES - 20/06/2024",
            "DES Diferencial - 15/06/2024",
            "Algoritmo Custom - 01/06/2024",
            "RSA Avanzado - 10/05/2024"
        ])
        recent_list.setFont(QtGui.QFont("Segoe UI", 12))
        recent_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                background-color: white;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #F0F0F0;
            }
            QListWidget::item:hover {
                background-color: #E0F2F7;
            }
        """)
        right_col.addWidget(recent_list, stretch=2)

        # Log de actividad
        log_label = QtWidgets.QLabel("Últimas Actividades")
        log_label.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Weight.Bold))
        log_label.setStyleSheet("color: #333; margin-top:10px;")
        right_col.addWidget(log_label)

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
                border-radius: 10px;
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
        right_col.addWidget(log_widget, stretch=2)

        # Añadir columnas al split
        main_split.addLayout(left_col, stretch=1)
        main_split.addLayout(right_col, stretch=2)
        content_layout.addLayout(main_split)

        main_layout.addWidget(content_area, stretch=1)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())
