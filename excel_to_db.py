import sqlite3
import pandas as pd

# Conectar a la base de datos SQLite
conn = sqlite3.connect('antonio_varas.db')  # Ruta relativa
cursor = conn.cursor()

# Crear las tablas en la base de datos
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sede (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL
    );
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Carrera (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        sede_id INTEGER,
        FOREIGN KEY (sede_id) REFERENCES Sede(id)
    );
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Curso (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sigla TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL
    );
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Docente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL
    );
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Seccion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        curso_id INTEGER,
        cod_seccion TEXT NOT NULL,
        docente_id INTEGER,
        FOREIGN KEY (curso_id) REFERENCES Curso(id),
        FOREIGN KEY (docente_id) REFERENCES Docente(id)
    );
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Horario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seccion_id INTEGER,
        dia TEXT,
        inicio TEXT,
        fin TEXT,
        FOREIGN KEY (seccion_id) REFERENCES Seccion(id)
    );
''')
conn.commit()

# Leer los datos del archivo Excel
df = pd.read_excel('/ANTONIO-VARAS.xlsx', sheet_name='Hoja1')  # Ruta ajustada

# Limpieza: eliminar filas donde 'Docente' es NaN
df = df.dropna(subset=['Docente'])

# Insertar datos únicos en la tabla Sede
sedes_unicas = df['Sede'].unique()
for sede in sedes_unicas:
    cursor.execute('INSERT OR IGNORE INTO Sede (nombre) VALUES (?)', (sede,))

# Obtener los IDs de las sedes para su uso en inserciones futuras
cursor.execute('SELECT id, nombre FROM Sede')
sede_id_map = {nombre: id for id, nombre in cursor.fetchall()}

# Insertar datos en la tabla Carrera
for _, row in df.iterrows():
    sede_id = sede_id_map[row['Sede']]
    cursor.execute('INSERT OR IGNORE INTO Carrera (nombre, sede_id) VALUES (?, ?)', (row['Carrera'], sede_id))

# Insertar datos en la tabla Curso
cursos_unicos = df.drop_duplicates(subset=['Sigla'])
for _, curso in cursos_unicos.iterrows():
    cursor.execute('INSERT OR IGNORE INTO Curso (sigla, nombre) VALUES (?, ?)', (curso['Sigla'], curso['Asignatura']))

# Insertar datos en la tabla Docente
docentes_unicos = df['Docente'].unique()
for docente in docentes_unicos:
    cursor.execute('INSERT OR IGNORE INTO Docente (nombre) VALUES (?)', (docente,))

# Obtener los IDs de los cursos, docentes y secciones
cursor.execute('SELECT id, sigla FROM Curso')
curso_id_map = {sigla: id for id, sigla in cursor.fetchall()}
cursor.execute('SELECT id, nombre FROM Docente')
docente_id_map = {nombre: id for id, nombre in cursor.fetchall()}

# Preparar para insertar datos en la tabla Seccion
# Primero, insertamos los datos únicos de Sección
secciones_unicas = df.drop_duplicates(subset=['Sigla', 'Sección'])
for _, seccion in secciones_unicas.iterrows():
    curso_id = curso_id_map[seccion['Sigla']]
    docente_id = docente_id_map[seccion['Docente']]
    cursor.execute('INSERT OR IGNORE INTO Seccion (curso_id, cod_seccion, docente_id) VALUES (?, ?, ?)', (curso_id, seccion['Sección'], docente_id))

# Obtener los IDs de las secciones para su uso en inserciones futuras
cursor.execute('SELECT id, cod_seccion, curso_id FROM Seccion')
seccion_id_map = {(row[1], row[2]): row[0] for row in cursor.fetchall()}  # Mapeo (cod_seccion, curso_id) a id

# Insertar datos en la tabla Horario
for _, row in df.iterrows():
    seccion_id = seccion_id_map[(row['Sección'], curso_id_map[row['Sigla']])]
    cursor.execute('''
        INSERT INTO Horario (seccion_id, dia, inicio, fin)
        VALUES (?, ?, ?, ?)
    ''', (seccion_id, row['Dia'], row['Inicio'], row['Fin']))

# Confirmar los cambios y cerrar la conexión
conn.commit()
cursor.close()
conn.close()

print("Datos insertados correctamente en la base de datos.")
