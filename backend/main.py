import mysql.connector
from mysql.connector import Error

def probar_conexion():
    """
    Intenta establecer conexión con la base de datos local en XAMPP.
    """
    try:
        # Configuración de la conexión a tu XAMPP local
        conexion = mysql.connector.connect(
            host='127.0.0.1',
            database='cook_and_share',
            user='root',
            password='' # En XAMPP por defecto la contraseña va vacía
        )

        if conexion.is_connected():
            db_info = conexion.server_info
            print(f"✅ ¡Conexión exitosa al servidor MySQL (Versión {db_info})!")
            print("✅ La base de datos 'cook_and_share' está lista para recibir peticiones.")
            
            # Cerramos la conexión por buenas prácticas
            conexion.close()
            print("🔌 Conexión cerrada correctamente.")

    except Error as e:
        print(f" Error al conectar a la base de datos: {e}")

# Ejecutar la prueba
if __name__ == '__main__':
    print("Iniciando prueba de conexión...")
    probar_conexion()
