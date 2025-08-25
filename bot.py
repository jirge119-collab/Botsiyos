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
        await update.message.reply_text("Bot de pago recurrente listo. Usa /donar para iniciar.")
    else:
        await update.message.reply_text("No tienes permiso para usar este bot.")

async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /donar, mostrando una barra de progreso animada."""
    user_id = update.effective_user.id
    if not config or user_id not in config.get('allowed_user_ids', []):
        await update.message.reply_text("No tienes permiso para usar este bot.")
        return

    # --- Lógica de la Barra de Progreso ---
    progress_bar_frames = [
        "[          ]",
        "[■         ]",
        "[■■        ]",
        "[■■■       ]",
        "[■■■■      ]",
        "[■■■■■     ]",
        "[■■■■■■    ]",
        "[■■■■■■■   ]",
        "[■■■■■■■■  ]",
        "[■■■■■■■■■ ]",
        "[■■■■■■■■■■]"
    ]

    # Enviar mensaje inicial
    progress_message = await update.message.reply_text(f"Iniciando... {progress_bar_frames[0]}")

    # Crear y ejecutar la tarea de automatización en segundo plano
    automation_task = asyncio.create_task(perform_donation())

    # Animar la barra de progreso mientras la tarea se ejecuta
    frame_index = 0
    while not automation_task.done():
        frame_index = (frame_index + 1) % len(progress_bar_frames)
        try:
            await progress_message.edit_text(f"Procesando pago... {progress_bar_frames[frame_index]}")
        except BadRequest as e:
            if "Message is not modified" not in str(e):
                logger.warning(f"Error al editar mensaje (ignorado): {e}")
        await asyncio.sleep(1) # Editar el mensaje cada segundo

    # --- Procesar el resultado de la tarea ---
    try:
        success, message = await automation_task
        if success:
            final_text = f"✅ ¡Pago exitoso!\nMotivo: {message}"
            await progress_message.edit_text(final_text)
        else:
            final_text = f"❌ Falló el pago.\nMotivo: {message}"
            await progress_message.edit_text(final_text)
            if os.path.exists("post-payment-error.png"):
                await update.message.reply_photo(
                    photo=open("post-payment-error.png", "rb"),
                    caption="Captura de pantalla del error."
                )
    except Exception as e:
        logger.error(f"Error crítico al procesar el pago: {e}")
        await progress_message.edit_text(f"⚠️ Ocurrió un error inesperado. Revisa los logs del bot.")


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Un comando público para que cualquier usuario pueda obtener su ID de Telegram."""
    user_id = update.effective_user.id
    await update.message.reply_text(f"Tu ID de usuario de Telegram es: `{user_id}`")


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde con 'pong' para verificar que el bot está activo."""
    await update.message.reply_text("pong")


# --- Funciones de Administración ---

def is_admin(user_id: int) -> bool:
    """Verifica si el user_id es el del administrador (el primero en la lista)."""
    if not config or not config.get('allowed_user_ids'): return False
    return user_id == config['allowed_user_ids'][0]

def save_config(new_config: dict):
    """Guarda la configuración actualizada en el archivo config.json."""
    global config
    with open('config.json', 'w') as f:
        json.dump(new_config, f, indent=2)
    config = new_config

async def adduser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Este comando solo puede ser usado por el administrador.")
        return
    try:
        new_user_id = int(context.args[0])
        if new_user_id not in config['allowed_user_ids']:
            config['allowed_user_ids'].append(new_user_id)
            save_config(config)
            await update.message.reply_text(f"Usuario {new_user_id} añadido.")
        else:
            await update.message.reply_text("El usuario ya está en la lista.")
    except (IndexError, ValueError):
        await update.message.reply_text("Uso: /adduser <ID_del_usuario>")

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
        await update.message.reply_text("Uso: /removeuser <ID_del_usuario>")

async def listusers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    user_list = "\n".join([f"- `{uid}`" for uid in config.get('allowed_user_ids', [])])
    admin_id = config.get('allowed_user_ids', [None])[0]
    message = f"**Usuarios Autorizados:**\n{user_list}\n\nEl administrador es: `{admin_id}`"
    await update.message.reply_text(message, parse_mode='Markdown')

async def cmds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_user_admin = is_admin(user_id)
    is_user_allowed = user_id in config.get('allowed_user_ids', [])
    help_text = "📜 **Comandos Disponibles** 📜\n\n/id - Muestra tu ID.\n/ping - Verifica si el bot está activo.\n"
    if is_user_allowed: help_text += "/donar - Inicia el pago recurrente.\n"
    if is_user_admin: help_text += "\n--- Admin ---\n/adduser <ID>\n/removeuser <ID>\n/listusers\n"
    help_text += "\n.cmds - Muestra esta ayuda."
    await update.message.reply_text(help_text, parse_mode='Markdown')

# --- Función Principal ---
def main():
    if not config: return
    bot_token = config.get('telegram_bot_token')
    if not bot_token or bot_token == "AQUI_VA_TU_TOKEN_DE_TELEGRAM":
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
