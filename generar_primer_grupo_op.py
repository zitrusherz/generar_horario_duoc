import sqlite3
import logging

# Configuración de logging para trazas detalladas
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Conexión a la base de datos
def conectar_bd():
    return sqlite3.connect('horarios.db')


# Obtener combinaciones sin solapamientos y con ventana_total <= mediana
def obtener_combinaciones_sin_solapamientos(mediana):
    conn = conectar_bd()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT DISTINCT c.*
    FROM Ventanas_Tiempo vt
    JOIN Combinaciones c ON vt.combinacion_id = c.id
    WHERE vt.ventana_total <= ? AND vt.solapamiento = 0
    """, (mediana,))
    combinaciones = cursor.fetchall()

    conn.close()
    return combinaciones


# Crear la tabla Primer_Grupo con la misma estructura que Combinaciones
def crear_tabla_primer_grupo():
    conn = conectar_bd()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Primer_Grupo (
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
    logger.debug("Tabla Primer_Grupo creada o existente.")


# Insertar combinaciones válidas en la tabla Primer_Grupo
def insertar_en_primer_grupo(combinaciones):
    conn = conectar_bd()
    cursor = conn.cursor()

    cursor.executemany("""
    INSERT INTO Primer_Grupo (id, curso1_id, curso2_id, curso3_id, curso4_id, curso5_id, curso6_id, curso7_id, curso8_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, combinaciones)

    conn.commit()
    conn.close()
    logger.info("Combinaciones válidas insertadas en Primer_Grupo.")


def main():
    logger.info("Iniciando proceso de clasificación de combinaciones.")

    # Definir la mediana ya calculada
    mediana = 1080.0

    # Obtener combinaciones válidas
    combinaciones_validas = obtener_combinaciones_sin_solapamientos(mediana)
    logger.info(
        f"Total de combinaciones sin solapamientos y con ventana_total <= {mediana}: {len(combinaciones_validas)}")

    # Crear la tabla Primer_Grupo
    crear_tabla_primer_grupo()

    # Insertar combinaciones válidas en Primer_Grupo
    insertar_en_primer_grupo(combinaciones_validas)
    logger.info("Proceso completado.")


if __name__ == '__main__':
    main()
