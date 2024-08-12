import sqlite3
import pandas as pd
import json

# Conexión a la base de datos 'horarios.db'
conn = sqlite3.connect('horarios.db')

# Combinaciones de cursos proporcionadas
combinations = [
    "MAT4140-006D,PGY4121-008D,FCE1100-020D,PLC2101-022D,MDY2131-002D,INU2101-015D"
]

# Para cada combinación, generamos el prompt de datos
for idx, comb in enumerate(combinations, start=1):
    cursos = comb.split(',')

    # Consultar los datos necesarios de las tablas Horario, Seccion y Curso
    query = """
    SELECT s.codigo_seccion, s.nombre_profesor, c.nombre AS nombre_curso, h.dia, h.inicio, h.fin
    FROM Horario h
    JOIN Seccion s ON h.id_seccion = s.id
    JOIN Curso c ON s.id_curso = c.id
    WHERE s.codigo_seccion IN ({})
    """.format(",".join(f"'{curso}'" for curso in cursos))

    df = pd.read_sql_query(query, conn)

    # Convertir los tiempos a cadenas de texto en el formato 'HH:MM'
    df['inicio'] = pd.to_datetime(df['inicio'], format='%H:%M:%S', errors='coerce').dt.strftime('%H:%M')
    df['fin'] = pd.to_datetime(df['fin'], format='%H:%M:%S', errors='coerce').dt.strftime('%H:%M')

    # Reemplazar valores NaT (errores de conversión) por un string indicando el error
    df['inicio'] = df['inicio'].fillna('Formato inválido')
    df['fin'] = df['fin'].fillna('Formato inválido')

    # Agrupar los datos por código de sección
    grupos = df.groupby('codigo_seccion')

    # Formatear los datos para el prompt
    datos_para_prompt = []
    for codigo, grupo in grupos:
        curso_info = {
            "codigo_seccion": codigo,
            "nombre_profesor": grupo['nombre_profesor'].iloc[0],
            "nombre_curso": grupo['nombre_curso'].iloc[0],
            "horarios": grupo[['dia', 'inicio', 'fin']].to_dict(orient='records')
        }
        datos_para_prompt.append(curso_info)

    # Convertir a JSON-like string para el prompt
    datos_json = json.dumps(datos_para_prompt, indent=2, ensure_ascii=False)

    # Imprimir el resultado para usar en el prompt
    print(f"""
    Para la combinación {idx}, aquí tienes los datos necesarios para cada curso, con los horarios de las clases, los nombres de los cursos y los profesores:

    {datos_json}

    Usa estos datos para crear una visualización con Canvas, donde cada curso esté representado con bloques de tiempo que reflejen sus horarios en una tabla de días de la semana. Incluye el nombre del curso y el profesor debajo de cada horario.
    """)

# Cerramos la conexión
conn.close()
