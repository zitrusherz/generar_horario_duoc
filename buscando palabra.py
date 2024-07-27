import cx_Oracle
import os


os.environ['TNS_ADMIN'] = 'B:/Wallet_DBZitrico'
user = 'ADMIN'
password = 'Heidegger22!'
dsn = 'g3b4e1e1d9023f8_dbzitrico_high.adb.oraclecloud.com'
try:
    print(cx_Oracle.clientversion())
except cx_Oracle.DatabaseError as e:
    print(f"Error: {e}")
try:
    # Establecer la conexión
    connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)
    print("Conexión establecida exitosamente")
except cx_Oracle.DatabaseError as e:
    print(f"Error al conectar a la base de datos: {e}")
finally:
    if connection:
        connection.close()
        print("Conexión cerrada")