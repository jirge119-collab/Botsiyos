import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from functools import wraps

import user_manager
from automation import run_donation_process

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Decorator for user permission checks ---
def restricted(func):
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if not user_manager.is_user_allowed(user_id):
            await update.message.reply_text("No tienes permiso para usar este comando.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

def owner_only(func):
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if not user_manager.is_owner(user_id):
            await update.message.reply_text("Este comando solo puede ser usado por el propietario del bot.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

# --- Bot Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    user = update.effective_user
    # If owner is not set, the first user to start the bot becomes the owner
    if user_manager.OWNER_ID == 0:
        user_manager.set_owner(user.id)
        user_manager.add_user(user.id)
        await update.message.reply_html(
            rf"Hola {user.mention_html()}! Eres el propietario de este bot. "
            "Usa el comando .cmds para ver lo que puedes hacer."
        )
    else:
        await update.message.reply_html(
            rf"Hola {user.mention_html()}! Bienvenido al bot de donaciones."
        )

@restricted
async def show_commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows available commands."""
    cmds = [
        ".cmds - Muestra esta lista de comandos.",
        ".donate - Inicia el proceso de donación. Envía los datos de las tarjetas en el formato correcto.",
        ".add_user <ID> - (Solo propietario) Agrega un usuario a la lista de permitidos."
    ]
    await update.message.reply_text("\n".join(cmds))

@owner_only
async def add_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Adds a new user to the allowed list."""
    try:
        user_id_to_add = int(context.args[0])
        if user_manager.add_user(user_id_to_add):
            await update.message.reply_text(f"Usuario {user_id_to_add} agregado correctamente.")
        else:
            await update.message.reply_text(f"El usuario {user_id_to_add} ya estaba en la lista.")
    except (IndexError, ValueError):
        await update.message.reply_text("Uso: .add_user <ID_del_usuario>")

@restricted
async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts the donation process with a list of cards."""
    text = update.message.text
    # Expects card data after the command, one card per line
    # Format: .donate\n<number> <expiry> <cvc>\n<number> <expiry> <cvc>
    lines = text.strip().split('\n')[1:] # remove command part

    if not lines:
        await update.message.reply_text(
            "Por favor, proporciona los datos de las tarjetas después del comando.\n"
            "Formato por línea: <numero> <MM/AA> <CVC>"
        )
        return

    await update.message.reply_text(f"Iniciando proceso de donación con {len(lines)} tarjeta(s).")

    # This URL should be passed from the user or configured elsewhere
    url = "https://parroquiamariamadredemisericordia.trytoku.com/recurring?user=cus_6kDcEHFpXiTTwJuljlnmqzwiJTphagWr&portal=1&account=acc_XpxidNAn00eoiSDka9wKEyiQUwH4P6Gw&subscriptions=%5B%22sub_KsDqoKddW0wjElzEaiYqZRhmOPdzds_1%22%5D"

    for i, line in enumerate(lines):
        try:
            number, expiry, cvc = line.split()
            card_details = {"number": number, "expiry": expiry, "cvc": cvc}

            await update.message.reply_text(f"Probando tarjeta #{i+1} (terminada en {number[-4:]})...")

            success, screenshot_path = await run_donation_process(card_details, url)

            if success:
                await update.message.reply_text(f"¡Donación exitosa con la tarjeta #{i+1}!")
                return # Stop after the first successful payment
            else:
                await update.message.reply_text(f"Falló el pago con la tarjeta #{i+1}.")
                if screenshot_path:
                    await update.message.reply_photo(photo=open(screenshot_path, 'rb'), caption="Error capturado.")
                    os.remove(screenshot_path) # Clean up the screenshot

        except ValueError:
            await update.message.reply_text(f"Error en el formato de la línea #{i+1}. Use: <numero> <MM/AA> <CVC>")
        except Exception as e:
            await update.message.reply_text(f"Ocurrió un error inesperado con la tarjeta #{i+1}: {e}")

    await update.message.reply_text("Se han probado todas las tarjetas y ninguna tuvo éxito.")


def main() -> None:
    """Start the bot."""
    # Get the bot token from an environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN no configurado en las variables de entorno.")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    # Using MessageHandler with a filter for commands starting with '.'
    application.add_handler(MessageHandler(filters.Regex(r'^\.cmds'), show_commands))
    application.add_handler(MessageHandler(filters.Regex(r'^\.add_user'), add_user_command))
    application.add_handler(MessageHandler(filters.Regex(r'^\.donate'), donate_command))


    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
