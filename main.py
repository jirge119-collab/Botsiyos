# -*- coding: utf-8 -*-

"""
Script principal para un bot de Telegram usando Pyrogram.
"""

# --- Importaciones ---
# Módulos estándar de Python
import logging  # Para registrar información, advertencias y errores.
import time  # Para medir el tiempo de inicio del bot.
from os import getenv  # Para obtener variables de entorno (claves, tokens).
import os
import shutil
import json
import threading

# Módulos de terceros
from dotenv import load_dotenv  # Para cargar variables desde un archivo .env.
from huepy import bad  # Para imprimir mensajes de error con color en la consola.
from pyromod import Client  # Una extensión de Pyrogram para manejar diálogos interactivos.
from pyrogram import filters  # Para filtrar mensajes (ej. por texto, comandos, etc.).
from pyrogram.enums import ParseMode  # Para definir el formato del texto (HTML o Markdown).
from pyrogram.types import CallbackQuery, Message  # Tipos de datos de Pyrogram (mensajes, botones).

# Módulos locales (desde la carpeta 'utils')
from utils.config.functions import (
    bot_on,
    is_maintenance_mode,
)
from utils.config.db import Database
from utils.config.vars import PREFIXES, GATES

# --- Configuración Inicial ---

# Carga las variables de entorno desde el archivo 'assets/.env'.
# Es una buena práctica para mantener las claves seguras y fuera del código.
LOADED_ENV = load_dotenv("./assets/.env")
if not LOADED_ENV:
    # Si el archivo .env no existe, muestra un error y detiene el bot.
    print(bad("Es necesario crear el archivo .env usando .env.example como plantilla."))
    exit(1)

# --- Lectura de Credenciales y Verificación ---

# Lee las credenciales desde las variables de entorno.
API_ID_STR = getenv("API_ID")
API_HASH = getenv("API_HASH")
BOT_TOKEN = getenv("BOT_TOKEN")
CHANNEL_LOGS = getenv("CHANNEL_LOGS")

# Verifica que las credenciales esenciales no estén vacías.
if not all([API_ID_STR, API_HASH, BOT_TOKEN]):
    print(bad("Falta una o más variables de entorno críticas (API_ID, API_HASH, BOT_TOKEN)."))
    print(bad("Asegúrate de que el archivo .env esté completo."))
    exit(1)

# **CORRECCIÓN DEL ERROR**: Convierte el API_ID a un entero.
# El error 'OverflowError' ocurre porque Pyrogram espera un entero, no una cadena de texto.
try:
    API_ID = int(API_ID_STR)
except ValueError:
    print(bad(f"El API_ID '{API_ID_STR}' no es un número entero válido."))
    exit(1)

# --- Inicialización del Cliente de Pyrogram ---

# Crea la instancia principal del bot.
app = Client(
    "bot",  # Nombre de la sesión (se guardará como 'bot.session').
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins"),  # Habilita la carga de módulos desde la carpeta 'plugins'.
    parse_mode=ParseMode.HTML,  # Establece HTML como el modo de formato de texto por defecto.
)

# Llama a una función personalizada al iniciar el bot.
bot_on()

# Configura el sistema de logging para mostrar información útil en la consola.
# Se silencia el logging de 'httpx' para no saturar la consola con detalles de red.
logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.CRITICAL)

# Guarda el momento exacto en que se inicia el script para calcular el tiempo de arranque.
start_time = time.time()


# --- Manejadores de Eventos (Handlers) ---

@app.on_callback_query()
async def warn_user(client: Client, callback_query: CallbackQuery):
    """
    Este manejador se activa cuando un usuario presiona un botón de un teclado inline.
    Su propósito es de seguridad: evita que un usuario 'B' pueda interactuar con
    los botones generados por un comando que ejecutó un usuario 'A'.
    """
    # Comprueba si el mensaje al que responde el botón fue enviado por otro usuario.
    if callback_query.message.reply_to_message.from_user and (
        callback_query.from_user.id
        != callback_query.message.reply_to_message.from_user.id
    ):
        # Si los IDs no coinciden, muestra una alerta y detiene la acción.
        await callback_query.answer("Acceso Denegado ⚠️", show_alert=True)
        return
    # Si el usuario es el correcto, permite que otros manejadores procesen la callback.
    await callback_query.continue_propagation()


@app.on_message(filters.text)
async def user_ban(client: Client, m: Message):
    """
    Este manejador se activa con cada mensaje de texto que recibe el bot.
    Realiza comprobaciones iniciales antes de procesar cualquier comando.
    """
    # Ignora mensajes que no provienen de un usuario (ej. en canales).
    if not m.from_user:
        return

    # Comprueba si el bot está en modo mantenimiento.
    if is_maintenance_mode(m.from_user.id):
        return await m.reply(
            """<b>
━━━━━━━━━━━━━━━━━
[ᛋ] Bot en mantenimiento ⚠️
━━━━━━━━━━━━━━━━━</b>"""
        )

    # Ignora si el mensaje no contiene texto.
    if not m.text:
        return

    # Comprueba si el mensaje comienza con uno de los prefijos definidos (ej. '/', '!', '.').
    # Si no es un comando, lo ignora para no procesar mensajes normales.
    if not m.text[0] in PREFIXES:
        return

    # Usa un 'context manager' para la base de datos.
    # Esto asegura que la conexión se abra y cierre correctamente.
    with Database() as db:
        user_id = m.from_user.id
        username = m.from_user.username

        # Realiza tareas de mantenimiento y comprobaciones de usuario.
        db.remove_expireds_users()
        banned = db.is_ban(user_id)
        if banned:
            # Si el usuario está baneado, no procesa nada más.
            return

        # Si no está baneado, lo registra (o actualiza su info).
        db.register_user(user_id, username)

        # Permite que el mensaje continúe hacia los manejadores de comandos específicos
        # que están en la carpeta 'plugins'.
        await m.continue_propagation()


# --- Punto de Entrada Principal ---

if __name__ == "__main__":
    # Calcula el tiempo que tardó el bot en inicializarse.
    end_time = time.time()
    print(f"\033[94mEl bot tardó {end_time - start_time:.2f} segundos en encender.\033[0m")

    # Inicia el bot. El script se quedará aquí, escuchando nuevos mensajes.
    app.run()
