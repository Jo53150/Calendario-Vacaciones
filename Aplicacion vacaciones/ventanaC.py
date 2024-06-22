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

feriados = [QDate(2024, 12, 25), QDate(2024, 10, 12), QDate(2024, 11, 1), QDate(2024, 12, 6), QDate(2024, 8, 15),
            QDate(2024, 7, 25)]

libre_interno = [QDate(2024, 7, 26), QDate(2024, 12, 24), QDate(2024, 12, 31)]

dias_libres = []

def draw_month(canvas, year, month, start_x, start_y, month_width, month_height, marked_days):
    cal = calendar.Calendar(firstweekday=0)
    month_names_es = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    month_name = month_names_es[month - 1]
    month_days = list(cal.itermonthdays(year, month))
    feriados = [(25, 12), (12, 10), (1, 11), (6, 12), (15, 8), (25, 7), (1, 1), (6, 1), (28, 3), (29, 3), (1, 5), (2, 5)]
    libre_interno = [(26, 7), (24, 12), (31, 12), (3, 5)]
    days_in_month = len(month_days)

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

    for week in range(len(data)):
        for day in range(len(data[week])):
            day_str = data[week][day]
            if day_str != '' and (int(day_str), month) in feriados:
                style.add('BACKGROUND', (day, week), (day, week), colors.red)

    for week in range(len(data)):
        for day in range(len(data[week])):
            day_str = data[week][day]
            if day_str != '' and (int(day_str), month) in libre_interno:
                style.add('BACKGROUND', (day, week), (day, week), colors.green)

    table.setStyle(style)

    table.wrapOn(canvas, month_width, month_height)
    table.drawOn(canvas, start_x, start_y)

    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(start_x + month_width / 2 - inch, start_y + month_height + 0.3 * inch, f"{month_name}")

    canvas.setFont("Helvetica", 8)
    day_width = month_width / 7
    for i, day in enumerate(days_es):
        canvas.drawString(start_x + i * day_width + 0 * inch, start_y + month_height + 0.1 * inch, day)

def create_calendar(year, filename, marked_days, nombre, empresa, departamento):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    margin = 50
    padding = 50

    c.setFont("Helvetica-Bold", 8)
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
        draw_month(c, year, month, x, y, month_width, month_height, marked_days)

    # Añadir leyenda en cuadrícula
    legend_x = margin
    legend_y = margin 
    square_size = 8

    c.setFont("Helvetica-Bold", 8)

    c.setFillColor(colors.lightgreen)
    c.rect(legend_x, legend_y + 209, square_size, square_size, fill=1)
    c.setFillColor(colors.black)
    c.drawString(legend_x + 15, legend_y + 210, "Vacaciones seleccionadas")

    legend_y -= 15

    c.setFillColor(colors.red)
    c.rect(legend_x, legend_y + 199, square_size, square_size, fill=1)
    c.setFillColor(colors.black)
    c.drawString(legend_x + 15, legend_y + 200, "Feriados")

    legend_y -= 15

    c.setFillColor(colors.green)
    c.rect(legend_x, legend_y + 189, square_size, square_size, fill=1)
    c.setFillColor(colors.black)
    c.drawString(legend_x + 15, legend_y + 190, "Libres internos")  

    c.setFontSize(7)
    c.setFillColor(colors.black)
    c.drawString(legend_x + 250, legend_y + 80, "APROBADO POR EL RESPONSABLE") 

    c.setFillColor(colors.black)
    c.drawString(legend_x + 250, legend_y + 60, "NOMBRE Y FIRMA") 

    c.setFont("Helvetica-Bold", 10)
    text_width = c.stringWidth("Vacaciones", "Helvetica", 10)
    c.drawString(width - 317, height - 20 , "2024")

    c.setFont("Helvetica-Bold", 9)
    text_width = c.stringWidth("Vacaciones", "Helvetica", 10)
    c.drawString(width - margin - text_width - 25, height - 30 , "Vacaciones")
    
    # Coordenadas del rectángulo blanco
    rect_x = width - margin - 20
    rect_y = height - 32
    rect_size = 10
    
    c.rect(rect_x, rect_y, rect_size, rect_size)  # Cuadrado blanco
    
    # Coordenadas para la línea diagonal dentro del rectángulo blanco
    line_x1 = rect_x
    line_y1 = rect_y
    line_x2 = rect_x + rect_size
    line_y2 = rect_y + rect_size
    
    c.line(line_x1, line_y1, line_x2, line_y2)

    c.setFont("Helvetica-Bold", 9)
    text_width = c.stringWidth("Vacaciones", "Helvetica", 10)
    c.drawString(width - margin - text_width - 42, height - 41, "Fiestas Locales")

    # Coordenadas del rectángulo blanco
    rect_x = width - margin - 20
    rect_y = height - 42
    rect_size = 10
    
    c.rect(rect_x, rect_y, rect_size, rect_size)  # Cuadrado blanco

    c.setFont("Helvetica-Bold", 9)
    text_width = c.stringWidth("Vacaciones", "Helvetica", 10)
    c.drawString(width - margin - text_width - 35, height - 51, "Otros Motivos")

    rect_x = width - margin - 20
    rect_y = height - 52
    rect_size = 10
    
    c.rect(rect_x, rect_y, rect_size, rect_size)  # Cuadrado blanco
    

    c.save()


