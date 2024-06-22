from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import calendar
import csv

def draw_month(canvas, year, month, start_x, start_y, month_width, month_height, marked_days):
    cal = calendar.Calendar(firstweekday=0)
    month_names_es = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    month_name = month_names_es[month - 1]
    month_days = list(cal.itermonthdays(year, month))
    feriados = [(25,12),(12,10),(1,11),(6,12),(15,8),(25,7),(1,1),(6,1),(28,3),(29,3),(1,5),(2,5)]
    vacaciones = [(12,8),(13,8),(14,8),(16,8),(19,8),(20,8),(21,8),(22,8),(23,8)]
    libre_interno = [(26,7),(24,12),(31,12),(3,5)]
    days_in_month = len(month_days)

    # Datos para la tabla: 7 columnas para los días de la semana
    data = [['' for _ in range(7)] for _ in range(6)]  # 6 filas para un máximo de 6 semanas en un mes
    days_es = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

    # Llenar la tabla con los días del mes
    week = 0
    for i, day in enumerate(month_days):
        if day != 0:
            day_str = str(day)
            data[week][i % 7] = day_str
        if (i + 1) % 7 == 0:
            week += 1

    # Crear la tabla
    table = Table(data, colWidths=[month_width / 7] * 7, rowHeights=[month_height / 6] * 6)

    # Estilo de la tabla
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Añadir líneas de cuadrícula
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alinear al centro todas las celdas
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alinear verticalmente al medio
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Fuente
        ('FONTSIZE', (0, 0), (-1, -1), 9),  # Tamaño de la fuente
    ])

    # Aplicar color a los días marcados
    for week in range(len(data)):
        for day in range(len(data[week])):
            day_str = data[week][day]
            if day_str != '' and (int(day_str), month) in marked_days:
                style.add('BACKGROUND', (day, week), (day, week), colors.lightgreen)

    for week in range(len(data)):
        for day in range(len(data[week])):
            day_str = data[week][day]
            if day_str != '' and (int(day_str), month) in feriados:
                style.add('BACKGROUND', (day, week), (day, week), colors.lightsalmon)  
    
    for week in range(len(data)):
        for day in range(len(data[week])):
            day_str = data[week][day]
            if day_str != '' and (int(day_str), month) in vacaciones:
                style.add('BACKGROUND', (day, week), (day, week), colors.yellow)  

    for week in range(len(data)):
        for day in range(len(data[week])):
            day_str = data[week][day]
            if day_str != '' and (int(day_str), month) in libre_interno:
                style.add('BACKGROUND', (day, week), (day, week), colors.green)                                   
                
    table.setStyle(style)

    # Posicionar la tabla en el lienzo (canvas)
    table.wrapOn(canvas, month_width, month_height)
    table.drawOn(canvas, start_x, start_y)

    # Dibujar el nombre del mes
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(start_x + month_width / 2 - inch, start_y + month_height + 0.3 * inch, f"{month_name} {year}")

    # Dibujar los días de la semana
    canvas.setFont("Helvetica", 8)
    day_width = month_width / 7
    for i, day in enumerate(days_es):
        canvas.drawString(start_x + i * day_width + 0 * inch, start_y + month_height + 0.1 * inch, day)

def create_calendar(year, filename, marked_days):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    margin = 0.5 * inch
    padding = 0.5 * inch

    # Número de meses por fila y columna
    months_per_row = 4
    months_per_col = 3
    month_width = (width - 2 * margin - (months_per_row - 1) * padding) / months_per_row
    month_height = (height - 2 * margin - (months_per_col - 1) * padding) / months_per_col

    x_start = margin
    y_start = height - margin

    for month in range(1, 13):
        row = (month - 1) // months_per_row
        col = (month - 1) % months_per_row
        x = x_start + col * (month_width + padding)
        y = y_start - (row + 1) * month_height - row * padding  # Ajustar la posición y
        draw_month(c, year, month, x, y, month_width, month_height, marked_days)

    c.save()

def read_marked_days_from_csv(csv_file):
    marked_days = []
    with open(csv_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Saltar encabezado
        for row in reader:
            fechas = row[3].split(', ')
            for fecha in fechas:
                day, month, year = map(int, fecha.split('/'))
                marked_days.append((day, month))
    print(marked_days)
    return marked_days

if __name__ == "__main__":
    year = 2024
    filename = "calendario_2024.pdf"
    csv_file = "vacaciones.csv"

    # Leer los días marcados desde el archivo CSV
    marked_days = read_marked_days_from_csv(csv_file)

    calendar.setfirstweekday(calendar.MONDAY)
    create_calendar(year, filename, marked_days)
    print(f"Calendario para el año {year} ha sido guardado en {filename}")