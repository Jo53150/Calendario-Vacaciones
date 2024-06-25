import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QMessageBox
import ventanaCalendario

dias_vacaciones = []
dias_fiestas_locales = []
dias_otros_motivos = []

class MainWindow(QMainWindow):
    def __init__(self, nombre, empresa, departamento, dias_vacaciones, dias_fiestas_locales, dias_otros_motivos):
        super().__init__()
        self.initUI()
        self.nombre = nombre
        self.empresa = empresa
        self.departamento = departamento
        self.dias_vacaciones_disponibles = dias_vacaciones
        self.dias_fiestas_locales_disponibles = dias_fiestas_locales
        self.dias_otros_motivos_disponibles = dias_otros_motivos


    def initUI(self):
        self.setWindowTitle("Menú con Botones")
        self.setGeometry(100, 100, 300, 300)

        # Crear un widget central y un layout vertical
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Crear botones para cada opción del menú
        btn_opcion1 = QPushButton("Opción 1")
        btn_opcion2 = QPushButton("Opción 2")

        # Conectar botones a funciones correspondientes
        btn_opcion1.clicked.connect(self.opcion1_click)
        btn_opcion2.clicked.connect(self.opcion2_click)

        # Agregar botones al layout vertical
        layout.addWidget(btn_opcion1)
        layout.addWidget(btn_opcion2)

    def opcion1_click(self, nombre, empresa, departamento, dias_vacaciones, dias_fiestas_locales, dias_otros_motivos):
        self.objeto_ventanaC = ventanaCalendario.CalendarWindow(nombre, empresa, departamento, dias_vacaciones, dias_fiestas_locales, dias_otros_motivos)
        self.objeto_ventanaC.show()
        self.mostrar_mensaje("Opción 1 seleccionada")

    def opcion2_click(self):
        self.mostrar_mensaje("Opción 2 seleccionada")


    def mostrar_mensaje(self, mensaje):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(mensaje)
        msg.setWindowTitle("Información")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())