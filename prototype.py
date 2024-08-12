"""import json
from datetime import datetime
import numpy as np
import cupy as cp
from statistics import mean, median, mode, StatisticsError
from multiprocessing import Pool, cpu_count
import psutil

# Función para cargar datos desde un archivo JSON
def cargar_datos(archivo):
    with open(archivo, 'r') as f:
        return json.load(f)

# Función para calcular la ventana de tiempo en minutos
def calcular_ventana(dias, horarios):
    ventana_total = 0
    formato_hora = "%H:%M:%S"

    # Agrupar horarios por día
    horarios_por_dia = {}
    for dia, horario in zip(dias, horarios):
        if dia not in horarios_por_dia:
            horarios_por_dia[dia] = []
        horarios_por_dia[dia].append(horario)

    # Calcular ventanas de tiempo dentro de cada día
    for dia, horarios in horarios_por_dia.items():
        horarios.sort()  # Asegurar que los horarios estén ordenados
        for i in range(len(horarios) - 1):
            fin_anterior = datetime.strptime(horarios[i].split('-')[1].strip(), formato_hora)
            inicio_siguiente = datetime.strptime(horarios[i + 1].split('-')[0].strip(), formato_hora)
            ventana_total += (inicio_siguiente - fin_anterior).total_seconds() / 60  # Convertir a minutos

    return ventana_total

# Función para calcular ventanas para una lista de combinaciones
def calcular_ventanas_para_combinaciones(lista_combinaciones, datos_horarios):
    ventanas_por_combinacion = {}
    for sublist in lista_combinaciones:  # Iterar sobre sublistas dentro de combinaciones_validas
        for combinacion in sublist:
            ventana_total = 0
            for seccion in combinacion:
                if seccion in datos_horarios:
                    dias = datos_horarios[seccion]["dias"]
                    horario = datos_horarios[seccion]["horario"]
                    ventana_total += calcular_ventana(dias, horario)

            combinacion_str = '_'.join(combinacion)
            ventanas_por_combinacion[combinacion_str] = ventana_total
    return ventanas_por_combinacion

# Función para calcular medidas estadísticas usando CuPy
def calcular_medidas(ventanas):
    if not ventanas:
        return None
    ventanas_gpu = cp.array(ventanas)
    media = cp.mean(ventanas_gpu).item()
    mediana = cp.median(ventanas_gpu).item()
    varianza = cp.var(ventanas_gpu).item()
    desviacion_estandar = cp.std(ventanas_gpu).item()
    rango = cp.ptp(ventanas_gpu).item()
    rango_intercuartilico = (cp.percentile(ventanas_gpu, 75) - cp.percentile(ventanas_gpu, 25)).item()

    # Calcular moda con numpy en CPU debido a falta de soporte en CuPy
    ventanas_cpu = cp.asnumpy(ventanas_gpu)
    try:
        moda_valor = mode(ventanas_cpu)
    except StatisticsError:
        moda_valor = None

    return {
        "media": media,
        "mediana": mediana,
        "moda": moda_valor,
        "rango": rango,
        "varianza": varianza,
        "desviacion_estandar": desviacion_estandar,
        "rango_intercuartilico": rango_intercuartilico
    }

if __name__ == '__main__':
    # Cargar los datos de horarios y combinaciones
    datos_horarios = cargar_datos('datos_horarios_transformados_completo.json')
    combinaciones_validas = cargar_datos('combinaciones_validas.json')

    # Limitación del uso de CPU al 90%
    num_cpus = max(1, int(cpu_count() * 0.9))

    # Limitar el uso de RAM al 90%
    memory_limit = int(psutil.virtual_memory().total * 0.9)

    # Usar multiprocessing para acelerar el cálculo de ventanas
    chunk_size = len(combinaciones_validas) // num_cpus

    with Pool(processes=num_cpus) as pool:
        resultados = pool.starmap(calcular_ventanas_para_combinaciones,
                                  [(combinaciones_validas[i:i + chunk_size], datos_horarios) for i in
                                   range(0, len(combinaciones_validas), chunk_size)])

    ventanas_por_combinacion = {}
    for resultado in resultados:
        ventanas_por_combinacion.update(resultado)

    # Clasificar las ventanas por tamaño de combinación
    ventanas_5 = [ventana for key, ventana in ventanas_por_combinacion.items() if len(key.split('_')) == 5]
    ventanas_6 = [ventana for key, ventana in ventanas_por_combinacion.items() if len(key.split('_')) == 6]
    ventanas_7 = [ventana for key, ventana in ventanas_por_combinacion.items() if len(key.split('_')) == 7]
    ventanas_8 = [ventana for key, ventana in ventanas_por_combinacion.items() if len(key.split('_')) == 8]

    # Calcular medidas para cada grupo y total
    medidas_totales = calcular_medidas(list(ventanas_por_combinacion.values()))
    medidas_5 = calcular_medidas(ventanas_5)
    medidas_6 = calcular_medidas(ventanas_6)
    medidas_7 = calcular_medidas(ventanas_7)
    medidas_8 = calcular_medidas(ventanas_8)

    # Imprimir las medidas calculadas
    print("medidas_totales:", medidas_totales)
    print("medidas_5_cursos:", medidas_5)
    print("medidas_6_cursos:", medidas_6)
    print("medidas_7_cursos:", medidas_7)
    print("medidas_8_cursos:", medidas_8)

    # Guardar los resultados en un archivo JSON
    resultados_finales = {
        "ventanas_por_combinacion": ventanas_por_combinacion,
        "medidas_totales": medidas_totales,
        "medidas_5_cursos": medidas_5,
        "medidas_6_cursos": medidas_6,
        "medidas_7_cursos": medidas_7,
        "medidas_8_cursos": medidas_8
    }

    with open('resultados_ventanas.json', 'w') as f:
        json.dump(resultados_finales, f, indent=4)

    print("Resultados guardados en 'resultados_ventanas.json'")
"""



