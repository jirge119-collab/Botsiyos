"""
Este archivo contiene funciones de utilidad que pueden ser
reutilizadas a lo largo del código del bot.
"""

def bot_on():
    """
    Una función simple que se llama cuando el bot se inicia.
    Puedes expandirla para que realice comprobaciones iniciales.
    """
    print("El bot se está encendiendo...")


def is_maintenance_mode(user_id: int) -> bool:
    """
    Comprueba si el bot está en modo de mantenimiento.
    Actualmente, siempre devuelve False (desactivado).

    Puedes modificar esta lógica para que, por ejemplo,
    solo los administradores puedan usar el bot mientras está
    en mantenimiento.

    Args:
        user_id (int): El ID del usuario que interactúa con el bot.

    Returns:
        bool: True si el mantenimiento está activado, False en caso contrario.
    """
    # Lógica de ejemplo: El mantenimiento nunca está activo.
    return False
