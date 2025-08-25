import json
import logging
import os
from telegram import Update
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
        await update.message.reply_text(
            "¡Hola! Soy tu bot de donaciones v2. 👋\n\n"
            "Para iniciar una donación, usa el comando /donar seguido de los datos de tus tarjetas, una por línea.\n\n"
            "El formato para cada tarjeta es: `numero|mes|año|cvc`\n\n"
            "**Ejemplo de uso:**\n"
            "```\n"
            "/donar\n"
            "1111222233334444|12|2028|123\n"
            "5555666677778888|06|2027|456\n"
            "```"
        )
    else:
        logger.warning(f"Acceso no autorizado denegado al usuario con ID: {user_id}")
        await update.message.reply_text("No tienes permiso para usar este bot.")

async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /donar, que procesa las tarjetas y ejecuta la donación."""
    user_id = update.effective_user.id
    if not config or user_id not in config.get('allowed_user_ids', []):
        await update.message.reply_text("No tienes permiso para usar este bot.")
        return

    # Extraer el texto que viene después del comando /donar
    message_text = update.message.text
    command_text = "/donar"
    cards_text = message_text[len(command_text):].strip()

    if not cards_text:
        await update.message.reply_text(
            "Por favor, proporciona los datos de las tarjetas después del comando /donar.\n\n"
            "Ejemplo:\n"
            "```\n"
            "/donar\n"
            "1111222233334444|12|2028|123\n"
            "```"
        )
        return

    # Procesar cada línea como una tarjeta
    lines = cards_text.split('\n')
    cards_to_process = []
    for line in lines:
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split('|')]
        if len(parts) == 4:
            card_info = {
                "card_number": parts[0],
                "expiry_month": parts[1],
                "expiry_year": parts[2],
                "cvc": parts[3]
            }
            cards_to_process.append(card_info)
        else:
            await update.message.reply_text(f"⚠️ Línea ignorada por formato incorrecto: `{line}`")

    if not cards_to_process:
        await update.message.reply_text("No se encontraron tarjetas válidas en tu mensaje. Asegúrate de usar el formato: `numero|mes|año|cvc`")
        return

    personal_info = config.get('personal_info')
    if not personal_info:
        await update.message.reply_text("Error: La sección `personal_info` no está configurada en `config.json`.")
        return

    await update.message.reply_text(f"Iniciando proceso de donación con {len(cards_to_process)} tarjeta(s)... 🚀")

    donation_successful = False
    for i, card in enumerate(cards_to_process):
        card_nickname = f"Tarjeta #{i + 1} (terminada en {card['card_number'][-4:]})"
        await update.message.reply_text(f"💳 Intentando con {card_nickname}...")

        try:
            success, message = await perform_donation(personal_info, card)
            if success:
                await update.message.reply_text(f"✅ ¡Donación exitosa con {card_nickname}!\nMotivo: {message}")
                donation_successful = True
                break
            else:
                await update.message.reply_text(f"❌ Falló la donación con {card_nickname}.\nMotivo: {message}")
                # Enviar captura de pantalla si existe
                if os.path.exists("post-payment-error.png"):
                    await update.message.reply_photo(
                        photo=open("post-payment-error.png", "rb"),
                        caption="Captura de pantalla del error."
                    )

        except Exception as e:
            logger.error(f"Error crítico al procesar {card_nickname}: {e}")
            await update.message.reply_text(f"⚠️ Ocurrió un error inesperado con {card_nickname}. Revisa los logs del bot.")

    if not donation_successful:
        await update.message.reply_text("🛑 Proceso finalizado. Ninguna de las tarjetas pudo completar la donación.")


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Un comando público para que cualquier usuario pueda obtener su ID de Telegram."""
    user_id = update.effective_user.id
    await update.message.reply_text(f"Tu ID de usuario de Telegram es: `{user_id}`")


# --- Funciones de Administración ---

def is_admin(user_id: int) -> bool:
    """Verifica si el user_id es el del administrador (el primero en la lista)."""
    if not config:
        return False
    admin_id = config.get('allowed_user_ids', [])[0]
    return user_id == admin_id

