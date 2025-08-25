import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

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
    if config and user_id == config.get('allowed_user_id'):
        await update.message.reply_text(
            "¡Hola! Soy tu bot de donaciones v2. 👋\n\n"
            "Para iniciar una donación, usa el comando /donar seguido de los datos de tus tarjetas, una por línea.\n\n"
            "El formato para cada tarjeta es: `numero,mes,año,cvc`\n\n"
            "**Ejemplo de uso:**\n"
            "```\n"
            "/donar\n"
            "1111222233334444,12,2028,123\n"
            "5555666677778888,06,2027,456\n"
            "```"
        )
    else:
        logger.warning(f"Acceso no autorizado denegado al usuario con ID: {user_id}")
        await update.message.reply_text("No tienes permiso para usar este bot.")

async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /donar, que procesa las tarjetas y ejecuta la donación."""
    user_id = update.effective_user.id
    if not config or user_id != config.get('allowed_user_id'):
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
            "1111222233334444,12,2028,123\n"
            "```"
        )
        return

    # Procesar cada línea como una tarjeta
    lines = cards_text.split('\n')
    cards_to_process = []
    for line in lines:
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split(',')]
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
        await update.message.reply_text("No se encontraron tarjetas válidas en tu mensaje. Asegúrate de usar el formato: `numero,mes,año,cvc`")
        return

    await update.message.reply_text(f"Iniciando proceso de donación con {len(cards_to_process)} tarjeta(s)... 🚀")

    donation_successful = False
    for i, card in enumerate(cards_to_process):
        card_nickname = f"Tarjeta #{i + 1} (terminada en {card['card_number'][-4:]})"
        await update.message.reply_text(f"💳 Intentando con {card_nickname}...")

        try:
            success = await perform_donation(card)
            if success:
                await update.message.reply_text(f"✅ ¡Donación exitosa con {card_nickname}!")
                donation_successful = True
                break
            else:
                await update.message.reply_text(f"❌ Falló la donación con {card_nickname}. Intentando con la siguiente.")

        except Exception as e:
            logger.error(f"Error crítico al procesar {card_nickname}: {e}")
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
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("donar", donate_command))

    logger.info("El bot se ha iniciado y está escuchando...")
    application.run_polling()

if __name__ == '__main__':
    main()
