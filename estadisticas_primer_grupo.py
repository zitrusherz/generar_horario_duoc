import ray
import cupy as cp
import sqlite3
import logging
import statistics
import numpy as np

# Configuración de logging para trazas detalladas
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ray.init(ignore_reinit_error=True, dashboard_host='0.0.0.0', dashboard_port=8265)

@ray.remote
def calcular_estadisticas_normalizadas_cupy(ventanas, numero_cursos):
    logger.debug(f"Iniciando procesamiento de batch con {len(ventanas)} elementos y {numero_cursos} cursos.")

    if len(ventanas) == 0 or numero_cursos == 0:
        logger.debug("No hay datos disponibles o número de cursos es cero.")
        return None, None, None, None, None, None, None

    # Normalizar ventanas de tiempo por el número de cursos
    datos_normalizados = cp.asnumpy(cp.array(ventanas)) / numero_cursos

    media = float(np.mean(datos_normalizados))
    mediana = float(np.median(datos_normalizados))
    rango = float(np.ptp(datos_normalizados))
    varianza = float(np.var(datos_normalizados))
    desviacion_estandar = float(np.std(datos_normalizados))
    rango_intercuartilico = float(np.percentile(datos_normalizados, 75) - np.percentile(datos_normalizados, 25))

    try:
        moda = float(statistics.mode(datos_normalizados))
    except statistics.StatisticsError:
        moda = None
        logger.debug("Múltiples modas encontradas o ninguna, continuando con moda=None.")

    logger.debug(f"Finalizado procesamiento de batch con resultados: "
                 f"media={media}, mediana={mediana}, moda={moda}, rango={rango}, "
                 f"varianza={varianza}, desviacion_estandar={desviacion_estandar}, "
                 f"rango_intercuartilico={rango_intercuartilico}")
    return media, mediana, moda, rango, varianza, desviacion_estandar, rango_intercuartilico

def obtener_ventanas_y_numero_cursos():
    logger.debug("Conectando a la base de datos y obteniendo datos de Ventanas_Tiempo y Combinaciones.")
    conn = sqlite3.connect('horarios.db')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT vt.ventana_total, 
           (CASE WHEN c.curso1_id IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.curso2_id IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.curso3_id IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.curso4_id IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.curso5_id IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.curso6_id IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.curso7_id IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.curso8_id IS NOT NULL THEN 1 ELSE 0 END) AS numero_cursos
    FROM Ventanas_Tiempo vt
    JOIN Primer_Grupo pg ON vt.combinacion_id = pg.id
    JOIN Combinaciones c ON pg.id = c.id
    """)
    resultados = cursor.fetchall()
    conn.close()
    logger.debug(f"Total de {len(resultados)} registros obtenidos.")
    return [(x[0], x[1]) for x in resultados]  # Extraer valores de ventana_total y numero_cursos

def main():
    logger.info("Iniciando proceso con Ray para Ventanas_Tiempo...")
    datos = obtener_ventanas_y_numero_cursos()
    logger.debug(f"Total de {len(datos)} datos obtenidos.")

    # Dividir en lotes si es necesario para manejar grandes conjuntos de datos
    batch_size = 100000  # Ajustar según la capacidad de la memoria de la GPU
    batches = [(batch[0], batch[1]) for batch in datos]

    futures = [calcular_estadisticas_normalizadas_cupy.remote([ventana_total], numero_cursos) for ventana_total, numero_cursos in batches]

    # Manejo asíncrono de resultados
    resultados_estadisticas = []
    while futures:
        done_ids, futures = ray.wait(futures, num_returns=1)
        for done_id in done_ids:
            resultado = ray.get(done_id)
            if resultado[0] is not None:
                resultados_estadisticas.append(resultado)
            logger.debug(f"Resultados obtenidos de una tarea.")

    # Calcular estadísticas globales de los resultados obtenidos
    todas_ventanas_normalizadas = np.concatenate([np.array([ventana_total]) / numero_cursos for ventana_total, numero_cursos in datos])
    media = np.mean(todas_ventanas_normalizadas)
    mediana = np.median(todas_ventanas_normalizadas)
    rango = np.ptp(todas_ventanas_normalizadas)
    varianza = np.var(todas_ventanas_normalizadas)
    desviacion_estandar = np.std(todas_ventanas_normalizadas)
    rango_intercuartilico = np.percentile(todas_ventanas_normalizadas, 75) - np.percentile(todas_ventanas_normalizadas, 25)

    try:
        moda = statistics.mode(todas_ventanas_normalizadas)
    except statistics.StatisticsError:
        moda = None

    logger.debug(f"Resultados finales: media={media}, mediana={mediana}, moda={moda}, rango={rango}, "
                 f"varianza={varianza}, desviacion_estandar={desviacion_estandar}, "
                 f"rango_intercuartilico={rango_intercuartilico}")

    # Guardar resultados en la base de datos
    conn = sqlite3.connect('horarios.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Estadisticas (
            combinacion_id, media, mediana, moda, rango, varianza, desviacion_estandar, rango_intercuartilico, actualizacion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    ''', (1, media, mediana, moda, rango, varianza, desviacion_estandar, rango_intercuartilico))
    logger.debug("Resultados globales guardados en la base de datos.")

    conn.commit()
    conn.close()
    logger.info("Proceso completado.")

if __name__ == '__main__':
    main()
