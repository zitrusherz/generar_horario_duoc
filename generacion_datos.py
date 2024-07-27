import json
import pandas as pd
from datetime import datetime, time
from collections import defaultdict


def parse_horario(horario_str):
    if horario_str.lower() == 'online':
        return ('Online', None, None)

    dia, horas = horario_str.split(' ', 1)
    inicio_str, fin_str = horas.split(' - ')
    formato = '%H:%M:%S'
    inicio = datetime.strptime(inicio_str, formato).time()
    fin = datetime.strptime(fin_str, formato).time()

    return (dia, inicio, fin)

# Cargar los datos desde el archivo Excel
ruta_archivo = r'C:\Users\chris\Desktop\ANTONIO-VARAS.xlsx'
columnas_necesarias = ['Sigla', 'Asignatura', 'Sección', 'Horario', 'Docente']
horarios_ing_info = pd.read_excel(ruta_archivo, sheet_name='Hoja3', usecols=columnas_necesarias)

# Identificar cursos obligatorios
materias_obligatorias = {'ASY4131', 'APY4461', 'PGY4121', 'CSY4111', 'FCE1100', 'INU2101', 'MAT4140', 'MDY2131', 'PLC2101'}
es_obligatoria = horarios_ing_info['Sigla'].isin(materias_obligatorias)

# Inicializar los diccionarios de cursos
cursos_dict = defaultdict(lambda: {'Horarios': [], 'Datos': {}})
cursos_dict_obligatorio = defaultdict(lambda: {'Horarios': [], 'Datos': {}})

# Rellenar los diccionarios con la información de los cursos
for index, row in horarios_ing_info.iterrows():
    seccion_curso = row['Sección']
    horario_curso = row['Horario']
    datos_curso = row.drop(labels=['Sección', 'Horario']).to_dict()
    cursos_dict[seccion_curso]['Horarios'].append(horario_curso)
    cursos_dict[seccion_curso]['Datos'] = datos_curso
    if es_obligatoria[index]:
        cursos_dict_obligatorio[seccion_curso]['Horarios'].append(horario_curso)
        cursos_dict_obligatorio[seccion_curso]['Datos'] = datos_curso

# Guardar los datos en archivos JSON separados
with open('cursos_datos.json', 'w') as f:
    json.dump(cursos_dict, f, indent=4)

with open('cursos_datos_obl.json', 'w') as f:
    json.dump(cursos_dict_obligatorio, f, indent=4)

# Leer los datos desde los archivos JSON para verificación
with open('cursos_datos.json', 'r') as f:
    data_cursos = json.load(f)

with open('cursos_datos_obl.json', 'r') as f:
    data_cursos_obl = json.load(f)

print("Datos cursos:", data_cursos)
print("Datos cursos obligatorios:", data_cursos_obl)
