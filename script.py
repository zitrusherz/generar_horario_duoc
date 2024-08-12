import sqlite3
import itertools
import logging
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Conectar a la base de datos
def connect_db():
    return sqlite3.connect('horarios.db')


# Obtener datos de cursos específicos
def obtener_cursos(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, sigla, nombre FROM Curso WHERE id IN (1, 2, 3, 4, 5, 6, 7, 8, 9)")
    cursos = cursor.fetchall()
    return cursos


# Obtener secciones de los cursos específicos
def obtener_secciones(conn, cursos):
    cursor = conn.cursor()
    secciones = []
    for curso in cursos:
        curso_id = curso[0]
        cursor.execute(
            "SELECT s.id, s.sigla, s.codigo_seccion, s.id_curso, s.nombre_profesor, s.online, h.dia, h.inicio, h.fin "
            "FROM Seccion s "
            "JOIN Horario h ON s.id = h.id_seccion "
            "WHERE s.id_curso = ?", (curso_id,))
        secciones.extend(cursor.fetchall())
    return secciones


# Convertir tiempo a minutos desde medianoche
def tiempo_a_minutos(tiempo):
    try:
        partes = tiempo.split(':')
        h, m = int(partes[0]), int(partes[1])
        return h * 60 + m
    except (ValueError, IndexError):
        logger.error(f"Error al convertir el tiempo: {tiempo}. Asegúrate de que esté en formato HH:MM o HH:MM:SS.")
        return None


# Verificar si dos horarios se solapan
def solapan(horario1, horario2):
    if horario1['dia'] != horario2['dia']:
        return False
    inicio1 = tiempo_a_minutos(horario1['inicio'])
    fin1 = tiempo_a_minutos(horario1['fin'])
    inicio2 = tiempo_a_minutos(horario2['inicio'])
    fin2 = tiempo_a_minutos(horario2['fin'])

    # Verificar si alguno de los valores es None
    if None in (inicio1, fin1, inicio2, fin2):
        logger.error(f"Error al verificar solapamiento entre horarios: {horario1} y {horario2}.")
        return False

    return not (fin1 <= inicio2 or fin2 <= inicio1)


# Función para verificar una combinación
def verificar_combinacion(combinacion):
    ids_cursos = set()
    for i in range(len(combinacion)):
        ids_cursos.add(combinacion[i]['id'])
        for j in range(i + 1, len(combinacion)):
            if solapan(combinacion[i], combinacion[j]):
                return None
    if len(ids_cursos) == 9:
        return combinacion
    return None


# Generar combinaciones sin solapamientos
def generar_combinaciones_sin_solapamientos(secciones):
    secciones_por_curso = {}
    for seccion in secciones:
        curso_id = seccion[3]
        if curso_id not in secciones_por_curso:
            secciones_por_curso[curso_id] = []
        secciones_por_curso[curso_id].append({
            'id': seccion[0],
            'dia': seccion[6],
            'inicio': seccion[7],
            'fin': seccion[8]
        })

    # Generar todas las combinaciones posibles de secciones sin solapamiento
    todas_combinaciones = itertools.product(*secciones_por_curso.values())

    combinaciones_validas = []

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(verificar_combinacion, combinacion) for combinacion in todas_combinaciones]
        for future in as_completed(futures):
            result = future.result()
            if result:
                combinaciones_validas.append(result)

    return combinaciones_validas


# Guardar combinaciones válidas en la base de datos
def guardar_combinaciones(conn, combinaciones):
    cursor = conn.cursor()

    # Imprimir las primeras 40 combinaciones
    logger.info("Primeras 40 combinaciones válidas:")
    for idx, combinacion in enumerate(combinaciones[:40]):
        ids = [seccion['id'] for seccion in combinacion]
        logger.info(f"Combinación {idx + 1}: {ids}")

    # Guardar las combinaciones en la base de datos
    for combinacion in combinaciones:
        if len(combinacion) == 9:
            try:
                cursor.execute(
                    "INSERT INTO Obligatorios (curso1_id, curso2_id, curso3_id, curso4_id, curso5_id, curso6_id, curso7_id, curso8_id, curso9_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    tuple([seccion['id'] for seccion in combinacion]))
            except sqlite3.Error as e:
                logger.error(f"Error al insertar combinación: {e}")
    conn.commit()


def main():
    conn = connect_db()
    cursos = obtener_cursos(conn)
    secciones = obtener_secciones(conn, cursos)
    combinaciones_validas = generar_combinaciones_sin_solapamientos(secciones)
    logger.info(f"Se encontraron {len(combinaciones_validas)} combinaciones válidas.")
    guardar_combinaciones(conn, combinaciones_validas)
    conn.close()


if __name__ == '__main__':
    main()
