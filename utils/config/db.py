"""
Este archivo simula la interacción con una base de datos.
La clase `Database` imita la estructura que el bot espera,
permitiendo que el código se ejecute sin una base de datos real.

Puedes reemplazar esta implementación con una conexión a una
base de datos real como SQLite, PostgreSQL, o MongoDB.
"""

class Database:
    def __init__(self):
        """
        El constructor de la clase. En una implementación real,
        aquí se establecería la conexión a la base de datos.
        """
        # print("Simulando: Conexión a la base de datos abierta.")
        pass

    def __enter__(self):
        """
        Permite usar la clase con la declaración 'with'.
        Ej: with Database() as db:
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Se ejecuta al salir del bloque 'with', asegurando que
        los recursos se liberen (ej. cerrar la conexión).
        """
        # print("Simulando: Conexión a la base de datos cerrada.")
        pass

    def remove_expireds_users(self):
        """ Simula la eliminación de usuarios expirados. """
        print("Simulando: Eliminando usuarios expirados de la base de datos.")

    def is_ban(self, user_id: int) -> bool:
        """
        Simula la comprobación de si un usuario está baneado.
        Siempre devuelve False para este ejemplo.
        """
        print(f"Simulando: Comprobando si el usuario {user_id} está baneado. (Resultado: No)")
        return False

    def register_user(self, user_id: int, username: str):
        """ Simula el registro de un nuevo usuario. """
        print(f"Simulando: Registrando al usuario {user_id} (@{username}) en la base de datos.")
