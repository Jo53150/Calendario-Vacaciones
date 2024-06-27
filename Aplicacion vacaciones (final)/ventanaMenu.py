import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QMessageBox
import ventanaCalendario
import ventanaEnviarEmail

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
        self.setWindowTitle("Menú")
        self.setGeometry(100, 100, 300, 200)
        self.setFixedSize(300, 200)

        # Crear un widget central y un layout vertical
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Crear botones para cada opción del menú
        button_opcion1 = QPushButton("Calendario")
        button_opcion2 = QPushButton("Enviar Email")

        # Conectar botones a funciones correspondientes
        button_opcion1.clicked.connect(self.opcion1_click)
        button_opcion2.clicked.connect(self.opcion2_click)

        # Agregar botones al layout vertical
        layout.addWidget(button_opcion1)
        layout.addWidget(button_opcion2)

    def opcion1_click(self):
        self.objeto_ventanaC = ventanaCalendario.CalendarWindow(
            self.nombre, self.empresa, self.departamento, 
            self.dias_vacaciones_disponibles, 
            self.dias_fiestas_locales_disponibles, 
            self.dias_otros_motivos_disponibles
        )
        self.objeto_ventanaC.show()

    def opcion2_click(self):
        self.objecto_ventanaEmail = ventanaEnviarEmail.EmailSenderWindow(self.nombre,self.empresa,self.departamento)
        self.objecto_ventanaEmail.show()

    def mostrar_mensaje(self, mensaje):
        message = QMessageBox()
        message.setIcon(QMessageBox.Information)
        message.setText(mensaje)
        message.setWindowTitle("Información")
        message.setStandardButtons(QMessageBox.Ok)
        message.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow("nombre", "empresa", "departamento", 10, 5, 3)  # Ejemplo de valores/Sirve para iniciar la ventana sin pasar por el login
    window.show()
    sys.exit(app.exec_())