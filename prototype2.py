import sqlite3
import pandas as pd
import cupy as cp
from multiprocessing import Pool

# Conexión a la base de datos
conn = sqlite3.connect('horarios.db')


def cargar_datos():
    cursos_df = pd.read_sql_query("SELECT * FROM cursos", conn)
    horarios_df = pd.read_sql_query("SELECT * FROM horarios", conn)
    solapamientos_df = pd.read_sql_query("SELECT * FROM solapamientos", conn)
    ventanas_tiempo_df = pd.read_sql_query("SELECT * FROM ventanas_tiempo", conn)

    return cursos_df, horarios_df, solapamientos_df, ventanas_tiempo_df


cursos_df, horarios_df, solapamientos_df, ventanas_tiempo_df = cargar_datos()

from itertools import product

# Agrupamos los horarios por curso
grupos_cursos = horarios_df.groupby('seccion')

# Generar todas las combinaciones posibles de una sección por curso
combinaciones_posibles = list(product(*[grupo.itertuples(index=False, name=None) for _, grupo in grupos_cursos]))

def verificar_solapamientos(combinacion):
    for i in range(len(combinacion)):
        for j in range(i+1, len(combinacion)):
            seccion_1 = combinacion[i][2]  # seccion
            seccion_2 = combinacion[j][2]  # seccion
            if not ventanas_tiempo_df[(ventanas_tiempo_df['seccion_1'] == seccion_1) &
                                       (ventanas_tiempo_df['seccion_2'] == seccion_2)].empty:
                ventana_tiempo = ventanas_tiempo_df[(ventanas_tiempo_df['seccion_1'] == seccion_1) &
                                                    (ventanas_tiempo_df['seccion_2'] == seccion_2)]
                if ventana_tiempo['ventana_tiempo'].iloc[0] < 0:
                    return False
    return True

# Verificación de combinaciones válidas utilizando múltiples procesos
def filtrar_combinaciones_validas(combinaciones):
    combinaciones_validas = []
    with Pool(processes=8) as pool:
        resultados = pool.map(verificar_solapamientos, combinaciones)
    for i, es_valida in enumerate(resultados):
        if es_valida:
            combinaciones_validas.append(combinaciones[i])
    return combinaciones_validas

combinaciones_validas = filtrar_combinaciones_validas(combinaciones_posibles)


def almacenar_combinaciones(combinaciones_validas):
    # Crear una nueva tabla para almacenar las combinaciones válidas
    conn.execute('''
        CREATE TABLE IF NOT EXISTS combinaciones_validas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            combinacion TEXT NOT NULL
        )
    ''')
    for combinacion in combinaciones_validas:
        conn.execute('INSERT INTO combinaciones_validas (combinacion) VALUES (?)', (str(combinacion),))
    conn.commit()

almacenar_combinaciones(combinaciones_validas)
