import sqlite3
import json

# Conexión a la base de datos SQLite
conn = sqlite3.connect('horarios.db')
cursor = conn.cursor()

# Mapeo de abreviaturas a nombres completos de los días de la semana
dias_semana = {
    "Lu": "Lunes",
    "Ma": "Martes",
    "Mi": "Miércoles",
    "Ju": "Jueves",
    "Vi": "Viernes",
    "Sa": "Sábado",
    "Do": "Domingo"
}

# Cargar datos desde el archivo JSON
with open('cursos_datos_obl.json', 'r') as file:
    data = json.load(file)

# Insertar datos en la tabla Curso y obtener el id_curso
for seccion_codigo, seccion_datos in data.items():
    sigla = seccion_datos['Datos']['Sigla']
    nombre_curso = seccion_datos['Datos']['Asignatura']
    nombre_profesor = seccion_datos['Datos'].get('Docente', '')
    horarios = seccion_datos['Horarios']

    # Verificar si la clase es online
    es_online = 1 if horarios and horarios[0] == "Online" else 0

    # Obtener o insertar el curso y obtener su id
    cursor.execute('SELECT id FROM Curso WHERE sigla = ?', (sigla,))
    curso_id = cursor.fetchone()
    if curso_id is None:
        cursor.execute('INSERT INTO Curso (sigla, nombre) VALUES (?, ?)', (sigla, nombre_curso))
        curso_id = cursor.lastrowid
    else:
        curso_id = curso_id[0]

    # Insertar datos en la tabla Seccion
    cursor.execute(
        'INSERT INTO Seccion (sigla, codigo_seccion, id_curso, nombre_profesor, online) VALUES (?, ?, ?, ?, ?)',
        (sigla, seccion_codigo, curso_id, nombre_profesor, es_online))
    seccion_id = cursor.lastrowid

    # Insertar datos en la tabla Horario, omitir si es online
    if not es_online:
        for horario in horarios:
            if 'Online' in horario:
                continue
            dia_abrev, horario_dia = horario.split(maxsplit=1)
            dia = dias_semana.get(dia_abrev, dia_abrev)  # Convertir a nombre completo del día
            inicio, fin = horario_dia.split('-')
            cursor.execute('INSERT INTO Horario (id_seccion, dia, inicio, fin) VALUES (?, ?, ?, ?)',
                           (seccion_id, dia, inicio.strip(), fin.strip()))

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()
