import sys
import os
import calendar
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QCalendarWidget, QPushButton, QLineEdit, QMessageBox
from PyQt5.QtGui import QFont, QTextCharFormat, QColor
from PyQt5.QtCore import Qt, QDate
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

feriados = [QDate(2024, 12, 25), QDate(2024, 10, 12), QDate(2024, 11, 1), QDate(2024, 12, 6), QDate(2024, 8, 15),
            QDate(2024, 7, 25)]
vacaciones = [QDate(2024, 8, 12), QDate(2024, 8, 13), QDate(2024, 8, 14), QDate(2024, 8, 16), QDate(2024, 8, 19),
              QDate(2024, 8, 20), QDate(2024, 8, 21), QDate(2024, 8, 22), QDate(2024, 8, 23)]
libre_interno = [QDate(2024, 7, 26), QDate(2024, 12, 24), QDate(2024, 12, 31)]

dias_seleccionado = []

def draw_month(canvas, year, month, start_x, start_y, month_width, month_height, marked_days):
    cal = calendar.Calendar(firstweekday=0)
    month_names_es = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    month_name = month_names_es[month - 1]
    month_days = list(cal.itermonthdays(year, month))
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
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ])

    for week in range(len(data)):
        for day in range(len(data[week])):
            day_str = data[week][day]
            if day_str != '' and (int(day_str), month) in marked_days:
                style.add('BACKGROUND', (day, week), (day, week), colors.lightgreen)

    table.setStyle(style)

    table.wrapOn(canvas, month_width, month_height)
    table.drawOn(canvas, start_x, start_y)

    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(start_x + month_width / 2 - inch, start_y + month_height + 0.3 * inch, f"{month_name} {year}")

    canvas.setFont("Helvetica", 10)
    day_width = month_width / 7
    for i, day in enumerate(days_es):
        canvas.drawString(start_x + i * day_width + 0 * inch, start_y + month_height + 0.1 * inch, day)

def create_calendar(year, filename, marked_days, nombre, empresa, departamento):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    margin = 0.5 * inch
    padding = 0.2 * inch

    # Añadir la información del nombre, empresa y departamento en la parte superior del PDF
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, height - margin, f"Nombre: {nombre}")
    c.drawString(margin, height - margin - 14, f"Empresa: {empresa}")
    c.drawString(margin, height - margin - 28, f"Departamento: {departamento}")

    months_per_row = 4
    months_per_col = 3

    month_width = (width - 2 * margin - (months_per_row - 1) * padding) / months_per_row
    month_height = (height - 2 * margin - (months_per_col - 1) * padding) / months_per_col

    x_start = margin
    y_start = height - margin - 50  # Ajustar para dejar espacio para la información del usuario

    for month in range(1, 13):
        row = (month - 1) // months_per_row
        col = (month - 1) % months_per_row
        x = x_start + col * (month_width + padding)
        y = y_start - (row + 1) * month_height - row * padding
        draw_month(c, year, month, x, y, month_width, month_height, marked_days)

    c.save()

