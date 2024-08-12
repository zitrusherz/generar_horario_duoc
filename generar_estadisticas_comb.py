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
def calcular_estadisticas_cupy(batch):
    logger.debug(f"Iniciando procesamiento de batch con {len(batch)} elementos.")

    if len(batch) == 0:
        logger.debug("No hay datos disponibles.")
        return None, None, None, None, None, None, None

    # Convertir batch a numpy array antes de operaciones
    datos = cp.asnumpy(cp.array(batch))
    media = float(np.mean(datos))
    mediana = float(np.median(datos))
    rango = float(np.ptp(datos))
    varianza = float(np.var(datos))
    desviacion_estandar = float(np.std(datos))
    rango_intercuartilico = float(np.percentile(datos, 75) - np.percentile(datos, 25))

    try:
        moda = float(statistics.mode(datos))
    except statistics.StatisticsError:
        moda = None
        logger.debug("Múltiples modas encontradas o ninguna, continuando con moda=None.")

    logger.debug(f"Finalizado procesamiento de batch con resultados: "
                 f"media={media}, mediana={mediana}, moda={moda}, rango={rango}, "
                 f"varianza={varianza}, desviacion_estandar={desviacion_estandar}, "
                 f"rango_intercuartilico={rango_intercuartilico}")
    return media, mediana, moda, rango, varianza, desviacion_estandar, rango_intercuartilico


def obtener_ventanas_totales():
    logger.debug("Conectando a la base de datos y obteniendo datos.")
    conn = sqlite3.connect('horarios.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ventana_total FROM Ventanas_Tiempo")
    resultados = cursor.fetchall()
    conn.close()
    logger.debug(f"Total de {len(resultados)} registros obtenidos.")
    return [x[0] for x in resultados]  # Extraer solo los valores de ventana_total


def main():
    logger.info("Iniciando proceso con Ray...")
    ventanas_totales = obtener_ventanas_totales()
    logger.debug(f"Total de {len(ventanas_totales)} ventanas obtenidas.")

    # Dividir en lotes si es necesario para manejar grandes conjuntos de datos
    batch_size = 100000  # Ajustar según la capacidad de la memoria de la GPU
    batches = [ventanas_totales[i:i + batch_size] for i in range(0, len(ventanas_totales), batch_size)]

    futures = [calcular_estadisticas_cupy.remote(batch) for batch in batches]

    # Manejo asíncrono de resultados
    resultados_estadisticas = []
    while futures:
        done_ids, futures = ray.wait(futures, num_returns=1)
        for done_id in done_ids:
            resultado = ray.get(done_id)
            if resultado[0] is not None:
                resultados_estadisticas.append(resultado)
            logger.debug(f"Resultados obtenidos de una tarea.")

    # Eliminar datos existentes en la tabla Estadisticas
    conn = sqlite3.connect('horarios.db')
    cursor = conn.cursor()
    logger.debug("Eliminando datos existentes de la tabla Estadisticas.")
    cursor.execute("DELETE FROM Estadisticas")
    conn.commit()

    # Calcular estadísticas globales de los resultados obtenidos
    todas_ventanas = np.concatenate([np.array(batch) for batch in batches])
    media = np.mean(todas_ventanas)
    mediana = np.median(todas_ventanas)
    rango = np.ptp(todas_ventanas)
    varianza = np.var(todas_ventanas)
    desviacion_estandar = np.std(todas_ventanas)
    rango_intercuartilico = np.percentile(todas_ventanas, 75) - np.percentile(todas_ventanas, 25)

    try:
        moda = statistics.mode(todas_ventanas)
    except statistics.StatisticsError:
        moda = None

    logger.debug(f"Resultados finales: media={media}, mediana={mediana}, moda={moda}, rango={rango}, "
                 f"varianza={varianza}, desviacion_estandar={desviacion_estandar}, "
                 f"rango_intercuartilico={rango_intercuartilico}")

    # Guardar resultados en la base de datos
    cursor.execute('''
        INSERT OR REPLACE INTO Estadisticas (
            combinacion_id, media, mediana, moda, rango, varianza, desviacion_estandar, rango_intercuartilico, actualizacion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    ''', (0, media, mediana, moda, rango, varianza, desviacion_estandar, rango_intercuartilico))
    logger.debug("Resultados globales guardados en la base de datos.")

    conn.commit()
    conn.close()
    logger.info("Proceso completado.")


if __name__ == '__main__':
    main()
