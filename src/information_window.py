import sys
from PyQt6 import QtWidgets, QtGui, QtCore

class InformationWindow(QtWidgets.QWidget):
    # Señal para volver al Dashboard
    go_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptJAD - Información")
        self.setGeometry(100, 100, 1200, 800) # Mismo tamaño para coherencia
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop) # Alinear el contenido arriba

        # Título de la pantalla
        title_label = QtWidgets.QLabel("Información sobre CryptJAD y Criptoanálisis")
        title_label.setFont(QtGui.QFont("Arial", 36, QtGui.QFont.Weight.Bold))
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(title_label)

        # Sección sobre CryptJAD
        cryptjad_title = QtWidgets.QLabel("Acerca de CryptJAD")
        cryptjad_title.setFont(QtGui.QFont("Arial", 24, QtGui.QFont.Weight.Bold))
        cryptjad_title.setContentsMargins(0, 20, 0, 10)
        main_layout.addWidget(cryptjad_title)

        cryptjad_info = QtWidgets.QLabel(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor "
            "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
            "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure "
            "dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
            "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt "
            "mollit anim id est laborum."
        )
        cryptjad_info.setFont(QtGui.QFont("Arial", 14))
        cryptjad_info.setWordWrap(True) # Para que el texto se ajuste
        main_layout.addWidget(cryptjad_info)

        # Sección sobre Criptoanálisis
        cryptoanalysis_title = QtWidgets.QLabel("¿Qué es el Criptoanálisis?")
        cryptoanalysis_title.setFont(QtGui.QFont("Arial", 24, QtGui.QFont.Weight.Bold))
        cryptoanalysis_title.setContentsMargins(0, 20, 0, 10)
        main_layout.addWidget(cryptoanalysis_title)

        cryptoanalysis_info = QtWidgets.QLabel(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut enim ad minim veniam, "
            "quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
            "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu "
            "fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in "
            "culpa qui officia deserunt mollit anim id est laborum. "
            "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium "
            "doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore "
            "veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam "
            "voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur "
            "magni dolores eos qui ratione voluptatem sequi nesciunt."
        )
        cryptoanalysis_info.setFont(QtGui.QFont("Arial", 14))
        cryptoanalysis_info.setWordWrap(True)
        main_layout.addWidget(cryptoanalysis_info)

        main_layout.addStretch(1) # Empuja el contenido hacia arriba

        # Botón "Volver"
        back_btn = QtWidgets.QPushButton("Volver al Dashboard")
        back_btn.setFixedSize(200, 50)
        back_btn.setFont(QtGui.QFont("Arial", 16))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #219EBC;
                color: white;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: #167DAB;
            }
        """)
        back_btn.clicked.connect(self.go_to_dashboard.emit)
        main_layout.addWidget(back_btn, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)