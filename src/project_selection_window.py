# project_selection_window.py
import sys
from PyQt6 import QtWidgets, QtGui, QtCore
from barra_lateral import SidebarWidget

class ProjectSelectionWindow(QtWidgets.QWidget):
    select_project_requested = QtCore.pyqtSignal(dict)
    go_to_history_screen = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CryptJAD - Selección de Proyecto")
        self.setGeometry(100, 100, 1200, 800)
        self.current_selected_project = None
        self.projects_data = self._load_dummy_projects()
        self.init_ui()
        if self.projects_data:
            self._display_project_details(self.projects_data[0])

    def init_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

         # --- Sidebar ---
        self.sidebar = SidebarWidget(self)
        main_layout.addWidget(self.sidebar)

        # --- Contenedor central ---
        central_widget = QtWidgets.QWidget()
        central_layout = QtWidgets.QVBoxLayout(central_widget)
        central_layout.setContentsMargins(20,20,20,20)
        central_layout.setSpacing(20)
        main_layout.addWidget(central_widget)


        # --- Título ---
        self.lbl_titulo = QtWidgets.QLabel("Selección de Proyecto")
        self.lbl_titulo.setFont(QtGui.QFont("Segoe UI", 26, QtGui.QFont.Weight.Bold))
        self.lbl_titulo.setStyleSheet("color: #333;")
        central_layout.addWidget(self.lbl_titulo)

        # --- Vista previa del proyecto ---
        preview_layout = QtWidgets.QVBoxLayout()
        preview_layout.setSpacing(15)

        self.lbl_nombre_proyecto = QtWidgets.QLabel("Nombre del Proyecto")
        self.lbl_nombre_proyecto.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Weight.Bold))
        self.lbl_nombre_proyecto.setStyleSheet("color: #1F3C88;")  # Azul moderno
        preview_layout.addWidget(self.lbl_nombre_proyecto)

        details_layout = QtWidgets.QHBoxLayout()
        details_layout.setSpacing(20)

        # Resumen
        summary_frame = QtWidgets.QFrame(self)
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 15px;
                padding: 15px;
                border: 1px solid #E0E0E0;
            }
        """)
        summary_layout = QtWidgets.QVBoxLayout(summary_frame)
        summary_layout.setSpacing(10)
        summary_title = QtWidgets.QLabel("Resumen")
        summary_title.setFont(QtGui.QFont("Segoe UI", 14, QtGui.QFont.Weight.Bold))
        summary_title.setStyleSheet("color: #555;")
        summary_layout.addWidget(summary_title)
        self.txt_resumen = QtWidgets.QTextBrowser(self)
        self.txt_resumen.setFont(QtGui.QFont("Segoe UI", 12))
        self.txt_resumen.setStyleSheet("border: none; background-color: transparent;")
        summary_layout.addWidget(self.txt_resumen)
        details_layout.addWidget(summary_frame, 1)

        # Parámetros y Resultados
        params_results_frame = QtWidgets.QFrame(self)
        params_results_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 15px;
                padding: 15px;
                border: 1px solid #E0E0E0;
            }
        """)
        params_layout = QtWidgets.QVBoxLayout(params_results_frame)
        params_layout.setSpacing(10)
        params_results_title = QtWidgets.QLabel("Parámetros y Resultados")
        params_results_title.setFont(QtGui.QFont("Segoe UI", 14, QtGui.QFont.Weight.Bold))
        params_results_title.setStyleSheet("color: #555;")
        params_layout.addWidget(params_results_title)
        self.txt_parametros_resultados = QtWidgets.QTextBrowser(self)
        self.txt_parametros_resultados.setFont(QtGui.QFont("Segoe UI", 12))
        self.txt_parametros_resultados.setStyleSheet("border: none; background-color: transparent;")
        params_layout.addWidget(self.txt_parametros_resultados)
        details_layout.addWidget(params_results_frame, 1)

        preview_layout.addLayout(details_layout)
        central_layout.addLayout(preview_layout)

        # --- Botones ---
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setSpacing(20)

        self.btn_seleccionar = QtWidgets.QPushButton("Seleccionar Proyecto")
        self.btn_seleccionar.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Weight.Bold))
        self.btn_seleccionar.setStyleSheet("""
            QPushButton {
                background-color: #1F3C88;
                color: white;
                border-radius: 25px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background-color: #1051B3;
            }
        """)
        self.btn_seleccionar.clicked.connect(self._on_select_project)
        buttons_layout.addWidget(self.btn_seleccionar)

        self.btn_regresar = QtWidgets.QPushButton("Regresar a Mis Proyectos")
        self.btn_regresar.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Weight.Bold))
        self.btn_regresar.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border-radius: 25px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        self.btn_regresar.clicked.connect(self.go_to_history_screen.emit)
        buttons_layout.addWidget(self.btn_regresar)

        central_layout.addLayout(buttons_layout)

         # Sección: Proyectos recientes
        recent_projects_title = QtWidgets.QLabel("Proyectos recientes")
        recent_projects_title.setFont(QtGui.QFont("Arial", 22, QtGui.QFont.Weight.Bold))
        recent_projects_title.setStyleSheet("color: #333;")
        central_layout.addWidget(recent_projects_title)

        self.contenedor_recientes = QtWidgets.QHBoxLayout()
        self.contenedor_recientes.setSpacing(15)
        self.contenedor_recientes.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft) # Alinear tarjetas a la izquierda

        self._populate_recent_projects() # Función para añadir las tarjetas
        central_layout.addLayout(self.contenedor_recientes)

        central_layout.addStretch(1) # Empuja el contenido hacia arriba

    def _load_dummy_projects(self):
        """Carga algunos datos de proyectos de ejemplo."""
        return [
            {"name": "Proyecto Criptoanálisis AES", "id": "proj_aes_1",
             "summary": "Análisis de la resistencia de AES a un ataque de fuerza bruta. Este proyecto evalúa la robustez del algoritmo AES en diferentes configuraciones de clave.",
             "parameters": "Algoritmo: AES-128\nTécnica: Fuerza Bruta\nClave: No especificada",
             "results": "Tiempo estimado: 2^128 operaciones\nConclusión: Seguro ante fuerza bruta simple."},
            {"name": "Análisis Diferencial DES", "id": "proj_des_diff",
             "summary": "Estudio de las propiedades diferenciales de DES para encontrar debilidades en su estructura. Se busca explotar diferencias en las entradas para predecir diferencias en las salidas.",
             "parameters": "Algoritmo: DES\nTécnica: Análisis Diferencial\nRounds: 16",
             "results": "Clave recuperada: Sí (para X rondas)\nComplejidad: 2^47"},
            {"name": "Prueba Algoritmo Personalizado", "id": "proj_custom_test",
             "summary": "Evaluación de un algoritmo de cifrado personalizado creado por el usuario. Se realizan pruebas estadísticas y de rendimiento.",
             "parameters": "Algoritmo: CustomCipher v1.0\nTécnica: Aleatoria\nLongitud Bloque: 64 bits",
             "results": "Estadísticas: Pasa pruebas de NIST STS (algunas)\nObservaciones: Necesita más rondas."},
            {"name": "Cifrado RSA Avanzado", "id": "proj_rsa_test",
             "summary": "Implementación y prueba de un sistema de cifrado asimétrico RSA con manejo de claves seguras.",
             "parameters": "Algoritmo: RSA\nLongitud Clave: 2048 bits\nPadding: OAEP",
             "results": "Rendimiento: 100ms por cifrado\nSeguridad: Satisfactoria con clave grande y padding adecuado."},
            {"name": "Ataque de Canal Lateral (Potencia)", "id": "proj_side_channel",
             "summary": "Simulación de un ataque de canal lateral basado en el consumo de energía para extraer información de operaciones criptográficas.",
             "parameters": "Objetivo: AES (hardware)\nMetodología: Análisis de Potencia Simple (SPA)",
             "results": "Resultado: Clave recuperada parcialmente\nNotas: Ataque viable en entorno de prueba con equipo específico."},
        ]

    def _populate_recent_projects(self):
        """Crea y añade las tarjetas de proyectos recientes."""
        for i, project in enumerate(self.projects_data):
            # Limitar a 4-5 proyectos recientes si hay muchos
            if i >= 5: break

            card_frame = QtWidgets.QFrame(self)
            card_frame.setFixedSize(200, 180) # Tamaño de la tarjeta
            card_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #D3D3D3; /* Bordes grises */
                    border-radius: 10px;
                }
                QFrame:hover {
                    border: 2px solid #219EBC; /* Borde azul al pasar el ratón */
                }
                QLabel { /* Estilo para el texto dentro de la tarjeta */
                    color: #555;
                }
            """)
            card_layout = QtWidgets.QVBoxLayout(card_frame)
            card_layout.setContentsMargins(10, 10, 10, 10)
            card_layout.setSpacing(5)

            # Nombre del proyecto
            name_label = QtWidgets.QLabel(project["name"])
            name_label.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Weight.Bold))
            name_label.setStyleSheet("color: #333;")
            card_layout.addWidget(name_label)
            card_layout.addSpacing(5)

            # Texto Parámetros (Mini-resumen)
            params_label = QtWidgets.QLabel("Parámetros: " + project["parameters"].split('\n')[0]) # Solo la primera línea
            params_label.setFont(QtGui.QFont("Arial", 10))
            params_label.setWordWrap(True)
            card_layout.addWidget(params_label)

            # Texto Resultados (Mini-resumen)
            results_label = QtWidgets.QLabel("Resultados: " + project["results"].split('\n')[0]) # Solo la primera línea
            results_label.setFont(QtGui.QFont("Arial", 10))
            results_label.setWordWrap(True)
            card_layout.addWidget(results_label)

            card_layout.addStretch(1) # Empuja el contenido hacia arriba

            # Hacer la tarjeta clickeable
            card_frame.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            click_overlay = QtWidgets.QPushButton("", card_frame) # Botón transparente que cubre la tarjeta
            click_overlay.setGeometry(card_frame.contentsRect()) # Ocupa todo el contenido
            click_overlay.setStyleSheet("background-color: transparent; border: none;")
            click_overlay.clicked.connect(lambda p=project: self._display_project_details(p))

            self.contenedor_recientes.addWidget(card_frame)

    def _display_project_details(self, project):
        """Actualiza el área de vista previa con los detalles del proyecto dado."""
        self.current_selected_project = project
        self.lbl_nombre_proyecto.setText(project["name"])
        self.txt_resumen.setText(project["summary"])
        self.txt_parametros_resultados.setText(
            f"<b>Parámetros:</b><br>{project['parameters']}<br><br><b>Resultados:</b><br>{project['results']}"
        )

    def _on_select_project(self):
        """Maneja el clic en el botón 'Seleccionar proyecto'."""
        if self.current_selected_project:
            QtWidgets.QMessageBox.information(self, "Proyecto Seleccionado",
                                              f"Proyecto '{self.current_selected_project['name']}' seleccionado. "
                                              "Aquí se redirigiría a la interfaz de análisis.")
            self.select_project_requested.emit(self.current_selected_project)
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "No hay ningún proyecto seleccionado.")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ProjectSelectionWindow()
    window.show()
    sys.exit(app.exec())