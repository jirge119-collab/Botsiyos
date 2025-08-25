import json
import logging
import os
import asyncio
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Importar la función de automatización
from automation import perform_donation

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Carga de Configuración ---
def load_config():
    """Carga la configuración desde config.json."""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Error: 'config.json' no encontrado. Por favor, crea uno a partir de 'config.json.template'.")
        return None
    except json.JSONDecodeError:
        logger.error("Error: 'config.json' tiene un formato incorrecto.")
        return None

config = load_config()

# --- Funciones de Comandos del Bot ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando .start y da la bienvenida."""
    user_id = update.effective_user.id
    if config and user_id in config.get('allowed_user_ids', []):
        await update.message.reply_text("Bot de donación v2.5 listo. Escribe .cmds para ver los comandos.")
    else:
        await update.message.reply_text("No tienes permiso para usar este bot.")

async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando .donar, que inicia el proceso de donación con las tarjetas guardadas."""
    user_id = update.effective_user.id
    if not config or user_id not in config.get('allowed_user_ids', []):
        await update.message.reply_text("No tienes permiso para usar este bot.")
        return

    if not config.get('credit_cards'):
        await update.message.reply_text("No hay tarjetas de crédito configuradas en `config.json`.")
        return

    await update.message.reply_text(f"Iniciando proceso de donación con {len(config['credit_cards'])} tarjeta(s)...")

    # Llamar a la función de automatización con toda la configuración
    success, message, screenshot_paths = await perform_donation(config)

    if success:
        await update.message.reply_text(f"✅ ¡Éxito! {message}")
    else:
        await update.message.reply_text(f"❌ Fallo. {message}")
        if screenshot_paths:
            await update.message.reply_text("Se generaron los siguientes informes de error:")
            for path in screenshot_paths:
                if os.path.exists(path):
                    await update.message.reply_photo(photo=open(path, "rb"))
                    os.remove(path) # Limpiar después de enviar

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Devuelve el ID de usuario de Telegram."""
    user_id = update.effective_user.id
    await update.message.reply_text(f"Tu ID de Telegram es: `{user_id}`", parse_mode='Markdown')

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde con 'pong'."""
    await update.message.reply_text("pong")

# --- Funciones de Administración ---
def is_admin(user_id: int) -> bool:
    """Verifica si un ID de usuario corresponde al administrador."""
    if not config or not config.get('allowed_user_ids'): return False
    return user_id == config['allowed_user_ids'][0]

def save_config(new_config: dict):
    """Guarda la configuración actualizada en config.json."""
    global config
    with open('config.json', 'w') as f: json.dump(new_config, f, indent=2)
    config = new_config
    logger.info("La configuración ha sido guardada.")

async def adduser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Añade un nuevo usuario a la lista de permitidos (solo admin)."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("No tienes permisos de administrador.")
        return

    try:
        # Extraer el ID del mensaje, que viene después del comando
        new_user_id = int(update.message.text.split()[1])
        if new_user_id not in config['allowed_user_ids']:
            config['allowed_user_ids'].append(new_user_id)
            save_config(config)
            await update.message.reply_text(f"Usuario `{new_user_id}` añadido correctamente.", parse_mode='Markdown')
        else:
            await update.message.reply_text("Ese usuario ya estaba autorizado.")
    except (IndexError, ValueError):
        await update.message.reply_text("Uso: `.adduser <ID_de_usuario>`")

async def listusers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista todos los usuarios autorizados (solo admin)."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("No tienes permisos de administrador.")
        return

    user_list = "\n".join([f"- `{uid}`" for uid in config.get('allowed_user_ids', [])])
    admin_id = config.get('allowed_user_ids', [None])[0]
    message = f"**Usuarios Autorizados:**\n{user_list}\n\nEl administrador es: `{admin_id}`"
    await update.message.reply_text(message, parse_mode='Markdown')

async def cmds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra la lista de comandos disponibles."""
    user_id = update.effective_user.id
    is_user_admin = is_admin(user_id)
    is_user_allowed = user_id in config.get('allowed_user_ids', [])

    help_text = "📜 **Comandos Disponibles** 📜\n\n"
    help_text += "`.ping` - Comprueba si el bot está vivo.\n"
    help_text += "`.id` - Muestra tu ID de Telegram.\n"

    if is_user_allowed:
        help_text += "`.donar` - Inicia el proceso de donación con las tarjetas guardadas.\n"

    if is_user_admin:
        help_text += "\n--- Comandos de Administrador ---\n"
        help_text += "`.adduser <ID>` - Autoriza a un nuevo usuario.\n"
        help_text += "`.listusers` - Muestra los usuarios autorizados.\n"

    help_text += "\n`.cmds` - Muestra esta ayuda."
    await update.message.reply_text(help_text, parse_mode='Markdown')

# --- Función Principal ---
def main():
    if not config: return
    bot_token = config.get('telegram_bot_token')
    if not bot_token or "AQUI" in bot_token:
        logger.error("Token no configurado en 'config.json'. Revisa el archivo.")
        return

    application = Application.builder().token(bot_token).build()

    # Registrar comandos usando MessageHandler con Regex para el prefijo '.'
    handlers = [
        MessageHandler(filters.Regex(r'^\.start$'), start_command),
        MessageHandler(filters.Regex(r'^\.donar$'), donate_command),
        MessageHandler(filters.Regex(r'^\.id$'), id_command),
        MessageHandler(filters.Regex(r'^\.ping$'), ping_command),
        MessageHandler(filters.Regex(r'^\.adduser(\s+\d+)?$'), adduser_command),
        MessageHandler(filters.Regex(r'^\.listusers$'), listusers_command),
        MessageHandler(filters.Regex(r'^\.cmds$'), cmds_command)
    ]
    application.add_handlers(handlers)

    logger.info("Bot iniciado. Escuchando comandos con prefijo '.'")
    application.run_polling()

if __name__ == '__main__':
    main()
