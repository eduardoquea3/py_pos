import os
from dotenv import load_dotenv
from psycopg2 import pool
from psycopg2.extras import DictCursor

load_dotenv()


class DatabaseEngine:
    def __init__(self, minconn=1, maxconn=5):
        self.config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "database": os.getenv("DB_NAME", "mi_basededatos"),
            "user": os.getenv("DB_USER", "mi_usuario"),
            "password": os.getenv("DB_PASSWORD", "mi_contraseña"),
        }
        self.minconn = minconn
        self.maxconn = maxconn
        self.pool = None

    def create_engine(self):
        try:
            self.pool = pool.SimpleConnectionPool(
                self.minconn, self.maxconn, **self.config
            )
            if self.pool:
                print("Engine creado exitosamente.")
            return self.pool
        except Exception as error:
            print("Error al crear engine de la base de datos:", error)
            return None

    def get_connection(self):
        try:
            if self.pool:
                conn = self.pool.getconn()
                if conn:
                    print("Conexión obtenida del pool.")
                    return conn
            print("El pool no está inicializado.")
            return None
        except Exception as error:
            print("Error al obtener conexión:", error)
            return None

    def return_connection(self, conn):
        try:
            if self.pool:
                self.pool.putconn(conn)
                print("Conexión retornada al pool.")
        except Exception as error:
            print("Error al retornar conexión:", error)

    def close_engine(self):
        try:
            if self.pool:
                self.pool.closeall()
                print("Engine cerrado. Todas las conexiones han sido liberadas.")
        except Exception as error:
            print("Error al cerrar engine:", error)

    def execute_procedure(self, proc_name, params=None, fetch=True):
        """
        Ejecuta un procedimiento almacenado en PostgreSQL.

        :param proc_name: Nombre del procedimiento a ejecutar.
        :param params: Tupla o lista de parámetros que se pasarán al procedimiento.
        :param fetch: Si True, se intentará obtener los resultados.
        :return: Los resultados obtenidos si fetch es True; de lo contrario, None.
        """
        conn = self.get_connection()
        if not conn:
            print("No se pudo obtener una conexión para ejecutar el procedimiento.")
            return None

        try:
            cursor = conn.cursor(cursor_factory=DictCursor)
            cursor.callproc(proc_name, params if params else [])
            result = None
            if fetch:
                try:
                    result = cursor.fetchall()
                except Exception:
                    # Si no hay resultados o no es aplicable fetch
                    result = None
            conn.commit()
            print(f"Procedimiento '{proc_name}' ejecutado exitosamente.")
            return result
        except Exception as error:
            print(f"Error al ejecutar el procedimiento '{proc_name}':", error)
            conn.rollback()
            return None
        finally:
            cursor.close()
            self.return_connection(conn)
