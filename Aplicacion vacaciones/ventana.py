import sys, math, ventanaC,datos,ventanaC2_gpt
from PyQt5.QtWidgets import (
     QApplication, QMainWindow, QWidget, QLabel, 
     QPushButton, QLineEdit, QMessageBox, QComboBox, 
)

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt


class VentanaPython(QMainWindow):
      def __init__(self): 
          super().__init__()
          self.pesonalizarVentana()
          self.personalizarComponentes()

      def pesonalizarVentana(self):
          self.setWindowTitle("INICIO SESIÓN")  # Crear una ventana y poner un título
          self.setFixedSize(430, 230) # Poner un ancho y altura a la ventana y no redimensiona
          self.setStyleSheet("background-color: lightgrey") # Color de fondo

          # Centrar la ventana en la pantalla
          self.pnlPrincipal = QWidget() # Crear un contenedor principal
          self.setCentralWidget(self.pnlPrincipal) # Establecer el contenedor principal para nuestra ventana
     
      def personalizarComponentes(self):
          self.lblUsuario = QLabel("USUARIO:",self.pnlPrincipal) #Crear objeto label
          self.lblUsuario.setFont(QFont("Helvetica", 10))
          self.lblUsuario.setStyleSheet("color: #000000;") #Color letra RGB
          self.lblUsuario.setAlignment(Qt.AlignLeft)
          self.lblUsuario.setGeometry(100, 60, 150, 20)

          self.lblContraseña = QLabel("CONTRASEÑA:",self.pnlPrincipal) #Crear objeto label
          self.lblContraseña.setFont(QFont("Helvetica", 10))
          self.lblContraseña.setStyleSheet("color: #000000;") #Color letra RGB
          self.lblContraseña.setAlignment(Qt.AlignLeft)
          self.lblContraseña.setGeometry(100, 120, 150, 20) 

          self.txtUsuario = QLineEdit(self.pnlPrincipal)
          self.txtUsuario.setGeometry(220, 60, 100, 20)
          self.txtUsuario.setFont(QFont("Helvetica", 9))
          self.txtUsuario.setAlignment(Qt.AlignCenter)
          self.txtUsuario.setStyleSheet("color: black;")    

          self.txtContraseña = QLineEdit(self.pnlPrincipal)
          self.txtContraseña.setGeometry(220, 120, 100, 20)
          self.txtContraseña.setFont(QFont("Helvetica", 9))
          self.txtContraseña.setAlignment(Qt.AlignCenter)
          self.txtContraseña.setStyleSheet("color: black;")  
          self.txtContraseña.setEchoMode(QLineEdit.Password)                               

          self.btoAceptar = QPushButton("ACEPTAR", self)
          self.btoAceptar.setGeometry(170, 180, 80, 20)
          self.btoAceptar.setFont(QFont("Helvetica-Bold", 0, 8))
          self.btoAceptar.setStyleSheet("background-color: LightSteelBlue; color: black;margin: round")
          self.btoAceptar.clicked.connect(self.comprobar)

      def comprobar(self):
          usuario = self.txtUsuario.text()

          contraseña = self.txtContraseña.text()

          for i in range(len(datos.usuario)):
            if usuario == datos.usuario[i] and contraseña == datos.password[i]:
                  self.mostrar_mensaje_exito()
                  self.abrirVentanaC(datos.nombre[i], datos.empresa[i], datos.departamento[i], datos.dias_vacaciones[i])
                  break
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

      def abrirVentanaC(self, nombre, empresa, departamento, dias_vacaciones):
         self.objeto_ventanaC = ventanaC.Ventana(nombre, empresa, departamento, dias_vacaciones)
         self.objeto_ventanaC.show()
          
if __name__ == '__main__':       # METODO PRINCIPAL
    app = QApplication(sys.argv) # ABRIR APLICACION
    ventana = VentanaPython()    # Objeto de la ventana
    ventana.show()               # Muestra la ventana
    sys.exit(app.exec_())        # CERRAR APLICACION
  