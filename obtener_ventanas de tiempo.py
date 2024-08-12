import sqlite3
from datetime import datetime

# Conexión a la base de datos SQLite
conn = sqlite3.connect('horarios.db')
cursor = conn.cursor()
cursor.execute('DELETE FROM Ventana_Tiempo')
conn.commit()
# Función para convertir tiempo a minutos
def tiempo_a_minutos(tiempo):
    horas, minutos, _ = map(int, tiempo.split(':'))
    return horas * 60 + minutos

# Función para calcular la ventana de tiempo entre dos horarios
def calcular_ventana_tiempo(fin1, inicio2):
    fin1_min = tiempo_a_minutos(fin1)
    inicio2_min = tiempo_a_minutos(inicio2)
    return inicio2_min - fin1_min

# Consulta para encontrar ventanas de tiempo y almacenarlas en la tabla 'ventanas_tiempo'
cursor.execute('''
SELECT h1.id_seccion, h2.id_seccion, h1.dia, h1.fin, h2.inicio
FROM Horario h1
JOIN Horario h2 ON h1.dia = h2.dia AND h1.id_seccion != h2.id_seccion
WHERE h1.fin <= h2.inicio
ORDER BY h1.dia, h1.fin
''')

resultados = cursor.fetchall()

# Insertar las ventanas de tiempo en la tabla
ventanas_tiempo = []
for seccion1_id, seccion2_id, dia, fin1, inicio2 in resultados:
    ventana_tiempo = calcular_ventana_tiempo(fin1, inicio2)
    ventanas_tiempo.append((seccion1_id, seccion2_id, ventana_tiempo))

cursor.executemany('''
INSERT INTO Ventana_Tiempo (seccion1_id, seccion2_id, ventana_tiempo)
VALUES (?, ?, ?)
''', ventanas_tiempo)

# Confirmar y cerrar conexión
conn.commit()
conn.close()
