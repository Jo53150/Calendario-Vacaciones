import sys
import os
import calendar
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QCalendarWidget, QPushButton, QLineEdit, QMessageBox, QComboBox
from PyQt5.QtGui import QFont, QTextCharFormat, QColor
from PyQt5.QtCore import Qt, QDate
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Definir los días festivos y libres internos
feriados = [QDate(2024, 12, 25), QDate(2024, 10, 12), QDate(2024, 11, 1), QDate(2024, 12, 6), QDate(2024, 8, 15), QDate(2024, 7, 25)]
libre_interno = [QDate(2024, 7, 26), QDate(2024, 12, 24), QDate(2024, 12, 31)]

# Listas para almacenar las fechas seleccionadas
dias_vacaciones = []
dias_fiestas_locales = []
dias_otros_motivos = []

def draw_month(canvas, year, month, start_x, start_y, month_width, month_height, marked_days, fiestas_locales, otros_motivos):
    cal = calendar.Calendar(firstweekday=0)
    month_names_es = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    month_name = month_names_es[month - 1]
    month_days = list(cal.itermonthdays(year, month))
    feriados = [(25, 12), (12, 10), (1, 11), (6, 12), (15, 8), (25, 7)]
    libre_interno = [(26, 7), (24, 12), (31, 12)]

    data = [['' for _ in range(7)] for _ in range(6)]
    days_es = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

    week = 0
    for i, day in enumerate(month_days):
        if day != 0:
            day_str = str(day)
            data[week][i % 7] = day_str
        if (i + 1) % 7 == 0:
            week += 1

    table = Table(data, colWidths=[month_width / 7] * 7, rowHeights=[month_height / 6] * 6)

    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ])

    for week in range(len(data)):
        for day in range(len(data[week])):
            day_str = data[week][day]
            if day_str != '' and (int(day_str), month) in marked_days:
                style.add('BACKGROUND', (day, week), (day, week), colors.lightgreen)
            if day_str != '' and (int(day_str), month) in feriados:
                style.add('BACKGROUND', (day, week), (day, week), colors.red)
            if day_str != '' and (int(day_str), month) in libre_interno:
                style.add('BACKGROUND', (day, week), (day, week), colors.green)
            if day_str != '' and (int(day_str), month) in fiestas_locales:
                style.add('BACKGROUND', (day, week), (day, week), colors.orange)
            if day_str != '' and (int(day_str), month) in otros_motivos:
                style.add('BACKGROUND', (day, week), (day, week), colors.blue)

    table.setStyle(style)

    table.wrapOn(canvas, month_width, month_height)
    table.drawOn(canvas, start_x, start_y)

    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(start_x + month_width / 2 - inch, start_y + month_height + 0.3 * inch, f"{month_name}")

    canvas.setFont("Helvetica", 8)
    day_width = month_width / 7
    for i, day in enumerate(days_es):
        canvas.drawString(start_x + i * day_width + 0 * inch, start_y + month_height + 0.1 * inch, day)

