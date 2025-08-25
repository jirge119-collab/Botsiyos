import json
import time
import os
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters, MessageHandler
from telegram.parsemode import ParseMode
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
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        config = load_data()
        user_id = str(update.effective_chat.id)
        if user_id not in config['authorized_users']:
            update.message.reply_text("❌ No tienes permiso para usar este comando.")
            print(f"Acceso denegado para el chat_id: {user_id}")
            return
        return func(update, context, *args, **kwargs)
    return wrapper

# --- Funciones de Comandos del Bot ---

def start(update: Update, context: CallbackContext):
    """Función que se activa con el comando /start. Muestra un mensaje de bienvenida."""
    user_name = update.effective_user.first_name
    chat_id = update.effective_chat.id
    update.message.reply_text(
        f"¡Hola, {user_name}! 👋\n"
        f"Soy tu asistente de donaciones. Tu ID de chat es: `{chat_id}`\n"
        "Asegúrate de que este ID esté en la lista `authorized_users` en `data.json`.\n"
        "Usa el comando `.cmds` para ver lo que puedo hacer."
    )

def ping(update: Update, context: CallbackContext):
    """Responde 'pong' al comando .ping."""
    update.message.reply_text("pong")

def cmds(update: Update, context: CallbackContext):
    """Muestra la lista de comandos disponibles."""
    update.message.reply_text(
        "🤖 *Comandos Disponibles*\n\n"
        "`.ping` - Verifica si estoy activo.\n"
        "`.donar <monto>` - Inicia el proceso de donación con todas las tarjetas. Si no especificas monto, se usarán 5000 CLP.\n"
        "`.tarjetas` - Muestra la cantidad de tarjetas configuradas.\n"
        "`.addcard` - Inicia el proceso para agregar una nueva tarjeta.\n"
        "`.cmds` - Muestra esta lista de comandos.",
        parse_mode=ParseMode.MARKDOWN
    )

@authorized
def list_cards(update: Update, context: CallbackContext):
    """Muestra cuántas tarjetas hay configuradas."""
    config = load_data()
    num_cards = len(config['cards'])
    update.message.reply_text(f"💳 Hay {num_cards} tarjetas configuradas y listas para donar.")

@authorized
def donate_all(update: Update, context: CallbackContext):
    """
    Inicia el ciclo de donación para todas las tarjetas en la lista.
    """
    config = load_data()
    try:
        # Obtener el monto desde el comando, ej: .donar 1000
        monto = int(context.args[0]) if context.args else 5000
    except (ValueError, IndexError):
        monto = 5000 # Valor por defecto si no se proporciona o es inválido

    update.message.reply_text(f"🚀 ¡Iniciando proceso de donación para {len(config['cards'])} tarjetas por un monto de ${monto} CLP cada una!")

    # Mensaje de progreso
    progress_message = update.message.reply_text("Iniciando...")

    success_count = 0
    failure_count = 0

    total_cards = len(config['cards'])
    for i, card in enumerate(config['cards']):
        # --- Barra de progreso visual en Telegram ---
        progress_percent = int(((i + 1) / total_cards) * 100)
        bar_filled = '█' * int(progress_percent / 10)
        bar_empty = '░' * (10 - len(bar_filled))

        progress_text = (
            f"*Procesando Tarjeta {i+1} de {total_cards} ({card['card_holder']})*\n"
            f"Progreso: `[{bar_filled}{bar_empty}] {progress_percent}%`"
        )
        context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=progress_message.message_id, text=progress_text, parse_mode=ParseMode.MARKDOWN)

        # --- Llamada a la función de automatización ---
        success, result = realizar_donacion(card, monto)

        if success:
            success_count += 1
            update.message.reply_text(f"✅ ¡Éxito con la tarjeta de {card['card_holder']}!")
        else:
            failure_count += 1
            update.message.reply_text(f"❌ Falló la donación con la tarjeta de {card['card_holder']}. Enviando captura del error...")
            try:
                # Enviar la foto del error
                with open(result, 'rb') as photo:
                    context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption="Captura del error.")
                os.remove(result)
            except Exception as e:
                update.message.reply_text(f"No se pudo enviar la captura de pantalla. Error: {e}")

    # --- Resumen Final ---
    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=progress_message.message_id)
    summary_text = (
        f"🏁 *Proceso Finalizado*\n\n"
        f"Donaciones exitosas: {success_count} ✅\n"
        f"Donaciones fallidas: {failure_count} ❌\n"
    )
    update.message.reply_text(summary_text, parse_mode=ParseMode.MARKDOWN)

