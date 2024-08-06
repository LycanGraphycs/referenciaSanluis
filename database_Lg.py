import mysql.connector
from mysql.connector import Error


def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="ADMIN",
            password="sanluis2024*",
            database="referenciaSl_db"
        )
        print("Conexión a MySQL exitosa")
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")

    return connection


def obtener_diagnosticos():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT nombre FROM diagnosticos")
    resultados = cursor.fetchall()
    cursor.close()
    connection.close()
    return [row[0] for row in resultados]
