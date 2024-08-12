import sqlite3
from tqdm import tqdm
from dask import delayed, compute
from dask.distributed import Client


def obtener_ventanas_entre_secciones(seccion_ids):
    conn = sqlite3.connect('horarios.db')
    cursor = conn.cursor()

    placeholders = ','.join('?' for _ in seccion_ids)
    query = f'''
        SELECT seccion1_id, seccion2_id, ventana_tiempo
        FROM Ventana_Tiempo
        WHERE seccion1_id IN ({placeholders}) AND seccion2_id IN ({placeholders})
    '''
    cursor.execute(query, seccion_ids + seccion_ids)
    ventanas = cursor.fetchall()

    conn.close()
    return ventanas


def calcular_ventana_total(combinacion):
    ventanas = obtener_ventanas_entre_secciones(combinacion)
    ventana_total = 0
    solapamiento = False

    for seccion1_id, seccion2_id, ventana_tiempo in ventanas:
        if ventana_tiempo < 0:
            solapamiento = True
        ventana_total += max(ventana_tiempo, 0)

    return combinacion[0], ventana_total, solapamiento


def guardar_resultados(cursor, resultados):
    for combinacion_id, ventana_total, solapamiento in resultados:
        cursor.execute('''
            INSERT INTO Ventanas_Tiempo (combinacion_id, ventana_total, solapamiento)
            VALUES (?, ?, ?)
        ''', (combinacion_id, ventana_total, solapamiento))


def main():
    client = Client(n_workers=8,
                    threads_per_worker=2,
                    memory_limit='2GB')
    print("Dask client setup:", client)

    conn = sqlite3.connect('horarios.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Combinaciones")
    todas_las_combinaciones = cursor.fetchall()

    delayed_results = [delayed(calcular_ventana_total)(combinacion) for combinacion in todas_las_combinaciones]

    batch_size = 50000
    total_combinaciones = len(delayed_results)

    for i in range(0, total_combinaciones, batch_size):
        batch = delayed_results[i:i + batch_size]
        with tqdm(total=len(batch), desc=f'Procesando lote {i // batch_size + 1}') as pbar:
            results = compute(*batch)
            pbar.update(len(batch))

        guardar_resultados(cursor, results)
        conn.commit()

    conn.close()
    print("Proceso completado.")


if __name__ == '__main__':
    main()
