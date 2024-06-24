import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QCalendarWidget, QPushButton, QLineEdit, QMessageBox, QComboBox
from PyQt5.QtGui import QFont, QTextCharFormat, QColor
from PyQt5.QtCore import Qt, QDate
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pdf import create_calendar

# Definir los días festivos y libres internos
feriados = [QDate(2024, 12, 25), QDate(2024, 10, 12), QDate(2024, 11, 1), QDate(2024, 12, 6), QDate(2024, 8, 15), QDate(2024, 7, 25)]
libre_interno = [QDate(2024, 7, 26), QDate(2024, 12, 24), QDate(2024, 12, 31)]

# Listas para almacenar las fechas seleccionadas
dias_vacaciones = []
dias_fiestas_locales = []
dias_otros_motivos = []

def send_email(subject, body, attachment_path, recipient_email, sender_email, sender_password):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    attachment = open(attachment_path, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(attachment_path)}")
    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    text = msg.as_string()
    server.sendmail(sender_email, recipient_email, text)
    server.quit()

class CalendarWindow(QMainWindow):
    def __init__(self,nombre,empresa,departamento):
        super().__init__()

        self.nombre = nombre
        self.empresa = empresa
        self.departamento = departamento

        self.setWindowTitle("Calendario de Vacaciones")
        self.setFixedSize(730, 400)

        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.move(50, 50)
        self.calendar.resize(400, 300)

        self.category_label = QLabel("Categoría:", self)
        self.category_label.move(500, 60)
        self.category_combo = QComboBox(self)
        self.category_combo.addItems(["Vacaciones", "Fiestas Locales", "Otros Motivos"])
        self.category_combo.move(570, 60)

        self.name_label = QLabel("Nombre:", self)
        self.name_label.move(500, 100)
        self.name_input = QLineEdit(self)
        self.name_input.move(570, 100)
        self.name_input.setReadOnly(True)
        self.name_input.setText(self.nombre)

        self.company_label = QLabel("Empresa:", self)
        self.company_label.move(500, 140)
        self.company_input = QLineEdit(self)
        self.company_input.move(570, 140)
        self.company_input.setReadOnly(True)
        self.company_input.setText(self.empresa)

        self.department_label = QLabel("Departamento:", self)
        self.department_label.move(500, 180)
        self.department_input = QLineEdit(self)
        self.department_input.move(580, 180)
        self.department_input.setReadOnly(True)
        self.department_input.setText(self.departamento)

        self.calendar.clicked.connect(self.mark_date)

        self.generate_button = QPushButton("Generar PDF", self)
        self.generate_button.move(540, 220)
        self.generate_button.clicked.connect(self.generate_calendar)

        self.email_label = QLabel("Email:", self)
        self.email_label.move(500, 260)
        self.email_input = QLineEdit(self)
        self.email_input.move(550, 260)

        self.send_button = QPushButton("Enviar Email", self)
        self.send_button.move(540, 300)
        self.send_button.clicked.connect(self.send_calendar_email)

        self.marked_days = []
        self.fiestas_locales = []
        self.otros_motivos = []
        self.mark_Feriados()
        self.mark_Interno()

    def mark_date(self, date):
        if date in dias_vacaciones or date in dias_fiestas_locales or date in dias_otros_motivos or date in feriados or date in libre_interno:
            QMessageBox.warning(self, "Error", "Este día ya ha sido seleccionado o es un feriado.")
            return

        category = self.category_combo.currentText()
        if category == "Vacaciones":
            if date not in dias_vacaciones:
                dias_vacaciones.append(date)
                self.mark_date_in_calendar(date, QColor("lightgreen"))
            else:
                dias_vacaciones.remove(date)
                self.mark_date_in_calendar(date, QColor("white"))    
        elif category == "Fiestas Locales":
            if date not in dias_fiestas_locales:
                dias_fiestas_locales.append(date)
                self.mark_date_in_calendar(date, QColor("royalblue"))
            else:
                dias_fiestas_locales.remove(date)
                self.mark_date_in_calendar(date, QColor("white"))
        elif category == "Otros Motivos":
            if date not in dias_otros_motivos:
                dias_otros_motivos.append(date)
                self.mark_date_in_calendar(date, QColor("lightsalmon"))
            else:
                dias_otros_motivos.remove(date)
                self.mark_date_in_calendar(date, QColor("white"))

    def mark_date_in_calendar(self, date, color):
        format = QTextCharFormat()
        format.setBackground(color)
        self.calendar.setDateTextFormat(date, format)

    def generate_calendar(self):
        nombre = self.name_input.text()
        empresa = self.company_input.text()
        departamento = self.department_input.text()

        marked_days = [(date.day(), date.month()) for date in dias_vacaciones]
        fiestas_locales = [(date.day(), date.month()) for date in dias_fiestas_locales]
        otros_motivos = [(date.day(), date.month()) for date in dias_otros_motivos]

        create_calendar(2024, "calendario_vacaciones.pdf", marked_days, fiestas_locales, otros_motivos, nombre, empresa, departamento)


        QMessageBox.information(self, "Éxito", "Calendario generado exitosamente.")

    def mark_Feriados(self):
        format = QTextCharFormat()
        format.setBackground(QColor("darkRed"))
        for date in feriados:
            self.calendar.setDateTextFormat(date, format)


    def mark_Interno(self):
        format = QTextCharFormat()
        format.setBackground(QColor("green"))
        for date in libre_interno:
            self.calendar.setDateTextFormat(date, format)
    

    def send_calendar_email(self):
        recipient_email = self.email_input.text()
        sender_email = "joseantoniomg06@gmail.com"
        sender_password = "fmcs aice crhe lbzv"

        if not recipient_email:
            QMessageBox.warning(self, "Error", "Por favor ingrese un correo electrónico.")
            return

        subject = "Calendario de Vacaciones"
        body = "Adjunto encontrarás el calendario de vacaciones."
        attachment_path = "calendario_vacaciones.pdf"

        try:
            send_email(subject, body, attachment_path, recipient_email, sender_email, sender_password)
            QMessageBox.information(self, "Éxito", "Correo enviado exitosamente.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo enviar el correo. Error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalendarWindow("Prueba", "Prueba", "Prueba")
    window.show()
    sys.exit(app.exec_())