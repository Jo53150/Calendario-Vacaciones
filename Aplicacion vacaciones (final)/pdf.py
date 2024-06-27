from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import calendar

def draw_month(canvas, year, month, start_x, start_y, month_width, month_height, marked_days, fiestas_locales, otros_motivos):
    cal = calendar.Calendar(firstweekday=0)
    month_names_es = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 
                      'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    month_name = month_names_es[month - 1]
    month_days = list(cal.itermonthdays(year, month))
    feriados = [(25, 12), (12, 10), (1, 11), (6, 12), (15, 8), (25, 7), (1, 1), (6,1), (28, 3), (29, 3), (1, 5), (2, 5)]
    libre_interno = [(26, 7), (24, 12), (31, 12), (3, 5)]

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
                style.add('BACKGROUND', (day, week), (day, week), colors.royalblue)
            if day_str != '' and (int(day_str), month) in otros_motivos:
                style.add('BACKGROUND', (day, week), (day, week), colors.lightsalmon)

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

    c.setFont("Helvetica-Bold", 9)
    c.drawString(width - 550,height - 40, f"Nombre: {nombre}")
    c.drawString(width - 550,height - 50, f"Empresa: {empresa}")
    c.drawString(width - 550,height - 60, f"Departamento: {departamento}")

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
    c.rect(legend_x, legend_y + 209, square_size, square_size, fill=1)
    c.setFillColor(colors.black)
    c.drawString(legend_x + 15, legend_y + 210, "Vacaciones seleccionadas")

    legend_y -= 15

    c.setFillColor(colors.red)
    c.rect(legend_x, legend_y + 209, square_size, square_size, fill=1)
    c.setFillColor(colors.black)
    c.drawString(legend_x + 15, legend_y + 210, "Feriados")

    legend_y -= 15

    c.setFillColor(colors.green)
    c.rect(legend_x, legend_y + 209, square_size, square_size, fill=1)
    c.setFillColor(colors.black)
    c.drawString(legend_x + 15, legend_y + 210, "Libres internos")  

    legend_y -= 15

    c.setFillColor(colors.royalblue)
    c.rect(legend_x, legend_y + 209, square_size, square_size, fill=1)
    c.setFillColor(colors.black)
    c.drawString(legend_x + 15, legend_y + 210, "Fiestas Locales")

    legend_y -= 15

    c.setFillColor(colors.lightsalmon)
    c.rect(legend_x, legend_y + 209, square_size, square_size, fill=1)
    c.setFillColor(colors.black)
    c.drawString(legend_x + 15, legend_y + 210, "Otros Motivos")

    c.setFontSize(8)
    c.setFillColor(colors.black)
    c.drawString(legend_x + 250, legend_y + 160, "APROBADO POR EL RESPONSABLE") 

    c.setFillColor(colors.black)
    c.drawString(legend_x + 250, legend_y + 140, "NOMBRE Y FIRMA") 

    c.setFont("Helvetica-Bold", 10)
    c.drawString(width - 317, height - 20 , "2024")

    c.setFont("Helvetica-Bold", 8)
    c.drawString(width - 120, height - 40 , "Vacaciones")
    rect_x = width - 55
    rect_y = height - 41
    rect_size = 7
    c.rect(rect_x, rect_y, rect_size, rect_size)

    if marked_days:
        line_x1 = rect_x
        line_y1 = rect_y
        line_x2 = rect_x + rect_size
        line_y2 = rect_y + rect_size
        c.line(line_x1, line_y1, line_x2, line_y2)  

    c.setFont("Helvetica-Bold", 8)
    c.drawString(width - 120, height - 50 , "Fiestas Locales")
    rect_x = width  - 55
    rect_y = height - 51
    rect_size = 7
    c.rect(rect_x, rect_y, rect_size, rect_size)

    if fiestas_locales:
        line_x1 = rect_x
        line_y1 = rect_y
        line_x2 = rect_x + rect_size
        line_y2 = rect_y + rect_size
        c.line(line_x1, line_y1, line_x2, line_y2)  
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(width - 120, height - 60 , "Otros Motivos")
    rect_x = width  - 55
    rect_y = height - 61
    rect_size = 7
    c.rect(rect_x, rect_y, rect_size, rect_size)

    if otros_motivos:
        line_x1 = rect_x
        line_y1 = rect_y
        line_x2 = rect_x + rect_size
        line_y2 = rect_y + rect_size
        c.line(line_x1, line_y1, line_x2, line_y2)  

    c.save()