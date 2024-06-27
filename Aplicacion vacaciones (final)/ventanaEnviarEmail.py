import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QFileDialog, QMessageBox
)
import requests

class EmailSenderWindow(QMainWindow):
    def __init__(self, nombre, empresa, departamento):
        super().__init__()
        self.nombre = nombre
        self.empresa = empresa
        self.departamento = departamento
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Enviar y Descargar Archivos')
        self.setGeometry(100, 100, 600, 400)
        self.setFixedSize(600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Crear los componentes de la interfaz
        self.label = QLabel(f'Nombre: {self.nombre}\nEmpresa: {self.empresa}\nDepartamento: {self.departamento}')
        self.label_to = QLabel("Para: ")
        self.input_to = QLineEdit()
        
        self.label_subject = QLabel('Asunto:')
        self.input_subject = QLineEdit()
        
        self.label_body = QLabel('Mensaje:')
        self.input_body = QTextEdit(f"Mi nombre es {self.nombre} de la empresa {self.empresa} del departamento {self.departamento}")

        self.label_attachment = QLabel('Archivo adjunto:')
        self.label_attachment_path = QLabel('No hay archivo adjunto')
        self.btn_attach = QPushButton('Adjuntar Archivo')
        self.btn_attach.clicked.connect(self.adjuntar_archivo)

        self.btn_send = QPushButton('Enviar Correo')
        self.btn_send.clicked.connect(self.enviar_correo)

        self.label_download = QLabel('Descargar Archivo:')
        self.input_download_url = QLineEdit()
        self.btn_download = QPushButton('Descargar')
        self.btn_download.clicked.connect(self.descargar_archivo)

        # Agregar componentes al layout
        layout.addWidget(self.label)
        layout.addWidget(self.label_to)
        layout.addWidget(self.input_to)
        layout.addWidget(self.label_subject)
        layout.addWidget(self.input_subject)
        layout.addWidget(self.label_body)
        layout.addWidget(self.input_body)
        layout.addWidget(self.label_attachment)
        layout.addWidget(self.label_attachment_path)
        layout.addWidget(self.btn_attach)
        layout.addWidget(self.btn_send)
        layout.addWidget(self.label_download)
        layout.addWidget(self.input_download_url)
        layout.addWidget(self.btn_download)

    def adjuntar_archivo(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo", "", "All Files (*);;Text Files (*.txt)", options=options)
        if file_name:
            self.attachment_path = file_name
            self.label_attachment_path.setText(file_name)

    def enviar_correo(self):
        to = self.input_to.text()
        subject = self.input_subject.text()
        body = self.input_body.toPlainText()
        attachment_path = getattr(self, 'attachment_path', None)

        msg = MIMEMultipart()
        msg['From'] = 'tu_correo@gmail.com'
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        if attachment_path:
            attachment = open(attachment_path, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(attachment_path)}")
            msg.attach(part)

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login('tu_correo@gmail.com', 'tu_contraseña')
            text = msg.as_string()
            server.sendmail('tu_correo@gmail.com', to, text)
            server.quit()
            self.mostrar_mensaje('Éxito', 'Correo enviado exitosamente')
        except Exception as e:
            self.mostrar_mensaje('Error', f'Error al enviar el correo: {str(e)}')

    def descargar_archivo(self):
        url = self.input_download_url.text()
        try:
            response = requests.get(url)
            file_name = url.split('/')[-1]
            with open(file_name, 'wb') as file:
                file.write(response.content)
            self.mostrar_mensaje('Éxito', f'Archivo descargado: {file_name}')
        except Exception as e:
            self.mostrar_mensaje('Error', f'Error al descargar el archivo: {str(e)}')

    def mostrar_mensaje(self, titulo, mensaje):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(mensaje)
        msg.setWindowTitle(titulo)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmailSenderWindow("Prueba", "Prueba", "Prueba") # Ejemplo de valores/Sirve para iniciar la ventana sin pasar por el login
    window.show()
    sys.exit(app.exec_())
 