import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox

class VentanaEnviarEmail(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enviar Documento por Correo")
        self.setFixedSize(400, 300)

        self.layout = QVBoxLayout()

        self.label_destinatario = QLabel("Destinatario:")
        self.layout.addWidget(self.label_destinatario)

        self.text_destinatario = QLineEdit(self)
        self.layout.addWidget(self.text_destinatario)

        self.label_asunto = QLabel("Asunto:")
        self.layout.addWidget(self.label_asunto)

        self.text_asunto = QLineEdit(self)
        self.layout.addWidget(self.text_asunto)

        self.label_mensaje = QLabel("Mensaje:")
        self.layout.addWidget(self.label_mensaje)

        self.text_mensaje = QLineEdit(self)
        self.layout.addWidget(self.text_mensaje)

        self.boton_adjuntar = QPushButton("Adjuntar Archivo", self)
        self.boton_adjuntar.clicked.connect(self.adjuntar_archivo)
        self.layout.addWidget(self.boton_adjuntar)

        self.boton_enviar = QPushButton("Enviar", self)
        self.boton_enviar.clicked.connect(self.enviar_correo)
        self.layout.addWidget(self.boton_enviar)

        self.setLayout(self.layout)
        self.archivo_adjunto = None

    def adjuntar_archivo(self):
        opciones = QFileDialog.Options()
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo", "", "Todos los archivos (*)", options=opciones)
        if archivo:
            self.archivo_adjunto = archivo

    def enviar_correo(self):
        destinatario = self.text_destinatario.text()
        asunto = self.text_asunto.text()
        mensaje = self.text_mensaje.text()

        if not destinatario or not asunto or not mensaje or not self.archivo_adjunto:
            QMessageBox.warning(self, "Error", "Todos los campos y el archivo adjunto son obligatorios.")
            return

        try:
            remitente = "tucorreo@ejemplo.com"  # Reemplaza con tu correo
            password = "tucontraseña"  # Reemplaza con tu contraseña

            msg = MIMEMultipart()
            msg['From'] = remitente
            msg['To'] = destinatario
            msg['Subject'] = asunto

            msg.attach(MIMEText(mensaje, 'plain'))

            attachment = open(self.archivo_adjunto, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {self.archivo_adjunto.split('/')[-1]}")
            msg.attach(part)

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(remitente, password)
            text = msg.as_string()
            server.sendmail(remitente, destinatario, text)
            server.quit()

            QMessageBox.information(self, "Éxito", "Correo enviado correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al enviar el correo: {e}")   