# --- Lógica para agregar tarjetas ---
CARD_HOLDER, CARD_NUMBER, EXPIRY_MONTH, EXPIRY_YEAR, CVV, EMAIL = range(6)

@authorized
def add_card_start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Vamos a agregar una nueva tarjeta. Por favor, dime el nombre del titular de la tarjeta.")
    return CARD_HOLDER

def card_holder(update: Update, context: CallbackContext) -> int:
    context.user_data['card_holder'] = update.message.text
    update.message.reply_text("Gracias. Ahora, por favor, introduce el número de la tarjeta.")
    return CARD_NUMBER

def card_number(update: Update, context: CallbackContext) -> int:
    context.user_data['card_number'] = update.message.text
    update.message.reply_text("Perfecto. Ahora el mes de expiración (MM).")
    return EXPIRY_MONTH

def expiry_month(update: Update, context: CallbackContext) -> int:
    context.user_data['expiry_month'] = update.message.text
    update.message.reply_text("Casi terminamos. Ahora el año de expiración (AA).")
    return EXPIRY_YEAR

def expiry_year(update: Update, context: CallbackContext) -> int:
    context.user_data['expiry_year'] = update.message.text
    update.message.reply_text("Ahora el código de seguridad (CVV).")
    return CVV

def cvv(update: Update, context: CallbackContext) -> int:
    context.user_data['cvv'] = update.message.text
    update.message.reply_text("Finalmente, el email asociado a la tarjeta.")
    return EMAIL

def email(update: Update, context: CallbackContext) -> int:
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

    update.message.reply_text("¡Tarjeta agregada con éxito!")
    return -1 # Fin de la conversación

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Proceso de agregar tarjeta cancelado.")
    return -1 # Fin de la conversación

# --- Función Principal del Bot ---
def main():
    """Función principal que configura y ejecuta el bot."""
    # Lee el token del bot desde el archivo de configuración
    try:
        with open('config.json', 'r') as f:
            config_data = json.load(f)
            token = config_data.get("telegram_token")
            if token == "YOUR_TELEGRAM_BOT_TOKEN_HERE" or not token:
                print("Error: Por favor, añade tu token de Telegram en el archivo config.json")
                return
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'config.json'.")
        return

    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    # --- Registro de Comandos ---
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('addcard', add_card_start, filters=Filters.regex(r'^\.addcard'))],
        states={
            CARD_HOLDER: [MessageHandler(Filters.text & ~Filters.command, card_holder)],
            CARD_NUMBER: [MessageHandler(Filters.text & ~Filters.command, card_number)],
            EXPIRY_MONTH: [MessageHandler(Filters.text & ~Filters.command, expiry_month)],
            EXPIRY_YEAR: [MessageHandler(Filters.text & ~Filters.command, expiry_year)],
            CVV: [MessageHandler(Filters.text & ~Filters.command, cvv)],
            EMAIL: [MessageHandler(Filters.text & ~Filters.command, email)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("ping", ping, filters=Filters.regex(r'^\.ping')))
    dispatcher.add_handler(CommandHandler("cmds", cmds, filters=Filters.regex(r'^\.cmds')))
    dispatcher.add_handler(CommandHandler("tarjetas", list_cards, filters=Filters.regex(r'^\.tarjetas')))
    dispatcher.add_handler(CommandHandler("donar", donate_all, filters=Filters.regex(r'^\.donar')))
    dispatcher.add_handler(conv_handler)

    # Inicia el bot
    updater.start_polling()
    print("🤖 Bot iniciado y escuchando...")
    updater.idle()

if __name__ == '__main__':
    main()
