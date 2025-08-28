from PyQt6 import QtWidgets, QtGui, QtCore

class SidebarWidget(QtWidgets.QFrame): 
    new_analysis_requested = QtCore.pyqtSignal()
    project_selection_requested = QtCore.pyqtSignal()
    history_requested = QtCore.pyqtSignal()
    settings_requested = QtCore.pyqtSignal()
    information_requested = QtCore.pyqtSignal()
    logout_requested = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setStyleSheet("""
            QFrame {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #264653, stop:1 #1B2B36);
                color: white;
                border-right: 1px solid #333;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                text-align: left;
                padding: 12px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2A9D8F;
                border-radius: 8px;
            }
            QLabel#LogoLabel {
                font-size: 28px;
                font-weight: bold;
                color: #F4F4F4;
            }
            QFrame#Separator {
                background-color: #3A5A64;
                max-height: 1px;
            }
        """)
        self.init_ui()

    def init_ui(self):
        sidebar_layout = QtWidgets.QVBoxLayout(self)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(10)

        # Logo/Título
        sidebar_logo_label = QtWidgets.QLabel("CryptJAD")
        sidebar_logo_label.setObjectName("LogoLabel")
        sidebar_logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        sidebar_logo_label.setContentsMargins(0, 0, 0, 30)
        sidebar_layout.addWidget(sidebar_logo_label)

        # Sección principal
        self._add_sidebar_button(sidebar_layout, "Nuevo Análisis", self.new_analysis_requested.emit, "📑")
        self._add_sidebar_button(sidebar_layout, "Cargar Proyecto", self.project_selection_requested.emit, "📂")
        self._add_sidebar_button(sidebar_layout, "Historial", self.history_requested.emit, "📜")
        self._add_sidebar_button(sidebar_layout, "Configuración", self.settings_requested.emit, "⚙️")
        self._add_sidebar_button(sidebar_layout, "Información", self.information_requested.emit, "ℹ️")

        # Separador
        separator = QtWidgets.QFrame()
        separator.setObjectName("Separator")
        sidebar_layout.addWidget(separator)

        sidebar_layout.addStretch(1)

        # Logout destacado en la parte inferior
        self._add_sidebar_button(sidebar_layout, "Cerrar sesión", self.logout_requested.emit, "🚪")

    def _add_sidebar_button(self, layout, text, connection_slot, icon_text=""):
        """Helper para añadir botones al sidebar con icono opcional."""
        btn = QtWidgets.QPushButton(f"{icon_text}  {text}")
        btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn.setFont(QtGui.QFont("Segoe UI", 14))
        btn.setMinimumHeight(40)
        btn.clicked.connect(connection_slot)
        layout.addWidget(btn)
