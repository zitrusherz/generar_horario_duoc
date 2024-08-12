import sqlite3
from datetime import datetime

# Conexión a la base de datos SQLite
conn = sqlite3.connect('horarios.db')
cursor = conn.cursor()

# Eliminar registros existentes en la tabla Solapamientos
cursor.execute('DELETE FROM Solapamientos')
conn.commit()


# Función para convertir cadena de tiempo a objeto datetime.time
def convertir_a_tiempo(hora_str):
    return datetime.strptime(hora_str, '%H:%M:%S').time()


# Función para calcular si hay solapamiento entre dos horarios
def hay_solapamiento(inicio1, fin1, inicio2, fin2):
    inicio1 = convertir_a_tiempo(inicio1)
    fin1 = convertir_a_tiempo(fin1)
    inicio2 = convertir_a_tiempo(inicio2)
    fin2 = convertir_a_tiempo(fin2)

    return max(inicio1, inicio2) < min(fin1, fin2)


# Consulta para encontrar solapamientos entre horarios
cursor.execute('''
SELECT h1.id_seccion, h2.id_seccion, h1.dia, h1.inicio, h1.fin, h2.inicio, h2.fin
FROM Horario h1
JOIN Horario h2 ON h1.dia = h2.dia AND h1.id_seccion != h2.id_seccion
''')

resultados = cursor.fetchall()

# Insertar los solapamientos en la tabla
solapamientos = []
for seccion1_id, seccion2_id, dia, inicio1, fin1, inicio2, fin2 in resultados:
    if hay_solapamiento(inicio1, fin1, inicio2, fin2):
        solapamientos.append((seccion1_id, seccion2_id, dia, inicio1, fin1, inicio2, fin2, True))
    else:
        solapamientos.append((seccion1_id, seccion2_id, dia, inicio1, fin1, inicio2, fin2, False))

cursor.executemany('''
INSERT INTO Solapamientos (id_seccion1, id_seccion2, dia, inicio1, fin1, inicio2, fin2, solapamiento)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', solapamientos)

# Confirmar y cerrar conexión
conn.commit()
conn.close()
