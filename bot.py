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
    """Maneja el comando /start y explica cómo usar /donar."""
    user_id = update.effective_user.id
    if config and user_id in config.get('allowed_user_ids', []):
        await update.message.reply_text("Bot listo. Usa /donar seguido de los datos de la tarjeta para iniciar.")
    else:
        await update.message.reply_text("No tienes permiso para usar este bot.")

async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /donar, procesando los datos de la tarjeta y ejecutando la automatización."""
    user_id = update.effective_user.id
    if not config or user_id not in config.get('allowed_user_ids', []):
        await update.message.reply_text("No tienes permiso para usar este bot.")
        return

    # --- Re-introducir el procesamiento de datos de tarjeta ---
    message_text = update.message.text
    command_text = "/donar"
    cards_text = message_text[len(command_text):].strip()

    if not cards_text:
        await update.message.reply_text("Uso: /donar <numero_tarjeta|mes|año|cvc>")
        return

    # Asumimos una sola tarjeta por comando para simplificar
    parts = [p.strip() for p in cards_text.split('|')]
    if len(parts) != 4:
        await update.message.reply_text("Formato incorrecto. Usa: numero_tarjeta|mes|año|cvc")
        return

    card_info = {
        "card_number": parts[0], "expiry_month": parts[1],
        "expiry_year": parts[2], "cvc": parts[3]
    }

    personal_info = config.get('personal_info')
    if not personal_info:
        await update.message.reply_text("Error: La sección `personal_info` no está configurada en `config.json`.")
        return

    # --- Lógica de la Barra de Progreso ---
    progress_bar_frames = ["[■■□□□□]", "[■■■□□□]", "[■■■■□□]", "[■■■■■□]", "[■■■■■■]"]
    progress_message = await update.message.reply_text(f"Iniciando... {progress_bar_frames[0]}")

    automation_task = asyncio.create_task(perform_donation(personal_info, card_info))

    frame_index = 0
    while not automation_task.done():
        frame_index = (frame_index + 1) % len(progress_bar_frames)
        try:
            await progress_message.edit_text(f"Procesando... {progress_bar_frames[frame_index]}")
        except BadRequest as e:
            if "Message is not modified" not in str(e):
                logger.warning(f"Error al editar mensaje (ignorado): {e}")
        await asyncio.sleep(1.5)

    # --- Procesar el resultado ---
    try:
        success, message = await automation_task
        final_text = f"✅ ¡Éxito!" if success else f"❌ Falló."
        final_text += f"\nMotivo: {message}"
        await progress_message.edit_text(final_text)

        if not success and os.path.exists("post-payment-error.png"):
            await update.message.reply_photo(photo=open("post-payment-error.png", "rb"))

    except Exception as e:
        logger.error(f"Error crítico al procesar el pago: {e}")
        await progress_message.edit_text(f"⚠️ Ocurrió un error inesperado.")


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(f"`{user_id}`", parse_mode='Markdown')

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("pong")

# --- Funciones de Administración (sin cambios) ---
def is_admin(user_id: int) -> bool:
    if not config or not config.get('allowed_user_ids'): return False
    return user_id == config['allowed_user_ids'][0]

def save_config(new_config: dict):
    global config
    with open('config.json', 'w') as f: json.dump(new_config, f, indent=2)
    config = new_config

async def adduser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        new_user_id = int(context.args[0])
        if new_user_id not in config['allowed_user_ids']:
            config['allowed_user_ids'].append(new_user_id)
            save_config(config)
            await update.message.reply_text(f"Usuario {new_user_id} añadido.")
        else:
            await update.message.reply_text("El usuario ya está en la lista.")
    except (IndexError, ValueError):
        await update.message.reply_text("Uso: /adduser <ID>")

async def removeuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        user_to_remove = int(context.args[0])
        if user_to_remove == config['allowed_user_ids'][0]:
            await update.message.reply_text("No puedes eliminar al administrador.")
            return
        if user_to_remove in config['allowed_user_ids']:
            config['allowed_user_ids'].remove(user_to_remove)
            save_config(config)
            await update.message.reply_text(f"Usuario {user_to_remove} eliminado.")
        else:
            await update.message.reply_text("El usuario no se encuentra en la lista.")
    except (IndexError, ValueError):
        await update.message.reply_text("Uso: /removeuser <ID>")

async def listusers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    user_list = "\n".join([f"- `{uid}`" for uid in config.get('allowed_user_ids', [])])
    admin_id = config.get('allowed_user_ids', [None])[0]
    message = f"**Usuarios Autorizados:**\n{user_list}\n\nAdmin: `{admin_id}`"
    await update.message.reply_text(message, parse_mode='Markdown')

async def cmds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_user_admin = is_admin(user_id)
    is_user_allowed = user_id in config.get('allowed_user_ids', [])
    help_text = "📜 **Comandos** 📜\n\n/id\n/ping\n"
    if is_user_allowed: help_text += "/donar <tarjeta|mes|año|cvv>\n"
    if is_user_admin: help_text += "\n--- Admin ---\n/adduser <ID>\n/removeuser <ID>\n/listusers\n"
    help_text += "\n.cmds - Muestra esta ayuda."
    await update.message.reply_text(help_text, parse_mode='Markdown')

# --- Función Principal ---
def main():
    if not config: return
    bot_token = config.get('telegram_bot_token')
    if not bot_token or "AQUI" in bot_token:
        logger.error("Token no configurado en 'config.json'.")
        return

    application = Application.builder().token(bot_token).build()
    handlers = [
        CommandHandler("start", start_command),
        CommandHandler("donar", donate_command),
        CommandHandler("id", id_command),
        CommandHandler("ping", ping_command),
        CommandHandler("adduser", adduser_command),
        CommandHandler("removeuser", removeuser_command),
        CommandHandler("listusers", listusers_command),
        MessageHandler(filters.Regex(r'^\.cmds$'), cmds_command)
    ]
    application.add_handlers(handlers)

    logger.info("El bot se ha iniciado...")
    application.run_polling()

if __name__ == '__main__':
    main()
