import json
import time
import os
import asyncio
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)
from telegram.constants import ParseMode
from automation import realizar_donacion

# --- Carga de Configuración ---
def load_data():
    """Carga los datos de usuarios y tarjetas desde data.json."""
    with open('data.json', 'r') as f:
        return json.load(f)

def save_data(data):
    """Guarda los datos actualizados en data.json."""
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)

# --- Decorador de Autorización ---
def authorized(func):
    """
    Un decorador que restringe el uso de un comando solo a usuarios autorizados.
    """
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        config = load_data()
        # Aseguramos que el ID de usuario se compare como string
        user_id = str(update.effective_chat.id)
        if user_id not in config['authorized_users']:
            await update.message.reply_text("❌ No tienes permiso para usar este comando.")
            print(f"Acceso denegado para el chat_id: {user_id}")
            return
        await func(update, context, *args, **kwargs)
    return wrapper

# --- Funciones de Comandos del Bot ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Función que se activa con el comando /start. Muestra un mensaje de bienvenida."""
    user_name = update.effective_user.first_name
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"¡Hola, {user_name}! 👋\n"
        f"Soy tu asistente de donaciones. Tu ID de chat es: `{chat_id}`\n"
        "Asegúrate de que este ID esté en la lista `authorized_users` en `data.json`.\n"
        "Usa el comando `.cmds` para ver lo que puedo hacer.",
        parse_mode=ParseMode.MARKDOWN
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde 'pong' al comando .ping."""
    await update.message.reply_text("pong")

async def cmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra la lista de comandos disponibles."""
    await update.message.reply_text(
        "🤖 *Comandos Disponibles*\n\n"
        "`.ping` - Verifica si estoy activo.\n"
        "`.donar <monto>` - Inicia el proceso de donación con todas las tarjetas. Si no especificas monto, se usarán 5000 CLP.\n"
        "`.tarjetas` - Muestra la cantidad de tarjetas configuradas.\n"
        "`.addcard` - Inicia el proceso para agregar una nueva tarjeta.\n"
        "`.cancel` - Cancela la operación actual (como agregar una tarjeta).\n"
        "`.cmds` - Muestra esta lista de comandos.",
        parse_mode=ParseMode.MARKDOWN
    )

@authorized
async def list_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra cuántas tarjetas hay configuradas."""
    config = load_data()
    num_cards = len(config['cards'])
    await update.message.reply_text(f"💳 Hay {num_cards} tarjetas configuradas y listas para donar.")

@authorized
async def donate_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Inicia el ciclo de donación para todas las tarjetas en la lista.
    """
    config = load_data()
    try:
        monto = int(context.args[0]) if context.args else 5000
    except (ValueError, IndexError):
        monto = 5000

    await update.message.reply_text(f"🚀 ¡Iniciando proceso de donación para {len(config['cards'])} tarjetas por un monto de ${monto} CLP cada una!")

    progress_message = await update.message.reply_text("Iniciando...")

    success_count = 0
    failure_count = 0

    total_cards = len(config['cards'])
    for i, card in enumerate(config['cards']):
        progress_percent = int(((i + 1) / total_cards) * 100)
        bar_filled = '█' * int(progress_percent / 10)
        bar_empty = '░' * (10 - len(bar_filled))

        progress_text = (
            f"*Procesando Tarjeta {i+1} de {total_cards} ({card['card_holder']})*\n"
            f"Progreso: `[{bar_filled}{bar_empty}] {progress_percent}%`"
        )
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=progress_message.message_id, text=progress_text, parse_mode=ParseMode.MARKDOWN)

        loop = asyncio.get_event_loop()
        success, result = await loop.run_in_executor(None, realizar_donacion, card, monto)

        if success:
            success_count += 1
            await update.message.reply_text(f"✅ ¡Éxito con la tarjeta de {card['card_holder']}!")
        else:
            failure_count += 1
            await update.message.reply_text(f"❌ Falló la donación con la tarjeta de {card['card_holder']}. Enviando captura del error...")
            try:
                with open(result, 'rb') as photo:
                    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption="Captura del error.")
                os.remove(result)
            except Exception as e:
                await update.message.reply_text(f"No se pudo enviar la captura de pantalla. Error: {e}")

    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=progress_message.message_id)
    summary_text = (
        f"🏁 *Proceso Finalizado*\n\n"
        f"Donaciones exitosas: {success_count} ✅\n"
        f"Donaciones fallidas: {failure_count} ❌\n"
    )
    await update.message.reply_text(summary_text, parse_mode=ParseMode.MARKDOWN)

