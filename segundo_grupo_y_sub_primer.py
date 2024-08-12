import sqlite3
import logging

# Configuración de logging para trazas detalladas
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Conexión a la base de datos
def conectar_bd():
    return sqlite3.connect('horarios.db')


# Obtener combinaciones del Primer_Grupo según las condiciones
def obtener_combinaciones_filtradas(mediana, condicion_adicional=False):
    conn = conectar_bd()
    cursor = conn.cursor()

    # Query base
    query = """
    SELECT pg.id, pg.curso1_id, pg.curso2_id, pg.curso3_id, pg.curso4_id, pg.curso5_id, pg.curso6_id, pg.curso7_id, pg.curso8_id
    FROM Ventanas_Tiempo vt
    JOIN Primer_Grupo pg ON vt.combinacion_id = pg.id
    WHERE vt.ventana_total >= ?
    """

    # Agregar condiciones adicionales si es necesario
    if condicion_adicional:
        query += " AND pg.curso6_id = 46 AND pg.curso7_id BETWEEN 1 AND 9"
        logger.debug("Aplicando condiciones adicionales: curso6_id = 46 AND curso7_id BETWEEN 1 AND 9")

    logger.debug(f"Ejecutando consulta: {query}")
    cursor.execute(query, (mediana,))
    combinaciones = cursor.fetchall()

    if not combinaciones:
        logger.warning(
            f"No se encontraron combinaciones para las condiciones dadas (mediana <= {mediana}, condiciones adicionales = {condicion_adicional})")

    conn.close()
    return combinaciones


# Crear tabla Segundo_Grupo
def crear_tabla_segundo_grupo():
    conn = conectar_bd()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Segundo_Grupo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        curso1_id INTEGER REFERENCES Seccion,
        curso2_id INTEGER REFERENCES Seccion,
        curso3_id INTEGER REFERENCES Seccion,
        curso4_id INTEGER REFERENCES Seccion,
        curso5_id INTEGER REFERENCES Seccion,
        curso6_id INTEGER REFERENCES Seccion,
        curso7_id INTEGER REFERENCES Seccion,
        curso8_id INTEGER REFERENCES Seccion
    );
    """)

    conn.commit()
    conn.close()
    logger.debug("Tabla Segundo_Grupo creada o existente.")


# Crear tabla Sub_Primer_Grupo
def crear_tabla_sub_primer_grupo():
    conn = conectar_bd()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Sub_Primer_Grupo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        curso1_id INTEGER REFERENCES Seccion,
        curso2_id INTEGER REFERENCES Seccion,
        curso3_id INTEGER REFERENCES Seccion,
        curso4_id INTEGER REFERENCES Seccion,
        curso5_id INTEGER REFERENCES Seccion,
        curso6_id INTEGER REFERENCES Seccion,
        curso7_id INTEGER REFERENCES Seccion,
        curso8_id INTEGER REFERENCES Seccion
    );
    """)

    conn.commit()
    conn.close()
    logger.debug("Tabla Sub_Primer_Grupo creada o existente.")


# Insertar combinaciones en una tabla específica
def insertar_en_tabla_combinaciones(combinaciones, nombre_tabla):
    conn = conectar_bd()
    cursor = conn.cursor()

    cursor.executemany(f"""
    INSERT INTO {nombre_tabla} (id, curso1_id, curso2_id, curso3_id, curso4_id, curso5_id, curso6_id, curso7_id, curso8_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, combinaciones)

    conn.commit()
    conn.close()
    logger.info(f"Combinaciones insertadas en {nombre_tabla}.")


def main():
    logger.info("Iniciando proceso de clasificación de combinaciones.")

    # Definir la mediana ya calculada
    mediana = 119.2

    # Obtener combinaciones válidas para Segundo_Grupo
    combinaciones_segundo_grupo = obtener_combinaciones_filtradas(mediana)
    logger.info(f"Total de combinaciones en Segundo_Grupo: {len(combinaciones_segundo_grupo)}")

    # Obtener combinaciones válidas para Sub_Primer_Grupo
    combinaciones_sub_primer_grupo = obtener_combinaciones_filtradas(mediana, condicion_adicional=True)
    logger.info(f"Total de combinaciones en Sub_Primer_Grupo: {len(combinaciones_sub_primer_grupo)}")

    # Crear las tablas necesarias
    crear_tabla_segundo_grupo()
    crear_tabla_sub_primer_grupo()

    # Insertar combinaciones en las tablas correspondientes
    insertar_en_tabla_combinaciones(combinaciones_segundo_grupo, "Segundo_Grupo")
    insertar_en_tabla_combinaciones(combinaciones_sub_primer_grupo, "Sub_Primer_Grupo")

    logger.info("Proceso completado.")


if __name__ == '__main__':
    main()