def create_calendar(year, filename, marked_days, fiestas_locales, otros_motivos, nombre, empresa, departamento):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    margin = 50
    padding = 50

    c.setFont("Helvetica-Bold", 6)
    c.drawString(margin, height - margin, f"Nombre: {nombre}")
    c.drawString(margin, height - margin - 14, f"Empresa: {empresa}")
    c.drawString(margin, height - margin - 28, f"Departamento: {departamento}")

    months_per_row = 3
    months_per_col = 4

    month_width = (width - 1.5 * margin - (months_per_row - 1) * padding) / months_per_row
    month_height = (height - 8 * margin - (months_per_col - 1) * padding) / months_per_col

    x_start = margin - 10
    y_start = height - margin - 70

    for month in range(1, 13):
        row = (month - 1) // months_per_row
        col = (month - 1) % months_per_row
        x = x_start + col * (month_width + padding)
        y = y_start - (row + 1) * month_height - row * padding
        draw_month(c, year, month, x, y, month_width, month_height, marked_days, fiestas_locales, otros_motivos)

    # Añadir leyenda en cuadrícula
    legend_x = margin
    legend_y = margin 
    square_size = 8

    c.setFont("Helvetica-Bold", 8)

    c.setFillColor(colors.lightgreen)
    c.rect(legend_x, legend_y + 99, square_size, square_size, fill=1)
    c.setFillColor(colors.black)
    c.drawString(legend_x + 15, legend_y + 100, "Vacaciones seleccionadas")

    legend_y -= 15

    c.setFillColor(colors.red)
    c.rect(legend_x, legend_y + 99, square_size, square_size, fill=1)
    c.setFillColor(colors.black)
    c.drawString(legend_x + 15, legend_y + 100, "Feriados")

    legend_y -= 15

    c.setFillColor(colors.green)
    c.rect(legend_x, legend_y + 99, square_size, square_size, fill=1)
    c.setFillColor(colors.black)
    c.drawString(legend_x + 15, legend_y + 100, "Libres internos")  

    legend_y -= 15

    c.setFillColor(colors.orange)
    c.rect(legend_x, legend_y + 99, square_size, square_size, fill=1)
    c.setFillColor(colors.black)
    c.drawString(legend_x + 15, legend_y + 100, "Fiestas Locales")

    legend_y -= 15

    c.setFillColor(colors.blue)
    c.rect(legend_x, legend_y + 99, square_size, square_size, fill=1)
    c.setFillColor(colors.black)
    c.drawString(legend_x + 15, legend_y + 100, "Otros Motivos")

    c.setFontSize(7)
    c.setFillColor(colors.black)
    c.drawString(legend_x + 250, legend_y + 80, "APROBADO POR EL RESPONSABLE") 

    c.setFillColor(colors.black)
    c.drawString(legend_x + 250, legend_y + 60, "NOMBRE Y FIRMA") 

    c.setFont("Helvetica-Bold", 10)
    text_width = c.stringWidth("Vacaciones", "Helvetica", 10)
    c.drawString(width - 317, height - 20 , "2024")

    c.save()

def read_marked_days_from_csv(csv_file):
    marked_days = []
    fiestas_locales = []
    otros_motivos = []
    with open(csv_file, newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            day, month, category = int(row[0]), int(row[1]), row[2]
            if category == "Vacaciones":
                marked_days.append((day, month))
            elif category == "Fiestas Locales":
                fiestas_locales.append((day, month))
            elif category == "Otros Motivos":
                otros_motivos.append((day, month))
    return marked_days, fiestas_locales, otros_motivos

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
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Calendario de Vacaciones")
        self.setGeometry(100, 100, 800, 600)

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

        self.company_label = QLabel("Empresa:", self)
        self.company_label.move(500, 140)
        self.company_input = QLineEdit(self)
        self.company_input.move(570, 140)

        self.department_label = QLabel("Departamento:", self)
        self.department_label.move(500, 180)
        self.department_input = QLineEdit(self)
        self.department_input.move(570, 180)

        self.calendar.clicked.connect(self.mark_date)

        self.generate_button = QPushButton("Generar Calendario", self)
        self.generate_button.move(500, 220)
        self.generate_button.clicked.connect(self.generate_calendar)

        self.email_label = QLabel("Email:", self)
        self.email_label.move(500, 260)
        self.email_input = QLineEdit(self)
        self.email_input.move(570, 260)

        self.send_button = QPushButton("Enviar Email", self)
        self.send_button.move(500, 300)
        self.send_button.clicked.connect(self.send_calendar_email)

        self.marked_days = []
        self.fiestas_locales = []
        self.otros_motivos = []

    def mark_date(self, date):
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
                self.mark_date_in_calendar(date, QColor("orange"))
            else:
                dias_fiestas_locales.remove(date)
                self.mark_date_in_calendar(date, QColor("white"))
        elif category == "Otros Motivos":
            if date not in dias_otros_motivos:
                dias_otros_motivos.append(date)
                self.mark_date_in_calendar(date, QColor("blue"))
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

        if not nombre or not empresa or not departamento:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos.")
            return

        marked_days = [(date.day(), date.month()) for date in dias_vacaciones]
        fiestas_locales = [(date.day(), date.month()) for date in dias_fiestas_locales]
        otros_motivos = [(date.day(), date.month()) for date in dias_otros_motivos]

        create_calendar(2024, "calendario_vacaciones.pdf", marked_days, fiestas_locales, otros_motivos, nombre, empresa, departamento)

        QMessageBox.information(self, "Éxito", "Calendario generado exitosamente.")

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
    window = CalendarWindow()
    window.show()
    sys.exit(app.exec_())