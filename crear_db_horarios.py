import sqlite3

# Conexión a la base de datos (o creación si no existe)
conn = sqlite3.connect('horarios.db')
cursor = conn.cursor()

# Crear tabla Curso
cursor.execute('''
CREATE TABLE IF NOT EXISTS Curso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sigla TEXT NOT NULL,
    nombre TEXT NOT NULL
);
''')

# Crear tabla Seccion
cursor.execute('''
CREATE TABLE IF NOT EXISTS Seccion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sigla TEXT NOT NULL,  
    codigo_seccion TEXT NOT NULL,  
    id_curso INTEGER,
    nombre_profesor TEXT,
    online BOOLEAN,
    FOREIGN KEY (id_curso) REFERENCES Curso(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Horario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_seccion INTEGER,
    dia TEXT,
    inicio TEXT,
    fin TEXT,
    FOREIGN KEY (id_seccion) REFERENCES Seccion(id)
)
''')
# Crear tabla Solapamiento
cursor.execute('''
CREATE TABLE IF NOT EXISTS Solapamientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_seccion1 INTEGER,
    id_seccion2 INTEGER,
    dia TEXT,
    inicio1 TEXT,
    fin1 TEXT,
    inicio2 TEXT,
    fin2 TEXT,
    solapamiento BOOLEAN,
    FOREIGN KEY (id_seccion1) REFERENCES Seccion(id),
    FOREIGN KEY (id_seccion2) REFERENCES Seccion(id)
)
''')

# Crear tabla Ventana_Tiempo
cursor.execute('''
CREATE TABLE IF NOT EXISTS Ventana_Tiempo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seccion1_id INTEGER NOT NULL,
    seccion2_id INTEGER NOT NULL,
    ventana_tiempo INTEGER NOT NULL,
    FOREIGN KEY (seccion1_id) REFERENCES Seccion(id),
    FOREIGN KEY (seccion2_id) REFERENCES Seccion(id)
)
''')

# Confirmar cambios y cerrar la conexión
conn.commit()
conn.close()