import sqlite3
from datetime import datetime
import numpy as np
from itertools import combinations, product
import dask
from dask import delayed, compute
from dask.diagnostics import ProgressBar
from dask.distributed import Client
# Conexión a la base de datos SQLite

conn = sqlite3.connect('horarios.db')
cursor = conn.cursor()
# Crear tabla Combinaciones
cursor.execute('''
CREATE TABLE IF NOT EXISTS Combinaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    curso1_id INTEGER,
    curso2_id INTEGER,
    curso3_id INTEGER,
    curso4_id INTEGER,
    curso5_id INTEGER,
    curso6_id INTEGER,
    curso7_id INTEGER,
    curso8_id INTEGER,
    FOREIGN KEY (curso1_id) REFERENCES Seccion(id),
    FOREIGN KEY (curso2_id) REFERENCES Seccion(id),
    FOREIGN KEY (curso3_id) REFERENCES Seccion(id),
    FOREIGN KEY (curso4_id) REFERENCES Seccion(id),
    FOREIGN KEY (curso5_id) REFERENCES Seccion(id),
    FOREIGN KEY (curso6_id) REFERENCES Seccion(id),
    FOREIGN KEY (curso7_id) REFERENCES Seccion(id),
    FOREIGN KEY (curso8_id) REFERENCES Seccion(id)
)
''')

# Crear tabla Ventanas_Tiempo
cursor.execute('''
CREATE TABLE IF NOT EXISTS Ventanas_Tiempo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    combinacion_id INTEGER,
    ventana_total INTEGER,
    FOREIGN KEY (combinacion_id) REFERENCES Combinaciones(id)
)
''')

# Crear tabla Estadisticas
cursor.execute('''
CREATE TABLE IF NOT EXISTS Estadisticas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    combinacion_id INTEGER,
    media REAL,
    mediana REAL,
    moda REAL,
    rango REAL,
    varianza REAL,
    desviacion_estandar REAL,
    rango_intercuartilico REAL,
    FOREIGN KEY (combinacion_id) REFERENCES Combinaciones(id)
)
''')
# Conexión a la base de datos
conn = sqlite3.connect('horarios.db')
cursor = conn.cursor()


import statistics

"""def calcular_estadisticas(combinacion):
    if not combinacion:
        return (None, None, None, None, None, None, None)
    datos = np.array(combinacion)  # Convertimos la combinación a un array de numpy para los cálculos
    try:
        moda = statistics.mode(datos)  # Calculamos la moda usando statistics
    except statistics.StatisticsError:
        moda = None  # En caso de que no haya una moda única

    media = np.mean(datos)
    mediana = np.median(datos)
    rango = np.ptp(datos)
    varianza = np.var(datos)
    desviacion_estandar = np.std(datos)
    rango_intercuartilico = np.percentile(datos, 75) - np.percentile(datos, 25)
    return (media, mediana, moda, rango, varianza, desviacion_estandar, rango_intercuartilico)"""


# Función para obtener secciones por curso fuera de las funciones paralelizadas
def obtener_secciones_por_curso(sigla):
    conn = sqlite3.connect('horarios.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM Seccion WHERE sigla = ?', (sigla,))
    secciones = [id_seccion for (id_seccion,) in cursor.fetchall()]
    conn.close()
    return secciones


