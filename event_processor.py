import json
from datetime import datetime

# Función para convertir el horario en formato datetime
def parse_time(time_str):
    # Manejar el caso especial 'Online'
    if time_str.lower() == 'online':
        return None

    try:
        day, times = time_str.split(maxsplit=1)
        start_time, end_time = times.split(' - ')
        return {
            'day': day,
            'start': datetime.strptime(start_time, '%H:%M:%S').time(),
            'end': datetime.strptime(end_time, '%H:%M:%S').time(),
            'raw': time_str  # Guardar el horario original para referencias
        }
    except ValueError as e:
        print(f"Formato de tiempo incorrecto: {time_str} ({e})")
        return None

# Función para verificar solapamiento de horarios
def check_overlap(horario1, horario2):
    if horario1 is None or horario2 is None:
        return False
    return (
            horario1['day'] == horario2['day'] and
            horario1['start'] < horario2['end'] and
            horario1['end'] > horario2['start']
    )

# Leer datos de cursos desde los archivos JSON
with open('cursos_datos.json', 'r') as f:
    cursos_dict = json.load(f)

with open('cursos_datos_obl.json', 'r') as f:
    cursos_dict_obligatorio = json.load(f)

# Función para encontrar solapamientos y generar el archivo de salida
def find_and_save_overlaps(cursos_dict, output_file):
    # Diccionario para almacenar los solapamientos
    solapamientos = {}

    # Diccionario para almacenar los horarios procesados
    horarios_procesados = {}

    # Procesar y almacenar horarios
    for course_id, course_info in cursos_dict.items():
        horarios_procesados[course_id] = [parse_time(horario) for horario in course_info['Horarios']]

    # Comparar todos los cursos entre sí para encontrar solapamientos
    course_ids = list(cursos_dict.keys())
    n = len(course_ids)

    for i in range(n):
        course_id = course_ids[i]
        horarios = horarios_procesados[course_id]
        for j in range(i + 1, n):
            other_course_id = course_ids[j]
            other_horarios = horarios_procesados[other_course_id]
            for horario in horarios:
                if horario is None:
                    continue
                for other_horario in other_horarios:
                    if other_horario is None:
                        continue
                    if check_overlap(horario, other_horario):
                        if course_id not in solapamientos:
                            solapamientos[course_id] = []
                        if other_course_id not in solapamientos[course_id]:
                            solapamientos[course_id].append({
                                'curso': other_course_id,
                                'horario_1': horario['raw'],
                                'horario_2': other_horario['raw']
                            })
                        if other_course_id not in solapamientos:
                            solapamientos[other_course_id] = []
                        if course_id not in [s['curso'] for s in solapamientos[other_course_id]]:
                            solapamientos[other_course_id].append({
                                'curso': course_id,
                                'horario_1': other_horario['raw'],
                                'horario_2': horario['raw']
                            })
                        break

    # Guardar los solapamientos en un archivo JSON
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(solapamientos, outfile, ensure_ascii=False, indent=4)

    print(f"Solapamientos encontrados y guardados en {output_file}")

# Generar solapamientos para ambos conjuntos de datos
find_and_save_overlaps(cursos_dict, 'solapamientos.json')
find_and_save_overlaps(cursos_dict_obligatorio, 'solapamientos_obl.json')