# --- Lógica para agregar tarjetas ---
CARD_HOLDER, CARD_NUMBER, EXPIRY_MONTH, EXPIRY_YEAR, CVV, EMAIL = range(6)

@authorized
async def add_card_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Vamos a agregar una nueva tarjeta. Por favor, dime el nombre del titular de la tarjeta. Envía /cancel para detener.")
    return CARD_HOLDER

async def card_holder_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['card_holder'] = update.message.text
    await update.message.reply_text("Gracias. Ahora, por favor, introduce el número de la tarjeta.")
    return CARD_NUMBER

async def card_number_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['card_number'] = update.message.text
    await update.message.reply_text("Perfecto. Ahora el mes de expiración (MM, por ejemplo: 08).")
    return EXPIRY_MONTH

async def expiry_month_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['expiry_month'] = update.message.text
    await update.message.reply_text("Casi terminamos. Ahora el año de expiración (AA, por ejemplo: 25).")
    return EXPIRY_YEAR

async def expiry_year_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['expiry_year'] = update.message.text
    await update.message.reply_text("Ahora el código de seguridad (CVV).")
    return CVV

async def cvv_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['cvv'] = update.message.text
    await update.message.reply_text("Finalmente, el email asociado a la tarjeta.")
    return EMAIL

async def email_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['email'] = update.message.text

    new_card = {
        "card_holder": context.user_data['card_holder'],
        "card_number": context.user_data['card_number'],
        "expiry_month": context.user_data['expiry_month'],
        "expiry_year": context.user_data['expiry_year'],
        "cvv": context.user_data['cvv'],
        "email": context.user_data['email']
    }

    config = load_data()
    config['cards'].append(new_card)
    save_data(config)

    await update.message.reply_text("¡Tarjeta agregada con éxito!")
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    update.message.reply_text("Proceso de agregar tarjeta cancelado.")
    context.user_data.clear()
    return ConversationHandler.END

# --- Función Principal del Bot ---
def main():
    """Función principal que configura y ejecuta el bot."""
    try:
        config = load_data()
        token = config.get("telegram_token")
        if token == "YOUR_TELEGRAM_BOT_TOKEN_HERE" or not token:
            print("Error: Por favor, añade tu token de Telegram en el archivo config.json")
            return
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'config.json'. Por favor, crea uno a partir del ejemplo.")
        return

    application = Application.builder().token(token).build()

    # --- Registro de Comandos ---
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('addcard', add_card_start, filters=filters.Regex(r'^\.addcard'))],
        states={
            CARD_HOLDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, card_holder_received)],
            CARD_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, card_number_received)],
            EXPIRY_MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, expiry_month_received)],
            EXPIRY_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, expiry_year_received)],
            CVV: [MessageHandler(filters.TEXT & ~filters.COMMAND, cvv_received)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ping", ping, filters=filters.Regex(r'^\.ping')))
    application.add_handler(CommandHandler("cmds", cmds, filters=filters.Regex(r'^\.cmds')))
    application.add_handler(CommandHandler("tarjetas", list_cards, filters=filters.Regex(r'^\.tarjetas')))
    application.add_handler(CommandHandler("donar", donate_all, filters=filters.Regex(r'^\.donar')))
    application.add_handler(conv_handler)

    # Inicia el bot
    print("🤖 Bot iniciado y escuchando...")
    application.run_polling()

if __name__ == '__main__':
    main()
