import sys
import os
from PyQt6 import QtWidgets, QtGui, QtCore

# Manejo de importaciones con rutas flexibles
def setup_imports():
    """Configura las rutas de importación"""
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    POSSIBLE_PATHS = [
        THIS_DIR,
        os.path.join(THIS_DIR, ".."),
        os.path.join(THIS_DIR, "..", "integracion"),
        os.path.join(THIS_DIR, "..", "ui"),
        os.path.join(THIS_DIR, "..", "windows"),
    ]
    
    for path in POSSIBLE_PATHS:
        abs_path = os.path.abspath(path)
        if os.path.isdir(abs_path) and abs_path not in sys.path:
            sys.path.insert(0, abs_path)

setup_imports()

# Importar componentes necesarios
try:
    from barra_lateral import SidebarWidget
except ImportError as e:
    print(f"❌ Error importando SidebarWidget: {e}")
    SidebarWidget = None

# Intentar importar las ventanas de ataque (opcional)
AttackWindow = None
SDESLinearWindow = None

try:
    from baby_aes_attack_window import AttackWindow
    print("✅ AttackWindow importado correctamente")
except ImportError as e:
    print(f"⚠️ No se pudo importar AttackWindow: {e}")

try:
    from sdes_attack_window import SDESLinearWindow
    print("✅ SDESLinearWindow importado correctamente")
except ImportError as e:
    print(f"⚠️ No se pudo importar SDESLinearWindow: {e}")


