import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, 
    QPushButton, QLineEdit, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import mysql.connector
from mysql.connector import Error
import ventanaC2_gpt

class VentanaPython(QMainWindow):
    def __init__(self): 
        super().__init__()
        self.conectar_base_datos()
        self.pesonalizarVentana()
        self.personalizarComponentes()

    def conectar_base_datos(self):
        try:
            self.conexion = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="",
                database="calendario",
                port=3306  # Asegúrate de que este es el puerto correcto
            )
            if self.conexion.is_connected():
                self.cursor = self.conexion.cursor()
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            QMessageBox.critical(self, "Error de conexión", f"No se pudo conectar a la base de datos MySQL:\n{e}", QMessageBox.Ok)
            sys.exit(1)

    def pesonalizarVentana(self):
        self.setWindowTitle("INICIO SESIÓN")
        self.setFixedSize(430, 230)
        self.setStyleSheet("background-color: lightgrey")

        self.panelPrincipal = QWidget()
        self.setCentralWidget(self.panelPrincipal)

    def personalizarComponentes(self):
        self.labelUsuario = QLabel("USUARIO:", self.panelPrincipal)
        self.labelUsuario.setFont(QFont("Helvetica", 10))
        self.labelUsuario.setStyleSheet("color: #000000;")
        self.labelUsuario.setAlignment(Qt.AlignLeft)
        self.labelUsuario.setGeometry(100, 60, 150, 20)

        self.labelContraseña = QLabel("CONTRASEÑA:", self.panelPrincipal)
        self.labelContraseña.setFont(QFont("Helvetica", 10))
        self.labelContraseña.setStyleSheet("color: #000000;")
        self.labelContraseña.setAlignment(Qt.AlignLeft)
        self.labelContraseña.setGeometry(100, 120, 150, 20)

        self.textUsuario = QLineEdit(self.panelPrincipal)
        self.textUsuario.setGeometry(220, 60, 100, 20)
        self.textUsuario.setFont(QFont("Helvetica", 9))
        self.textUsuario.setAlignment(Qt.AlignCenter)
        self.textUsuario.setStyleSheet("color: black;")

        self.textContraseña = QLineEdit(self.panelPrincipal)
        self.textContraseña.setGeometry(220, 120, 100, 20)
        self.textContraseña.setFont(QFont("Helvetica", 9))
        self.textContraseña.setAlignment(Qt.AlignCenter)
        self.textContraseña.setStyleSheet("color: black;")
        self.textContraseña.setEchoMode(QLineEdit.Password)

        self.buttonAceptar = QPushButton("ACEPTAR", self)
        self.buttonAceptar.setGeometry(170, 180, 80, 20)
        self.buttonAceptar.setFont(QFont("Helvetica-Bold", 0, 8))
        self.buttonAceptar.setStyleSheet("background-color: LightSteelBlue; color: black;margin: round")
        self.buttonAceptar.clicked.connect(self.comprobar)

    def comprobar(self):
        usuario = self.textUsuario.text()
        contraseña = self.textContraseña.text()

        consulta = "SELECT nombre, empresa, departamento FROM usuarios WHERE usuario = %s AND password = %s"
        valores = (usuario, contraseña)
        self.cursor.execute(consulta, valores)
        resultado = self.cursor.fetchone()

        if resultado:
            nombre, empresa, departamento = resultado
            self.mostrar_mensaje_exito()
            self.abrirVentanaC(nombre, empresa, departamento)
        else:
            self.mostrar_mensaje_error()

    def mostrar_mensaje_exito(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Inicio de sesión exitoso")
        msg.setWindowTitle("Éxito")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def mostrar_mensaje_error(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Usuario o contraseña incorrectos")
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def abrirVentanaC(self, nombre, empresa, departamento):
        self.objeto_ventanaC = ventanaC2_gpt.CalendarWindow(nombre, empresa, departamento)
        self.objeto_ventanaC.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaPython()
    ventana.show()
    sys.exit(app.exec_())