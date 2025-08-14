from PyQt6 import QtWidgets, QtGui, QtCore

class SidebarWidget(QtWidgets.QFrame): 
    # Definir todas las señales de navegación
    new_analysis_requested = QtCore.pyqtSignal()
    project_selection_requested = QtCore.pyqtSignal()
    history_requested = QtCore.pyqtSignal()
    settings_requested = QtCore.pyqtSignal()
    information_requested = QtCore.pyqtSignal()
    logout_requested = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250) 
        self.setStyleSheet("""
            QFrame {
                background-color: #264653; /* Azul oscuro */
                color: white;
                border-right: 1px solid #333; /* Opcional: un borde para separarla */
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                text-align: left;
                padding: 15px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2A9D8F; /* Verde azulado al pasar el ratón */
            }
        """)
        self.init_ui()

    def init_ui(self):
        sidebar_layout = QtWidgets.QVBoxLayout(self)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(10)

        # Logo/Título en el sidebar
        sidebar_logo_label = QtWidgets.QLabel("CryptJAD")
        sidebar_logo_label.setFont(QtGui.QFont("Arial", 28, QtGui.QFont.Weight.Bold))
        sidebar_logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        sidebar_logo_label.setContentsMargins(0, 0, 0, 30) # Espacio inferior
        sidebar_layout.addWidget(sidebar_logo_label)

        # Botones de navegación del sidebar, conectándolos a las señales de esta clase
        self._add_sidebar_button(sidebar_layout, "Nuevo Análisis", self.new_analysis_requested.emit)
        self._add_sidebar_button(sidebar_layout, "Cargar Proyecto", self.project_selection_requested.emit)
        self._add_sidebar_button(sidebar_layout, "Historial", self.history_requested.emit)
        self._add_sidebar_button(sidebar_layout, "Configuración", self.settings_requested.emit)
        self._add_sidebar_button(sidebar_layout, "Información", self.information_requested.emit)

        sidebar_layout.addStretch(1) # Empuja los botones hacia arriba

        self._add_sidebar_button(sidebar_layout, "Cerrar sesión", self.logout_requested.emit)

    def _add_sidebar_button(self, layout, text, connection_slot):
        """Helper para añadir botones al sidebar."""
        btn = QtWidgets.QPushButton(text, self)
        btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn.clicked.connect(connection_slot)
        layout.addWidget(btn)