class NewAnalysisWindow(QtWidgets.QWidget):
    project_created = QtCore.pyqtSignal(str)
    new_analysis_requested2 = QtCore.pyqtSignal()
    project_selection_requested2 = QtCore.pyqtSignal()
    history_requested2 = QtCore.pyqtSignal()
    settings_requested2 = QtCore.pyqtSignal()
    logout_requested2 = QtCore.pyqtSignal()
    information_requested2 = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD - Nuevo Proyecto")
        self.setGeometry(100, 100, 1400, 850)
        
        # Referencias a ventanas abiertas
        self.baby_window = None
        self.sdes_window = None
        self.custom_window = None
        
        self.init_ui()

    def init_ui(self):
        # Fondo estilo Fluent Design
        self.setStyleSheet("""
            QWidget {
                background-color: #F3F4F6;
                font-family: 'Segoe UI', 'San Francisco', system-ui;
            }
        """)

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        if SidebarWidget:
            self.sidebar = SidebarWidget(self)
            main_layout.addWidget(self.sidebar, stretch=0)

            # Conectar señales del sidebar
            self.sidebar.project_selection_requested.connect(self.project_selection_requested2.emit)
            self.sidebar.history_requested.connect(self.history_requested2.emit)
            self.sidebar.information_requested.connect(self.information_requested2.emit)
            self.sidebar.logout_requested.connect(self.logout_requested2.emit)

        # Contenedor principal
        content_container = QtWidgets.QWidget()
        content_container.setStyleSheet("background-color: #F3F4F6;")
        content_main_layout = QtWidgets.QVBoxLayout(content_container)
        content_main_layout.setContentsMargins(0, 0, 0, 0)
        content_main_layout.setSpacing(0)

        # Header Bar estilo Teams
        header = QtWidgets.QFrame()
        header.setFixedHeight(52)
        header.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E1E1E1;
            }
        """)
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(32, 0, 32, 0)

        # Título con icono
        title_container = QtWidgets.QHBoxLayout()
        icon_label = QtWidgets.QLabel("📋")
        icon_label.setFont(QtGui.QFont("Segoe UI", 16))
        title_label = QtWidgets.QLabel("Nuevo proyecto")
        title_label.setFont(QtGui.QFont("Segoe UI", 16, QtGui.QFont.Weight.DemiBold))
        title_label.setStyleSheet("color: #242424;")
        
        title_container.addWidget(icon_label)
        title_container.addWidget(title_label)
        title_container.addStretch()
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()

        # Breadcrumb
        breadcrumb = QtWidgets.QLabel("Inicio  >  Nuevo proyecto")
        breadcrumb.setFont(QtGui.QFont("Segoe UI", 10))
        breadcrumb.setStyleSheet("color: #616161;")
        header_layout.addWidget(breadcrumb)

        content_main_layout.addWidget(header)

        # Área de contenido con scroll
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #F3F4F6;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #C1C1C1;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #A8A8A8;
            }
        """)

        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(32, 32, 32, 32)
        scroll_layout.setSpacing(24)

        # Hero section
        hero_label = QtWidgets.QLabel("Seleccionar plantilla")
        hero_label.setFont(QtGui.QFont("Segoe UI", 24, QtGui.QFont.Weight.Bold))
        hero_label.setStyleSheet("color: #242424;")
        scroll_layout.addWidget(hero_label)

        subtitle_label = QtWidgets.QLabel("Elija una plantilla de cifrado o cree un proyecto personalizado desde cero")
        subtitle_label.setFont(QtGui.QFont("Segoe UI", 13))
        subtitle_label.setStyleSheet("color: #616161; margin-bottom: 8px;")
        scroll_layout.addWidget(subtitle_label)

        # Grid de tarjetas estilo Fluent
        grid_container = QtWidgets.QWidget()
        grid_layout = QtWidgets.QGridLayout(grid_container)
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(0, 16, 0, 0)

        projects_data = [
            {
                "title": "Proyecto en blanco",
                "subtitle": "Empiece desde cero",
                "description": "Cree su propio cifrador de bloques con configuración completa de parámetros",
                "icon": "✨",
                "color": "#0078D4",
                "accent": "#106EBE",
                "type": "custom",
                "specs": ["Totalmente personalizable", "Control completo", "Para usuarios avanzados"]
            },
            {
                "title": "Baby AES",
                "subtitle": "Plantilla educativa",
                "description": "Versión simplificada del estándar AES ideal para aprendizaje y análisis",
                "icon": "🔐",
                "color": "#0078D4",
                "accent": "#106EBE",
                "type": "babyaes",
                "specs": ["16 bits de bloque", "2 rondas", "S-Box 4×4"]
            },
            {
                "title": "S-DES",
                "subtitle": "Cifrado Feistel",
                "description": "Simplified DES para comprender fundamentos de criptoanálisis clásico",
                "icon": "🔑",
                "color": "#0078D4",
                "accent": "#106EBE",
                "type": "sdes",
                "specs": ["8 bits de bloque", "Clave de 10 bits", "2 rondas Feistel"]
            }
        ]

        for idx, data in enumerate(projects_data):
            card = self.create_fluent_card(data)
            row = idx // 2
            col = idx % 2
            grid_layout.addWidget(card, row, col)

        scroll_layout.addWidget(grid_container)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        content_main_layout.addWidget(scroll)

        main_layout.addWidget(content_container, stretch=1)

    def create_fluent_card(self, data):
        """Crea una tarjeta estilo Microsoft Fluent Design"""
        card = QtWidgets.QFrame()
        card.setFixedSize(620, 200)
        card.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        # Estilo Fluent con sombra suave
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid #E1E1E1;
                border-radius: 8px;
            }}
            QFrame:hover {{
                background-color: #FAFAFA;
                border: 1px solid {data['color']};
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            }}
        """)

        card_layout = QtWidgets.QHBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(20)

        # Columna izquierda: icono destacado
        icon_container = QtWidgets.QFrame()
        icon_container.setFixedSize(80, 80)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {data['color']}, stop:1 {data['accent']});
                border-radius: 12px;
            }}
        """)
        icon_layout = QtWidgets.QVBoxLayout(icon_container)
        icon_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QtWidgets.QLabel(data['icon'])
        icon_label.setFont(QtGui.QFont("Segoe UI Emoji", 32))
        icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon_label)

        card_layout.addWidget(icon_container)

        # Columna central: contenido
        content_col = QtWidgets.QVBoxLayout()
        content_col.setSpacing(6)

        # Título
        title = QtWidgets.QLabel(data['title'])
        title.setFont(QtGui.QFont("Segoe UI", 15, QtGui.QFont.Weight.DemiBold))
        title.setStyleSheet("color: #242424;")
        content_col.addWidget(title)

        # Subtítulo
        subtitle = QtWidgets.QLabel(data['subtitle'])
        subtitle.setFont(QtGui.QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #616161;")
        content_col.addWidget(subtitle)

        # Descripción
        desc = QtWidgets.QLabel(data['description'])
        desc.setFont(QtGui.QFont("Segoe UI", 10))
        desc.setStyleSheet("color: #797979; margin-top: 4px;")
        desc.setWordWrap(True)
        content_col.addWidget(desc)

        # Especificaciones con bullets
        specs_layout = QtWidgets.QHBoxLayout()
        specs_layout.setSpacing(16)
        specs_layout.setContentsMargins(0, 8, 0, 0)
        
        for spec in data['specs']:
            spec_label = QtWidgets.QLabel(f"• {spec}")
            spec_label.setFont(QtGui.QFont("Segoe UI", 9))
            spec_label.setStyleSheet("color: #616161;")
            specs_layout.addWidget(spec_label)
        specs_layout.addStretch()
        
        content_col.addLayout(specs_layout)
        content_col.addStretch()

        card_layout.addLayout(content_col, stretch=1)

        # Columna derecha: botón de acción
        action_col = QtWidgets.QVBoxLayout()
        action_col.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        btn = QtWidgets.QPushButton("Crear")
        btn.setFixedSize(100, 36)
        btn.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Weight.DemiBold))
        btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {data['color']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {data['accent']};
            }}
            QPushButton:pressed {{
                background-color: #005A9E;
            }}
        """)
        btn.clicked.connect(lambda: self.on_project_selected(data['type'], data['title']))
        action_col.addWidget(btn)

        card_layout.addLayout(action_col)

        return card

    def on_project_selected(self, project_type, project_name):
        """Maneja la selección de un tipo de proyecto"""
        print(f"✅ Proyecto seleccionado: {project_type} - {project_name}")
        self.project_created.emit(project_type)

        if project_type == "babyaes":
            if AttackWindow:
                try:
                    self.baby_window = AttackWindow()
                    self.baby_window.show()
                    print("✅ Ventana Baby AES abierta")
                except Exception as e:
                    print(f"❌ Error al abrir Baby AES: {e}")
                    QtWidgets.QMessageBox.critical(
                        self,
                        "Error",
                        f"No se pudo abrir la ventana de Baby AES:\n{str(e)}"
                    )
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Módulo no disponible",
                    "La ventana de Baby AES no está disponible.\n"
                    "Verifique que 'baby_aes_attack_window.py' esté en la ruta correcta."
                )

        elif project_type == "sdes":
            if SDESLinearWindow:
                try:
                    self.sdes_window = SDESLinearWindow()
                    self.sdes_window.show()
                    print("✅ Ventana S-DES abierta")
                except Exception as e:
                    print(f"❌ Error al abrir S-DES: {e}")
                    QtWidgets.QMessageBox.critical(
                        self,
                        "Error",
                        f"No se pudo abrir la ventana de S-DES:\n{str(e)}"
                    )
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Módulo no disponible",
                    "La ventana de S-DES no está disponible.\n"
                    "Verifique que 'sdes_attack_window.py' esté en la ruta correcta."
                )

        elif project_type == "custom":
            QtWidgets.QMessageBox.information(
                self,
                "En desarrollo",
                "La configuración de proyectos personalizados estará disponible próximamente.\n\n"
                "Esta función permitirá crear cifradores de bloques con parámetros completamente personalizables."
            )

        else:
            QtWidgets.QMessageBox.warning(
                self,
                "Error",
                f"Tipo de proyecto no reconocido: {project_type}"
            )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = NewAnalysisWindow()
    window.show()
    sys.exit(app.exec())