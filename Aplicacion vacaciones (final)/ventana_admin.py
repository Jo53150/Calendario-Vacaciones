import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem, 
                             QVBoxLayout, QWidget, QPushButton, QMessageBox, QLineEdit, QLabel, QDialog)
from PyQt5.QtCore import Qt
import mysql.connector
from mysql.connector import Error

class VentanaAdmin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ventana de Administrador")
        self.setGeometry(100, 100, 800, 400)
        self.setFixedSize(800, 400)

        # Crear tabla para mostrar datos
        self.table = QTableWidget()
        self.table.setColumnCount(9)  # Número de columnas
        self.table.setHorizontalHeaderLabels(["ID", "USUARIO", "PASSWORD", "Nombre", "Empresa", 
                                              "Departamento", "Días Vacaciones", "Días Fiestas", "Días Otros Motivos"])

        # Botones para agregar, eliminar y modificar usuarios
        self.agregar_button = QPushButton("Agregar Usuario")
        self.eliminar_button = QPushButton("Eliminar Usuario")
        self.modificar_button = QPushButton("Modificar Usuario")  # Botón de Modificar
        self.agregar_button.clicked.connect(self.agregar_usuario)
        self.eliminar_button.clicked.connect(self.eliminar_usuario)
        self.modificar_button.clicked.connect(self.modificar_usuario)  # Conectar el botón a la función modificar

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.agregar_button)
        layout.addWidget(self.eliminar_button)
        layout.addWidget(self.modificar_button)  # Agregar el botón de Modificar al layout

        # Widget principal
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Cargar y mostrar datos
        self.cargar_datos()


    def modificar_usuario(self):
        filas_seleccionadas = self.table.selectionModel().selectedRows()
        if len(filas_seleccionadas) != 1:
            QMessageBox.warning(self, "Error", "Por favor, selecciona exactamente un usuario para modificar.")
            return
        
        fila_seleccionada = filas_seleccionadas[0].row()
        id_usuario = self.table.item(fila_seleccionada, 0).text()
        usuario = self.table.item(fila_seleccionada, 1).text()
        password = self.table.item(fila_seleccionada, 2).text()
        nombre = self.table.item(fila_seleccionada, 3).text()
        empresa = self.table.item(fila_seleccionada, 4).text()
        departamento = self.table.item(fila_seleccionada, 5).text()
        dias_vacaciones = self.table.item(fila_seleccionada, 6).text()
        dias_fiestas = self.table.item(fila_seleccionada, 7).text()
        dias_otros = self.table.item(fila_seleccionada, 8).text()

        dialogo = AgregarUsuarioDialog(self)
        dialogo.setWindowTitle("Modificar Usuario")
        dialogo.usuario_input.setText(usuario)
        dialogo.password_input.setText(password)
        dialogo.nombre_input.setText(nombre)
        dialogo.empresa_input.setText(empresa)
        dialogo.departamento_input.setText(departamento)
        dialogo.dias_vacaciones_input.setText(dias_vacaciones)
        dialogo.dias_fiestas_input.setText(dias_fiestas)
        dialogo.dias_otros_input.setText(dias_otros)

        if dialogo.exec_() == QDialog.Accepted:
            datos_usuario = dialogo.obtener_datos_usuario()
            self.modificar_usuario_en_db(id_usuario, datos_usuario)

    def modificar_usuario_en_db(self, id_usuario, datos_usuario):
        try:
            conexion = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="",
                database="calendario",
                port=3306
            )
            if conexion.is_connected():
                cursor = conexion.cursor()
                query = """UPDATE usuarios 
                           SET usuario = %s, password = %s, nombre = %s, empresa = %s, departamento = %s, 
                               dias_vacaciones = %s, dias_fiestas = %s, dias_otros = %s 
                           WHERE id = %s"""
                cursor.execute(query, (*datos_usuario, id_usuario))
                conexion.commit()
                print("Usuario modificado correctamente.")
                self.cargar_datos()
                conexion.close()
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")

    def cargar_datos(self):
        try:
            conexion = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="",
                database="calendario",
                port=3306
            )
            if conexion.is_connected():
                cursor = conexion.cursor()
                cursor.execute("""SELECT id, usuario, password, nombre, empresa, departamento, 
                               dias_vacaciones, dias_fiestas, dias_otros FROM usuarios""")
                rows = cursor.fetchall()

                # Limpiar tabla antes de cargar nuevos datos
                self.table.setRowCount(0)

                # Insertar datos en la tabla
                for row_number, row_data in enumerate(rows):
                    self.table.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        item = QTableWidgetItem(str(data))
                        if column_number > 0:  # Hacer editable las columnas desde usuario hasta días otros motivos
                            item.setFlags(item.flags() | Qt.ItemIsEditable)
                        self.table.setItem(row_number, column_number, item)

                conexion.close()
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")

    def agregar_usuario(self):
        # Crear una ventana de diálogo para ingresar los datos del nuevo usuario
        dialogo = AgregarUsuarioDialog(self)
        if dialogo.exec_() == QDialog.Accepted:
            datos_usuario = dialogo.obtener_datos_usuario()
            self.insertar_usuario_en_db(datos_usuario)

    def insertar_usuario_en_db(self, datos_usuario):
        try:
            conexion = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="",
                database="calendario",
                port=3306
            )
            if conexion.is_connected():
                cursor = conexion.cursor()

                # Comprobar si el usuario ya existe
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = %s", (datos_usuario[0],))
                if cursor.fetchone()[0] > 0:
                    QMessageBox.warning(self, "Error", "El usuario ya existe. Por favor, elija otro nombre de usuario.")
                    conexion.close()
                    return

                # Obtener el ID máximo actual
                cursor.execute("SELECT MAX(id) FROM usuarios")
                max_id = cursor.fetchone()[0]
                if max_id is None:
                    max_id = 0
                nuevo_id = max_id + 1
                
                cursor.execute("""INSERT INTO usuarios (id, usuario, password, nombre, empresa, departamento, 
                               dias_vacaciones, dias_fiestas, dias_otros) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                               (nuevo_id, *datos_usuario))
                conexion.commit()
                print("Usuario agregado correctamente.")
                self.cargar_datos()  # Recargar datos en la tabla después de la inserción
                conexion.close()
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")

    def eliminar_usuario(self):
        filas_seleccionadas = set()
        for index in self.table.selectionModel().selectedRows():
            filas_seleccionadas.add(index.row())

        if not filas_seleccionadas:
            QMessageBox.warning(self, "Error", "Por favor, selecciona al menos un usuario para eliminar.")
            return

        ids_a_eliminar = []
        for row in filas_seleccionadas:
            id_usuario = self.table.item(row, 0).text()
            ids_a_eliminar.append(id_usuario)

        confirmacion = QMessageBox.question(self, "Confirmar Eliminación", "¿Estás seguro de eliminar los usuarios seleccionados?",
                                            QMessageBox.Yes | QMessageBox.No)
        if confirmacion == QMessageBox.Yes:
            self.eliminar_usuarios_en_db(ids_a_eliminar)

    def eliminar_usuarios_en_db(self, ids_usuarios):
        try:
            conexion = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="",
                database="calendario",
                port=3306
            )
            if conexion.is_connected():
                cursor = conexion.cursor()
                for id_usuario in ids_usuarios:
                    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id_usuario,))
                conexion.commit()
                print("Usuarios eliminados correctamente.")
                self.cargar_datos()  # Recargar datos en la tabla después de la eliminación
                conexion.close()
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")

class AgregarUsuarioDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Nuevo Usuario")
        self.resize(300, 200)

        layout = QVBoxLayout()

        self.usuario_input = QLineEdit()
        self.password_input = QLineEdit()
        self.nombre_input = QLineEdit()
        self.empresa_input = QLineEdit()
        self.departamento_input = QLineEdit()
        self.dias_vacaciones_input = QLineEdit()
        self.dias_fiestas_input = QLineEdit()
        self.dias_otros_input = QLineEdit()

        layout.addWidget(QLabel("Usuario:"))
        layout.addWidget(self.usuario_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel("Nombre:"))
        layout.addWidget(self.nombre_input)
        layout.addWidget(QLabel("Empresa:"))
        layout.addWidget(self.empresa_input)
        layout.addWidget(QLabel("Departamento:"))
        layout.addWidget(self.departamento_input)
        layout.addWidget(QLabel("Días Vacaciones:"))
        layout.addWidget(self.dias_vacaciones_input)
        layout.addWidget(QLabel("Días Fiestas:"))
        layout.addWidget(self.dias_fiestas_input)
        layout.addWidget(QLabel("Días Otros Motivos:"))
        layout.addWidget(self.dias_otros_input)

        boton_aceptar = QPushButton("Aceptar")
        boton_aceptar.clicked.connect(self.accept)
        layout.addWidget(boton_aceptar)

        self.setLayout(layout)

    def obtener_datos_usuario(self):
        usuario = self.usuario_input.text()
        password = self.password_input.text()
        nombre = self.nombre_input.text()
        empresa = self.empresa_input.text()
        departamento = self.departamento_input.text()
        dias_vacaciones = self.dias_vacaciones_input.text()
        dias_fiestas = self.dias_fiestas_input.text()
        dias_otros = self.dias_otros_input.text()
        return (usuario, password, nombre, empresa, departamento, dias_vacaciones, dias_fiestas, dias_otros)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana_admin = VentanaAdmin()
    ventana_admin.show()
    sys.exit(app.exec_())