def read_marked_days_from_csv(csv_file):
    marked_days = []
    with open(csv_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            fechas = row[3].split(', ')
            for fecha in fechas:
                day, month, year = map(int, fecha.split('/'))
                marked_days.append((day, month))
    return marked_days

class Ventana(QMainWindow):
    def __init__(self, nombre, empresa, departamento, dias_vacaciones):
        super().__init__()
        self.nombre = nombre
        self.empresa = empresa
        self.departamento = departamento
        self.dias_vacaciones = dias_vacaciones
        self.dias_seleccionado = []
        self.personalizarVentana()
        self.personalizarComponentes()

    def personalizarVentana(self):
        self.setWindowTitle("VENTANA PYQT5")
        self.setStyleSheet("background-color: lightgray;")
        self.setFixedSize(480, 630)

        self.pnlPrincipal = QWidget()
        self.setCentralWidget(self.pnlPrincipal)

    def personalizarComponentes(self):
        self.lblNombre = QLabel("NOMBRE:", self.pnlPrincipal)
        self.lblNombre.setFont(QFont("Courier New", 10))
        self.lblNombre.setStyleSheet("color: #000000;")
        self.lblNombre.setAlignment(Qt.AlignLeft)
        self.lblNombre.setGeometry(30, 20, 100, 20)

        self.lblEmpresa = QLabel("EMPRESA:", self.pnlPrincipal)
        self.lblEmpresa.setFont(QFont("Courier New", 10))
        self.lblEmpresa.setStyleSheet("color: #000000;")
        self.lblEmpresa.setAlignment(Qt.AlignLeft)
        self.lblEmpresa.setGeometry(30, 50, 100, 20)

        self.txtNombre = QLineEdit(self.pnlPrincipal)
        self.txtNombre.setGeometry(100, 20, 100, 20)
        self.txtNombre.setFont(QFont("Courier New", 9))
        self.txtNombre.setAlignment(Qt.AlignCenter)
        self.txtNombre.setStyleSheet("color: black;")
        self.txtNombre.setReadOnly(True)
        self.txtNombre.setText(self.nombre)

        self.txtEmpresa = QLineEdit(self.pnlPrincipal)
        self.txtEmpresa.setGeometry(100, 50, 100, 20)
        self.txtEmpresa.setFont(QFont("Courier New", 9))
        self.txtEmpresa.setAlignment(Qt.AlignCenter)
        self.txtEmpresa.setStyleSheet("color: black;")
        self.txtEmpresa.setReadOnly(True)
        self.txtEmpresa.setText(self.empresa)

        self.lblDepartamento = QLabel("DEPARTAMENTO:", self.pnlPrincipal)
        self.lblDepartamento.setFont(QFont("Courier New", 10))
        self.lblDepartamento.setStyleSheet("color: #000000;")
        self.lblDepartamento.setAlignment(Qt.AlignLeft)
        self.lblDepartamento.setGeometry(20, 80, 100, 20)

        self.txtDepartamento = QLineEdit(self.pnlPrincipal)
        self.txtDepartamento.setGeometry(130, 80, 100, 20)
        self.txtDepartamento.setFont(QFont("Courier New", 9))
        self.txtDepartamento.setAlignment(Qt.AlignCenter)
        self.txtDepartamento.setStyleSheet("color: black;")
        self.txtDepartamento.setReadOnly(True)
        self.txtDepartamento.setText(self.departamento)

        self.lblVacaciones = QLabel("DIAS DE VACACIONES:", self.pnlPrincipal)
        self.lblVacaciones.setFont(QFont("Courier New", 10))
        self.lblVacaciones.setStyleSheet("color: black;")
        self.lblVacaciones.setAlignment(Qt.AlignCenter)
        self.lblVacaciones.setGeometry(300, 20, 150, 20)

        self.txtVacaciones = QLineEdit(self.pnlPrincipal)
        self.txtVacaciones.setGeometry(390, 20, 80, 20)
        self.txtVacaciones.setFont(QFont("Courier New", 9))
        self.txtVacaciones.setAlignment(Qt.AlignCenter)
        self.txtVacaciones.setStyleSheet("color: black;")
        self.txtVacaciones.setReadOnly(True)
        self.txtVacaciones.setText(str(self.dias_vacaciones))

        self.lblFecha = QLabel("SELECCIONAR DIAS", self.pnlPrincipal)
        self.lblFecha.setFont(QFont("Courier New", 12))
        self.lblFecha.setStyleSheet("color: black;")
        self.lblFecha.setAlignment(Qt.AlignCenter)
        self.lblFecha.setGeometry(0, 170, 490, 20)

        self.btoSeleccion = QPushButton("ACEPTAR", self)
        self.btoSeleccion.setGeometry(10, 500, 460, 20)
        self.btoSeleccion.setFont(QFont("Courier New", 0, 8))
        self.btoSeleccion.setStyleSheet("background-color: black; color: white;")
        self.btoSeleccion.clicked.connect(self.comprobar)

        self.btoGenerarPDF = QPushButton("GENERAR PDF", self)
        self.btoGenerarPDF.setGeometry(10, 530, 460, 20)
        self.btoGenerarPDF.setFont(QFont("Courier New", 0, 8))
        self.btoGenerarPDF.setStyleSheet("background-color: black; color: white;")
        self.btoGenerarPDF.clicked.connect(self.generar_pdf)

        self.calendario = QCalendarWidget(self.pnlPrincipal)
        self.calendario.setGridVisible(True)
        self.calendario.setGeometry(10, 200, 460, 250)
        self.calendario.clicked[QDate].connect(self.guardarFechaSeleccionada)

        min_date = QDate(2024, 1, 1)
        max_date = QDate(2024, 12, 31)
        self.calendario.setDateRange(min_date, max_date)
        self.calendario.setFirstDayOfWeek(Qt.Sunday)

        self.calendario.setStyleSheet("color: black; background-color: white")
        self.calendario.setNavigationBarVisible(True)

        self.marcarFeriados()
        self.marcarVacaciones()
        self.marcarInterno()

    def guardarFechaSeleccionada(self, fecha):
        if fecha not in dias_seleccionado:
            if len(dias_seleccionado) < self.dias_vacaciones:
                fecha_str = "{:02d}/{:02d}/{:04d}".format(fecha.day(), fecha.month(), fecha.year())
                dias_seleccionado.append(fecha)
                self.marcarDiasSeleccionados()
                print(dias_seleccionado)
            else:
                QMessageBox.warning(self, "Límite Excedido", "No puedes seleccionar más días de vacaciones de los disponibles.")
        else:
            dias_seleccionado.remove(fecha)
            self.desmarcarDia(fecha)
            print(f"La fecha {fecha.toString('dd/MM/yyyy')} se ha deseleccionado.")

    def marcarDiasSeleccionados(self):
        formato = QTextCharFormat()
        formato.setBackground(QColor("lightGreen"))
        for fecha in dias_seleccionado:
            self.calendario.setDateTextFormat(fecha, formato)

    def desmarcarDia(self, fecha):
        formato = QTextCharFormat()
        self.calendario.setDateTextFormat(fecha, formato)

    def comprobar(self, cantidad_dias):
        vacaciones_dias = int(self.txtVacaciones.text())
        cantidad_dias = len(dias_seleccionado)
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

    def marcarVacaciones(self):
        formato = QTextCharFormat()
        formato.setBackground(QColor("yellow"))
        for fecha in vacaciones:
            self.calendario.setDateTextFormat(fecha, formato)

    def marcarInterno(self):
        formato = QTextCharFormat()
        formato.setBackground(QColor("green"))
        for fecha in libre_interno:
            self.calendario.setDateTextFormat(fecha, formato)

    def guardar_en_csv(self):
        with open('vacaciones.csv', mode='w', newline='') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(['Nombre', 'Empresa', 'Departamento', 'Fechas de Vacaciones'])
            fechas_str = [fecha.toString('dd/MM/yyyy') for fecha in dias_seleccionado]
            escritor.writerow([self.nombre, self.empresa, self.departamento, ', '.join(fechas_str)])
        print("Datos guardados en vacaciones.csv")

    def limpiarSeleccion(self):
        global dias_seleccionado
        dias_seleccionado = []
        formato = QTextCharFormat()
        for i in range(1, self.calendario.maximumDate().daysTo(self.calendario.minimumDate()) + 1):
            self.calendario.setDateTextFormat(self.calendario.minimumDate().addDays(i), formato)

    def generar_pdf(self):
        marked_days = read_marked_days_from_csv('vacaciones.csv')
        create_calendar(2024, 'calendario_vacaciones.pdf', marked_days, self.nombre, self.empresa, self.departamento)
        QMessageBox.information(self, "PDF Generado", "El calendario de vacaciones se ha generado como 'calendario_vacaciones.pdf'.")

    def show(self):
        self.limpiarSeleccion()
        self.guardar_en_csv()
        super().show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Ventana("Juan Perez", "Empresa XYZ", "Departamento ABC", 5)
    ventana.show()
    sys.exit(app.exec_())