def read_marked_days_from_csv(csv_file):
    marked_days = []
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if row: # Verificar si la fila no está vacía
                    try:
                        fechas = row[3].split(', ')
                        for fecha in fechas:
                            day, month, year = map(int, fecha.split('/'))
                            marked_days.append((day, month))
                    except ValueError:
                        print(f"Valor inválido encontrado en el archivo CSV: {row[3]}")        
    except FileNotFoundError:
        print(f"El archivo {csv_file} no se encontró.")
    except Exception as e:
        print(f"Se produjo un error al leer el archivo CSV: {e}")                
    print(marked_days)            
    return marked_days



class Ventana(QMainWindow):
    def __init__(self, nombre, empresa, departamento, dias_vacaciones):
        super().__init__()
        self.nombre = nombre
        self.empresa = empresa
        self.departamento = departamento
        self.dias_vacaciones = dias_vacaciones
        self.dias_libres = []
        self.personalizarVentana()
        self.personalizarComponentes()

    def personalizarVentana(self):
        self.setWindowTitle("SELECCION DIAS")
        self.setStyleSheet("background-color: lightgray;")
        self.setFixedSize(480, 590)

        self.pnlPrincipal = QWidget()
        self.setCentralWidget(self.pnlPrincipal)

    def personalizarComponentes(self):
        self.lblNombre = QLabel("NOMBRE:", self.pnlPrincipal)
        self.lblNombre.setFont(QFont("Helvetica", 10))
        self.lblNombre.setStyleSheet("color: #000000;")
        self.lblNombre.setAlignment(Qt.AlignLeft)
        self.lblNombre.setGeometry(30, 20, 100, 20)

        self.lblEmpresa = QLabel("EMPRESA:", self.pnlPrincipal)
        self.lblEmpresa.setFont(QFont("Helvetica", 10))
        self.lblEmpresa.setStyleSheet("color: #000000;")
        self.lblEmpresa.setAlignment(Qt.AlignLeft)
        self.lblEmpresa.setGeometry(30, 50, 100, 20)

        self.txtNombre = QLineEdit(self.pnlPrincipal)
        self.txtNombre.setGeometry(100, 20, 100, 20)
        self.txtNombre.setFont(QFont("Helvetica", 9))
        self.txtNombre.setAlignment(Qt.AlignCenter)
        self.txtNombre.setStyleSheet("color: black;")
        self.txtNombre.setReadOnly(True)
        self.txtNombre.setText(self.nombre)

        self.txtEmpresa = QLineEdit(self.pnlPrincipal)
        self.txtEmpresa.setGeometry(100, 50, 100, 20)
        self.txtEmpresa.setFont(QFont("Helvetica", 9))
        self.txtEmpresa.setAlignment(Qt.AlignCenter)
        self.txtEmpresa.setStyleSheet("color: black;")
        self.txtEmpresa.setReadOnly(True)
        self.txtEmpresa.setText(self.empresa)

        self.lblDepartamento = QLabel("DEPARTAMENTO:", self.pnlPrincipal)
        self.lblDepartamento.setFont(QFont("Helvetica", 10))
        self.lblDepartamento.setStyleSheet("color: #000000;")
        self.lblDepartamento.setAlignment(Qt.AlignLeft)
        self.lblDepartamento.setGeometry(20, 80, 100, 20)

        self.txtDepartamento = QLineEdit(self.pnlPrincipal)
        self.txtDepartamento.setGeometry(130, 80, 100, 20)
        self.txtDepartamento.setFont(QFont("Helvetica", 9))
        self.txtDepartamento.setAlignment(Qt.AlignCenter)
        self.txtDepartamento.setStyleSheet("color: black;")
        self.txtDepartamento.setReadOnly(True)
        self.txtDepartamento.setText(self.departamento)

        self.lblVacaciones = QLabel("VACACIONES:", self.pnlPrincipal)
        self.lblVacaciones.setFont(QFont("Helvetica", 10))
        self.lblVacaciones.setStyleSheet("color: #000000;")
        self.lblVacaciones.setAlignment(Qt.AlignLeft)
        self.lblVacaciones.setGeometry(300, 20, 150, 20)

        self.txtVacaciones = QLineEdit(self.pnlPrincipal)
        self.txtVacaciones.setGeometry(390, 20, 80, 20)
        self.txtVacaciones.setFont(QFont("Helvetica", 9))
        self.txtVacaciones.setAlignment(Qt.AlignCenter)
        self.txtVacaciones.setStyleSheet("color: black;")
        self.txtVacaciones.setReadOnly(True)
        self.txtVacaciones.setText(str(self.dias_vacaciones))

        self.txtEmail = QLineEdit(self.pnlPrincipal)
        self.txtEmail.setPlaceholderText("Correo del destinatario")
        self.txtEmail.setGeometry(20, 110, 300, 30)

        self.comboBox = QComboBox(self)
        self.comboBox.addItems(["Vacaciones", "Fiestas locales", "Otros Motivos"])
        self.comboBox.setGeometry(10, 380, 460, 30)
        self.comboBox.setFont(QFont("Helvetica", 10, 20))
        self.comboBox.setStyleSheet("background-color: LightSteelBlue; color: black; margin: round")

        self.btoSeleccion = QPushButton("ACEPTAR", self)
        self.btoSeleccion.setGeometry(10, 420, 460, 20)
        self.btoSeleccion.setFont(QFont("Helvetica", 10, 20))
        self.btoSeleccion.setStyleSheet("background-color: LightSteelBlue; color: black; margin: round")
        self.btoSeleccion.clicked.connect(self.seleccion)

        self.btoGenerarPDF = QPushButton("GENERAR PDF", self)
        self.btoGenerarPDF.setGeometry(10, 450, 460, 20)
        self.btoGenerarPDF.setFont(QFont("Helvetica", 10, 20))
        self.btoGenerarPDF.setStyleSheet("background-color: LightSteelBlue; color: black; margin: round")
        self.btoGenerarPDF.clicked.connect(self.generar_pdf)

        self.btoEnviarEmail = QPushButton("ENVIAR EMAIL", self)
        self.btoEnviarEmail.setGeometry(10, 480, 460, 20)
        self.btoEnviarEmail.setFont(QFont("Helvetica", 10, 20))
        self.btoEnviarEmail.setStyleSheet("background-color: LightSteelBlue; color: black; margin: round")
        self.btoEnviarEmail.clicked.connect(self.enviar_email)

        self.btoSalir = QPushButton("SALIR", self)
        self.btoSalir.setGeometry(10, 510, 460, 20)
        self.btoSalir.setFont(QFont("Helvetica", 10, 20))
        self.btoSalir.setStyleSheet("background-color: LightSteelBlue; color: black; margin: round")
        self.btoSalir.clicked.connect(self.salir)

        self.calendario = QCalendarWidget(self.pnlPrincipal)
        self.calendario.setGridVisible(True)
        self.calendario.setGeometry(10, 150, 460, 250)
        self.calendario.clicked[QDate].connect(self.guardarFechaSeleccionada)

        min_date = QDate(2024, 1, 1)
        max_date = QDate(2024, 12, 31)
        self.calendario.setDateRange(min_date, max_date)
        self.calendario.setFirstDayOfWeek(Qt.Sunday)

        self.calendario.setStyleSheet("color: black; background-color: white")
        self.calendario.setNavigationBarVisible(True)

        self.marcarFeriados()

        self.marcarInterno()

    def guardarFechaSeleccionada(self, fecha):
        if fecha not in dias_libres:
            if len(dias_libres) < self.dias_vacaciones:
                fecha_str = "{:02d}/{:02d}/{:04d}".format(fecha.day(), fecha.month(), fecha.year())
                dias_libres.append(fecha)
                self.marcarDiasSeleccionados()
                print(dias_libres)
            else:
                QMessageBox.warning(self, "Límite Excedido", "No puedes seleccionar más días de vacaciones de los disponibles.")
        else:
            dias_libres.remove(fecha)
            self.desmarcarDia(fecha)
            print(f"La fecha {fecha.toString('dd/MM/yyyy')} se ha deseleccionado.")

    def marcarDiasSeleccionados(self):
        formato = QTextCharFormat()
        formato.setBackground(QColor("lightGreen"))
        for fecha in dias_libres:
            self.calendario.setDateTextFormat(fecha, formato)

    def desmarcarDia(self, fecha):
        formato = QTextCharFormat()
        self.calendario.setDateTextFormat(fecha, formato)

    def seleccion(self, cantidad_dias):
        vacaciones_dias = int(self.txtVacaciones.text())
        cantidad_dias = len(dias_libres)
        print(f"Días seleccionados: {cantidad_dias}")
        self.ventanaDias(cantidad_dias)
        vacaciones_dias = vacaciones_dias - cantidad_dias
        self.txtVacaciones.setText(str(vacaciones_dias))
        self.guardar_en_csv()

    def ventanaDias(self, cantidad_dias):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Días seleccionados: {cantidad_dias}")
        msg.setWindowTitle("Info")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def marcarFeriados(self):
        formato = QTextCharFormat()
        formato.setBackground(QColor("darkRed"))
        for fecha in feriados:
            self.calendario.setDateTextFormat(fecha, formato)


    def marcarInterno(self):
        formato = QTextCharFormat()
        formato.setBackground(QColor("green"))
        for fecha in libre_interno:
            self.calendario.setDateTextFormat(fecha, formato)

    def guardar_en_csv(self):
        with open('vacaciones.csv', mode='w', newline='', encoding='utf-8') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(['Nombre', 'Empresa', 'Departamento', 'Fechas de Vacaciones'])
            fechas_str = [fecha.toString('dd/MM/yyyy') for fecha in dias_libres]
            escritor.writerow([self.nombre, self.empresa, self.departamento, ', '.join(fechas_str)])
        print("Datos guardados en vacaciones.csv")

    def limpiarSeleccion(self):
        global dias_libres
        dias_libres = []
        formato = QTextCharFormat()
        for i in range(1, self.calendario.maximumDate().daysTo(self.calendario.minimumDate()) + 1):
            self.calendario.setDateTextFormat(self.calendario.minimumDate().addDays(i), formato)

    def enviar_email(self):
        recipient_email = self.txtEmail.text()
        if recipient_email:
            pdf_path = 'calendario_vacaciones.pdf'
            email_user = 'joseantoniomg06@gmail.com'
            email_password = 'fmcs aice crhe lbzv'  # Usa la contraseña de aplicación aquí
            email_send = recipient_email

            subject = 'Calendario de Vacaciones'

            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = email_send
            msg['Subject'] = subject

            body = 'Adjunto se encuentra el calendario de vacaciones.'
            msg.attach(MIMEText(body, 'plain','utf-8'))

            with open(pdf_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(pdf_path)}')
                msg.attach(part)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(email_user, email_password)
                server.send_message(msg)

            QMessageBox.information(self, "Correo enviado", "El calendario de vacaciones se ha enviado por correo electrónico.")
        else:
            QMessageBox.warning(self, "Correo faltante", "Por favor, ingrese un correo electrónico para enviar el PDF.")


    def generar_pdf(self, recipient_email):
        csv_filename = 'vacaciones.csv'
        
        # Verificar si el archivo CSV existe
        if not os.path.isfile(csv_filename):
            QMessageBox.warning(self, "Sin Archivo", "El archivo CSV no existe")
            return
        
        # Leer los días marcados del archivo CSV
        marked_days = read_marked_days_from_csv(csv_filename)
        
        # Verificar si el archivo CSV está vacío o no contiene días marcados
        if not marked_days:
            QMessageBox.warning(self, "Archivo Vacío", "El archivo 'vacaciones.csv' está vacío o no contiene días marcados.")
            return
        
        # Crear el calendario
        create_calendar(2024, 'calendario_vacaciones.pdf', marked_days, self.nombre, self.empresa, self.departamento)
        
        # Mostrar mensaje de éxito
        QMessageBox.information(self, "PDF Generado", "El calendario de vacaciones se ha generado como 'calendario_vacaciones.pdf'.")

    def salir(self):
        ventana.close()

    def show(self):
        self.guardar_en_csv()
        self.limpiarSeleccion()
        super().show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Ventana("Prueba", "Prueba", "Prueba", 10)
    ventana.show()
    sys.exit(app.exec_())