def save_config(new_config: dict):
    """Guarda la configuración actualizada en el archivo config.json."""
    global config
    with open('config.json', 'w') as f:
        json.dump(new_config, f, indent=2)
    config = new_config # Actualizar la configuración en memoria

async def adduser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando de admin para añadir un nuevo usuario autorizado."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Este comando solo puede ser usado por el administrador.")
        return

    try:
        new_user_id = int(context.args[0])
        if new_user_id not in config['allowed_user_ids']:
            new_config = config.copy()
            new_config['allowed_user_ids'].append(new_user_id)
            save_config(new_config)
            await update.message.reply_text(f"Usuario {new_user_id} añadido exitosamente.")
        else:
            await update.message.reply_text(f"El usuario {new_user_id} ya está en la lista.")
    except (IndexError, ValueError):
        await update.message.reply_text("Uso: /adduser <ID_del_usuario>")

async def removeuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando de admin para quitar a un usuario autorizado."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Este comando solo puede ser usado por el administrador.")
        return

    try:
        user_to_remove = int(context.args[0])
        if user_to_remove == config['allowed_user_ids'][0]:
            await update.message.reply_text("No puedes eliminar al administrador.")
            return

        if user_to_remove in config['allowed_user_ids']:
            new_config = config.copy()
            new_config['allowed_user_ids'].remove(user_to_remove)
            save_config(new_config)
            await update.message.reply_text(f"Usuario {user_to_remove} eliminado exitosamente.")
        else:
            await update.message.reply_text(f"El usuario {user_to_remove} no se encuentra en la lista.")
    except (IndexError, ValueError):
        await update.message.reply_text("Uso: /removeuser <ID_del_usuario>")

async def listusers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando de admin para listar todos los usuarios autorizados."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Este comando solo puede ser usado por el administrador.")
        return

    user_list = "\n".join([f"- `{uid}`" for uid in config.get('allowed_user_ids', [])])
    admin_id = config.get('allowed_user_ids', [None])[0]
    message = f"**Lista de Usuarios Autorizados:**\n{user_list}\n\nEl administrador es: `{admin_id}`"
    await update.message.reply_text(message, parse_mode='Markdown')


async def cmds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra una lista de todos los comandos disponibles."""
    user_id = update.effective_user.id
    is_user_admin = is_admin(user_id)
    is_user_allowed = user_id in config.get('allowed_user_ids', [])

    # Construir el mensaje de ayuda
    help_text = "📜 **Comandos Disponibles** 📜\n\n"
    help_text += "**/id** - Muestra tu ID de usuario de Telegram.\n\n"

    if is_user_allowed:
        help_text += "**/donar** - Inicia el proceso de donación.\n_(Debes pasar los datos de la tarjeta en el mensaje)_\n\n"

    if is_user_admin:
        help_text += "--- **Comandos de Administrador** ---\n"
        help_text += "**/adduser <ID>** - Autoriza a un nuevo usuario.\n"
        help_text += "**/removeuser <ID>** - Revoca el acceso a un usuario.\n"
        help_text += "**/listusers** - Muestra la lista de usuarios autorizados.\n"

    help_text += "\n**.cmds** - Muestra este mensaje de ayuda."

    await update.message.reply_text(help_text, parse_mode='Markdown')


# --- Función Principal ---
def main():
    """Inicia el bot de Telegram."""
    if not config:
        return

    bot_token = config.get('telegram_bot_token')
    if not bot_token or bot_token == "AQUI_VA_TU_TOKEN_DE_TELEGRAM":
        logger.error("El token del bot de Telegram no está configurado en 'config.json'.")
        return

    application = Application.builder().token(bot_token).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("donar", donate_command))
    application.add_handler(CommandHandler("id", id_command))
    application.add_handler(CommandHandler("adduser", adduser_command))
    application.add_handler(CommandHandler("removeuser", removeuser_command))
    application.add_handler(CommandHandler("listusers", listusers_command))
    application.add_handler(MessageHandler(filters.Regex(r'^\.cmds$'), cmds_command))

    logger.info("El bot se ha iniciado y está escuchando...")
    application.run_polling()

if __name__ == '__main__':
    main()
