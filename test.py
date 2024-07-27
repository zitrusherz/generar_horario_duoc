import json
from datetime import datetime

# Cargar los datos del archivo JSON
with open('datos_cursos_org.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

cursos_dict = data.get('cursos_dict_obligatorio', {})

# Cargar solapamientos
with open('solapamientos.json', 'r', encoding='utf-8') as file:
    solapamientos = json.load(file)

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

# Procesar y almacenar horarios de cursos sin solapamientos
horarios_procesados = {}

for course_id, course_info in cursos_dict.items():
    if course_id in solapamientos:
        print(f"El curso {course_id} tiene solapamientos y será omitido.")
        continue
    print(f"Procesando curso: {course_id}")
    horarios_procesados[course_id] = [parse_time(horario) for horario in course_info['Horarios']]
    print(f"Horarios procesados para {course_id}: {horarios_procesados[course_id]}")

# Guardar horarios procesados en un archivo JSON
with open('horarios_procesados.json', 'w', encoding='utf-8') as outfile:
    json.dump(horarios_procesados, outfile, ensure_ascii=False, indent=4)

print("Horarios procesados guardados en 'horarios_procesados.json'")
