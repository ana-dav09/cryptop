import sys
from PyQt6 import QtWidgets, QtGui, QtCore


class InicioWindow(QtWidgets.QWidget):
    login_requested = QtCore.pyqtSignal()
    register_requested = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD - Analizador Criptográfico")
        self.setGeometry(100, 100, 1000, 700)
        self.current_page = 0
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Header ---
        header_frame = QtWidgets.QFrame(self)
        header_frame.setObjectName("navbar")
        header_layout = QtWidgets.QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 5, 20, 5)

        logo_label = QtWidgets.QLabel("CryptJAD")
        logo_label.setObjectName("logo")
        header_layout.addWidget(logo_label)
        header_layout.addStretch()

        login_btn = QtWidgets.QPushButton("Iniciar sesión")
        login_btn.setObjectName("signIn")
        login_btn.clicked.connect(self.request_login)

        register_btn = QtWidgets.QPushButton("Registro")
        register_btn.setObjectName("signUp")
        register_btn.clicked.connect(self.request_register)

        header_layout.addWidget(login_btn)
        header_layout.addWidget(register_btn)
        main_layout.addWidget(header_frame)

        # --- Hero ---
        hero_layout = QtWidgets.QVBoxLayout()
        hero_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        hero_layout.setSpacing(15)

        title_label = QtWidgets.QLabel("Analizador criptográfico")
        title_label.setObjectName("heroTitle")
        hero_layout.addWidget(title_label)

        subtitle_label = QtWidgets.QLabel("¿Tu algoritmo es seguro?")
        subtitle_label.setObjectName("heroSubtitle")
        hero_layout.addWidget(subtitle_label)

        register_main_btn = QtWidgets.QPushButton("Comienza ahora")
        register_main_btn.setObjectName("mainCTA")
        register_main_btn.clicked.connect(self.request_register)
        hero_layout.addWidget(register_main_btn)

        main_layout.addLayout(hero_layout)

        # --- Carrusel de Cards ---
        self.carousel = QtWidgets.QStackedWidget()
        self.carousel.setObjectName("carousel")
        main_layout.addWidget(self.carousel)

        # Datos de cards (varias páginas de stock)
        pages_data = [
            [
                ("Personaliza", "Modifica parámetros de un algoritmo preestablecido"),
                ("Analiza", "Ejecuta análisis diferencial, lineal y algebraico"),
                ("Resultados", "Visualiza y exporta informes completos"),
            ],
            [
                ("AES", "Analiza la seguridad de AES con distintos ataques"),
                ("DES", "Ejecuta criptoanálisis diferencial en DES"),
                ("Present", "Evalúa algoritmos livianos como Present"),
            ],
            [
                ("Historial", "Consulta proyectos anteriores"),
                ("Reportes", "Genera reportes en PDF o imagen"),
                ("Exportar", "Guarda tus análisis para compartirlos"),
            ]
        ]

        for page_cards in pages_data:
            page = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(page)
            layout.setSpacing(30)
            layout.setContentsMargins(50, 20, 50, 20)

            for title, desc in page_cards:
                card = QtWidgets.QFrame()
                card.setObjectName("card")
                card_layout = QtWidgets.QVBoxLayout(card)
                card_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

                icon = QtWidgets.QLabel("🔒")
                icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                icon.setStyleSheet("font-size: 40px;")
                card_layout.addWidget(icon)

                card_title = QtWidgets.QLabel(title)
                card_title.setObjectName("cardTitle")
                card_layout.addWidget(card_title)

                card_desc = QtWidgets.QLabel(desc)
                card_desc.setObjectName("cardDesc")
                card_desc.setWordWrap(True)
                card_desc.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                card_layout.addWidget(card_desc)

                layout.addWidget(card)

            self.carousel.addWidget(page)

        # --- Flechas navegación ---
        nav_layout = QtWidgets.QHBoxLayout()
        nav_layout.setSpacing(40)
        nav_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.left_arrow_btn = QtWidgets.QPushButton("◀")
        self.left_arrow_btn.setObjectName("navArrow")
        self.left_arrow_btn.clicked.connect(self.show_prev_page)

        self.right_arrow_btn = QtWidgets.QPushButton("▶")
        self.right_arrow_btn.setObjectName("navArrow")
        self.right_arrow_btn.clicked.connect(self.show_next_page)

        nav_layout.addWidget(self.left_arrow_btn)
        nav_layout.addWidget(self.right_arrow_btn)
        main_layout.addLayout(nav_layout)

        # --- Footer ---
        footer_label = QtWidgets.QLabel("© 2025 CryptJAD – Todos los derechos reservados")
        footer_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        footer_label.setObjectName("footer")
        main_layout.addWidget(footer_label)

        # Estilos
        self.setStyleSheet("""
        #navbar { background-color: #2C3E50; }
        #logo { color: white; font-size: 20px; font-weight: bold; }
        QPushButton#signIn, QPushButton#signUp {
            background-color: transparent; color: white; padding: 6px 12px; border-radius: 5px;
        }
        QPushButton#signIn:hover, QPushButton#signUp:hover { background-color: #1ABC9C; }

        #heroTitle { font-size: 32px; font-weight: bold; }
        #heroSubtitle { font-size: 18px; color: #555; }
        QPushButton#mainCTA {
            background-color: #e42c1f; color: white; border-radius: 25px; padding: 12px 24px; font-size: 16px;
        }
        QPushButton#mainCTA:hover { background-color: #c9302c; }

        #card {
            background-color: white; border: 1px solid #ddd; border-radius: 12px;
            padding: 20px; min-width: 200px;
        }
        #cardTitle { font-size: 18px; font-weight: bold; margin-top: 10px; }
        #cardDesc { font-size: 14px; color: #666; }

        QPushButton#navArrow {
            background-color: #3498DB; color: white; font-size: 20px;
            border-radius: 8px; padding: 8px 16px;
        }
        QPushButton#navArrow:hover { background-color: #2980B9; }

        #footer { font-size: 12px; color: #888; margin-top: 20px; }
        """)

    # Navegación carrusel
    def show_next_page(self):
        next_index = (self.carousel.currentIndex() + 1) % self.carousel.count()
        self.carousel.setCurrentIndex(next_index)

    def show_prev_page(self):
        prev_index = (self.carousel.currentIndex() - 1) % self.carousel.count()
        self.carousel.setCurrentIndex(prev_index)

    # Señales
    def request_login(self):
        self.login_requested.emit()

    def request_register(self):
        self.register_requested.emit()