# Función para verificar solapamientos usando datos preprocesados
def verificar_solapamientos_preprocesado(seccion1, seccion2, solapamientos):
    return (seccion1, seccion2) in solapamientos or (seccion2, seccion1) in solapamientos


# Función que será llamada por Dask para verificar si una combinación es válida
def es_combinacion_valida(combinacion, solapamientos):
    return all(
        not verificar_solapamientos_preprocesado(s1, s2, solapamientos) for s1 in combinacion for s2 in combinacion if
        s1 != s2)


def obtener_solapamientos():
    conn = sqlite3.connect('horarios.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id_seccion1, id_seccion2 FROM Solapamientos WHERE solapamiento = 1')
    solapamientos = [(row[0], row[1]) for row in cursor.fetchall()]
    conn.close()
    return solapamientos


def procesar_combinaciones(combinacion, solapamientos):
    if not es_combinacion_valida(combinacion, solapamientos):
        return None, None, None
    estadisticas = (0, 0, 0, 0, 0, 0, 0)
    ventana_total = 0
    return estadisticas, ventana_total, combinacion

def calcular_ventana_total(combinacion):
    # Simularemos que cada combinación tiene un inicio y un final, debes ajustar según tus datos reales
    horarios = [(combinacion[i], combinacion[i+1]) for i in range(0, len(combinacion), 2)]  # Simulación
    inicio_minimo = min(h[0] for h in horarios)
    final_maximo = max(h[1] for h in horarios)
    ventana_total = final_maximo - inicio_minimo
    return ventana_total

# Función que genera combinaciones y guarda en la base de datos cada 100,000 combinaciones
def guardar_combinaciones(cursor, combinaciones):
    print("Guardando combinaciones en la base de datos...")
    for comb in combinaciones:
        padded_comb = comb + (None,) * (9 - len(comb))  # Rellenar con None para ajustar a 8 elementos
        cursor.execute('''
        INSERT INTO Obligatorios (curso1_id, curso2_id, curso3_id, curso4_id, curso5_id, curso6_id, curso7_id, curso8_id, curso9_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)
        ''', padded_comb)
    print(f"{len(combinaciones)} combinaciones guardadas.")

def generar_combinaciones(cursos_obligatorios, lista_adicional, solapamientos, max_cursos=9):
    combinaciones_validas = []
    conn = sqlite3.connect('horarios.db')
    cursor = conn.cursor()
    contador = 0

    secciones_por_curso = {sigla: obtener_secciones_por_curso(sigla) for sigla in cursos_obligatorios + lista_adicional}
    print("Generando combinaciones...")

    for num_cursos in range(8, max_cursos + 1):
        for cursos_comb in combinations(cursos_obligatorios + lista_adicional, num_cursos):
            for secciones_comb in product(*[secciones_por_curso[c] for c in cursos_comb]):
                if es_combinacion_valida(secciones_comb, solapamientos):
                    combinaciones_validas.append(secciones_comb)
                    contador += 1
                    if contador % 10000 == 0:
                        print(f"Procesadas {contador} combinaciones")
                    if contador % 100000 == 0:
                        guardar_combinaciones(cursor, combinaciones_validas[-100000:])
                        combinaciones_validas = []  # Limpiar la lista para liberar memoria

    guardar_combinaciones(cursor, combinaciones_validas)
    conn.commit()
    conn.close()
    print("Finalizada la generación de combinaciones.")

def main():
    client = Client(n_workers=8, threads_per_worker=2, memory_limit='3GB')
    print("Dask client setup:", client)

    solapamientos = obtener_solapamientos()
    cursos_obligatorios = ["MAT4140", "PGY4121", "CSY4111", "ASY4131", "FCE1100"]
    lista_adicional = ["INU2101", "MDY2131", "PLC2101", "APY4461"]

    combinaciones = generar_combinaciones(cursos_obligatorios, lista_adicional, solapamientos)
    print("Combinaciones generadas y guardadas.")


"""def procesar_estadisticas_y_ventana(combinacion, solapamientos):
    combinacion_id = combinacion[0]
    datos_de_combinacion = combinacion[1:]

    if es_combinacion_valida(datos_de_combinacion, solapamientos):
        estadisticas = calcular_estadisticas(datos_de_combinacion)
        ventana_total = calcular_ventana_total(datos_de_combinacion)
        return combinacion_id, estadisticas, ventana_total
    return None"""

if __name__ == '__main__':
    main()
