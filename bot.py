import logging
import os
import re
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Mis módulos locales
import card_utils
import gateway

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Configurar logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Funciones de los Comandos ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía un mensaje de bienvenida cuando el comando /start es ejecutado."""
    user_name = update.effective_user.first_name
    welcome_message = (
        f"¡Hola, {user_name}! 👋\n\n"
        "Soy tu bot verificador de tarjetas. Puedo ayudarte a validar números de tarjeta para evitar errores.\n\n"
        "Usa /help para ver los comandos disponibles."
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra los comandos de ayuda."""
    help_text = (
        "Aquí tienes los comandos que puedes usar:\n\n"
        "🔹 `/validate <numero_de_tarjeta>`\n"
        "   Verifica si el formato del número es correcto (algoritmo de Luhn) e identifica la marca de la tarjeta.\n"
        "   *Ejemplo:* `/validate 49927398716`\n\n"
        "🔹 `/check <numero_de_tarjeta>`\n"
        "   Hace lo mismo que `/validate` y además incluye una verificación (simulada) del estado de la tarjeta a través de una pasarela de pago.\n"
        "   *Nota:* La pasarela de pago debe ser configurada por el administrador del bot.\n"
        "   *Ejemplo:* `/check 49927398716`"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

def get_card_number_from_args(args: list[str]) -> str | None:
    """Extrae y limpia el número de tarjeta de los argumentos del comando."""
    if not args:
        return None

    # Unir todos los argumentos por si el número viene con espacios
    full_arg = "".join(args)

    # Limpiar cualquier caracter que no sea un dígito
    card_number = re.sub(r'\D', '', full_arg)

    if card_number:
        return card_number
    return None

async def validate_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Valida el número de tarjeta usando el algoritmo de Luhn y la marca."""
    card_number = get_card_number_from_args(context.args)

    if not card_number:
        await update.message.reply_text("Por favor, proporciona un número de tarjeta después del comando.\nEjemplo: `/validate 49927398716`")
        return

    is_valid = card_utils.is_luhn_valid(card_number)
    brand = card_utils.get_card_brand(card_number)

    response = (
        f"Resultados para la tarjeta: `...{card_number[-4:]}`\n"
        f"-------------------------------------\n"
        f"✅ **Validación Luhn:** {'Válido' if is_valid else 'Inválido'}\n"
        f"💳 **Marca:** {brand}"
    )
    await update.message.reply_text(response, parse_mode='Markdown')

async def check_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Valida la tarjeta, la marca y comprueba el estado en la pasarela."""
    card_number = get_card_number_from_args(context.args)

    if not card_number:
        await update.message.reply_text("Por favor, proporciona un número de tarjeta después del comando.\nEjemplo: `/check 49927398716`")
        return

    is_valid = card_utils.is_luhn_valid(card_number)
    brand = card_utils.get_card_brand(card_number)
    status = gateway.check_card_status(card_number)

    response = (
        f"Resultados para la tarjeta: `...{card_number[-4:]}`\n"
        f"-------------------------------------\n"
        f"✅ **Validación Luhn:** {'Válido' if is_valid else 'Inválido'}\n"
        f"💳 **Marca:** {brand}\n"
        f"🚦 **Pasarela de Pago:** {status}"
    )
    await update.message.reply_text(response, parse_mode='Markdown')


def main() -> None:
    """Inicia el bot."""
    # Obtener el token desde las variables de entorno
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("No se encontró la variable de entorno TELEGRAM_TOKEN. El bot no puede iniciar.")
        return

    # Crear la aplicación del bot
    application = Application.builder().token(token).build()

    # Registrar los manejadores de comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("validate", validate_card))
    application.add_handler(CommandHandler("check", check_card))

    # Iniciar el bot
    logger.info("Iniciando el bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
