import asyncio
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Importar la función de automatización
from automation import perform_donation

# Configurar logging para ver información útil en la consola
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
        logger.error("Error: El archivo 'config.json' no se encontró.")
        logger.info("Por favor, copia 'config.json.template', renómbralo a 'config.json' y rellena tus datos.")
        return None
    except json.JSONDecodeError:
        logger.error("Error: El archivo 'config.json' tiene un formato incorrecto.")
        return None

config = load_config()

# --- Funciones de Comandos del Bot ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /start."""
    user_id = update.effective_user.id
    if config and user_id == config.get('allowed_user_id'):
        await update.message.reply_text(
            "¡Hola! Soy tu bot de donaciones. 👋\n"
            "Estoy listo para ayudarte a automatizar tus donaciones.\n\n"
            "Usa el comando /donar para iniciar el proceso."
        )
    else:
        logger.warning(f"Acceso no autorizado denegado al usuario con ID: {user_id}")
        await update.message.reply_text("No tienes permiso para usar este bot.")

async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /donar, que inicia el proceso de donación."""
    user_id = update.effective_user.id
    if not config or user_id != config.get('allowed_user_id'):
        logger.warning(f"Acceso no autorizado denegado al usuario con ID: {user_id} para el comando /donar")
        await update.message.reply_text("No tienes permiso para usar este bot.")
        return

    personal_info = config.get('personal_info')
    cards = config.get('cards', [])

    if not personal_info or not cards:
        await update.message.reply_text("Error: La información personal o la lista de tarjetas no está configurada correctamente en 'config.json'.")
        return

    await update.message.reply_text("Iniciando proceso de donación... 🚀\nIntentaré con cada tarjeta hasta que una funcione.")

    donation_successful = False
    for i, card in enumerate(cards):
        card_nickname = f"Tarjeta #{i + 1} (terminada en {card.get('card_number', '****')[-4:]})"
        await update.message.reply_text(f"💳 Intentando con {card_nickname}...")

        try:
            # Ejecutar la función de automatización asíncrona
            success = await perform_donation(personal_info, card)

            if success:
                success_message = f"✅ ¡Donación exitosa con {card_nickname}!"
                await update.message.reply_text(success_message)
                donation_successful = True
                break  # Detener el proceso si una donación es exitosa
            else:
                failure_message = f"❌ Falló la donación con {card_nickname}. Intentando con la siguiente."
                await update.message.reply_text(failure_message)

        except Exception as e:
            logger.error(f"Ocurrió un error crítico al procesar {card_nickname}: {e}")
            await update.message.reply_text(f"⚠️ Ocurrió un error inesperado con {card_nickname}. Revisa los logs.")

    if not donation_successful:
        await update.message.reply_text("🛑 Proceso finalizado. Ninguna de las tarjetas pudo completar la donación.")


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

    # Añadir manejadores de comandos
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("donar", donate_command))

    logger.info("El bot se ha iniciado y está escuchando...")
    application.run_polling()

if __name__ == '__main__':
    main()
