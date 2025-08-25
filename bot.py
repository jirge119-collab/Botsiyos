# === IMPORTANTE ===
# Este es un script de Python para un bot de Telegram que automatiza donaciones en un sitio web específico.
# Sigue las instrucciones en el archivo INSTRUCCIONES.md para configurarlo y ejecutarlo correctamente.

import time
import sys
from telegram.ext import Updater, MessageHandler, Filters
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- CONFIGURACIÓN OBLIGATORIA ---
# 1. Reemplaza el texto de abajo con tu propio Token de Telegram.
#    Lo obtienes hablando con @BotFather en Telegram.
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# 2. Edita tus datos personales. Se usarán para rellenar el formulario.
#    (Estos datos son de ejemplo, reemplázalos con los tuyos).
NAME = "Tu Nombre"
LAST_NAME = "Tu Apellido"
EMAIL = "tu@email.com"
PHONE = "1234567890"
ID_DOCUMENT = "Tu Cédula o DNI"  # Cédula, DNI, etc.

# --- CONFIGURACIÓN AVANZADA (EDITAR DESPUÉS DE LEER INSTRUCCIONES.MD) ---
# 3. URL del formulario de donación.
URL = "https://parroquiamariamadredemisericordia.trytoku.com/forms/abonosparroquia?portal=1"
AMOUNT = "5000"  # Monto de la donación

# 4. Selectores de los campos del formulario.
#    DEBES REEMPLAZAR 'id_del_campo' con los valores reales que obtengas
#    inspeccionando la página web, como se explica en INSTRUCCIONES.MD.
#    Puedes usar By.ID, By.NAME, o By.XPATH.
SELECTORS = {
    # Datos Personales
    'name': (By.ID, 'id_del_campo_nombre'),
    'last_name': (By.ID, 'id_del_campo_apellido'),
    'email': (By.ID, 'id_del_campo_email'),
    'phone': (By.ID, 'id_del_campo_celular'),
    'id_document': (By.ID, 'id_del_campo_cedula'),
    # Monto
    'amount': (By.ID, 'id_del_campo_valor'),
    # Datos de la Tarjeta
    'card_number': (By.ID, 'id_del_campo_numero_tarjeta'),
    'holder_name': (By.ID, 'id_del_campo_nombre_tarjetahabiente'),
    'expiry_month': (By.ID, 'id_del_campo_mes_expiracion'),
    'expiry_year': (By.ID, 'id_del_campo_ano_expiracion'),
    'cvv': (By.ID, 'id_del_campo_cvv'),
    # Otros
    'terms_checkbox': (By.ID, 'id_del_checkbox_terminos'),
    'submit_button': (By.XPATH, '//button[@type="submit"]') # Este XPath suele funcionar para botones de envío
}

def automate_donation(update, context, card_number, holder_name, expiry_month, expiry_year, cvv):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Iniciando proceso de donación...")

    # Configuración de Selenium (no es necesario editar)
    chrome_options = Options()
    # chrome_options.add_argument('--headless') # Descomentar para modo sin cabeza si es compatible
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # La ruta al chromedriver debe estar en el PATH del sistema
    # En Termux, sigue las instrucciones de INSTRUCCIONES.MD
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(URL)
        time.sleep(5)  # Espera a que la página cargue

        # Rellenar información personal
        driver.find_element(*SELECTORS['name']).send_keys(NAME)
        driver.find_element(*SELECTORS['last_name']).send_keys(LAST_NAME)
        driver.find_element(*SELECTORS['email']).send_keys(EMAIL)
        driver.find_element(*SELECTORS['phone']).send_keys(PHONE)
        driver.find_element(*SELECTORS['id_document']).send_keys(ID_DOCUMENT)

        # Rellenar monto
        amount_field = driver.find_element(*SELECTORS['amount'])
        amount_field.clear()
        amount_field.send_keys(AMOUNT)

        # Rellenar datos de la tarjeta
        driver.find_element(*SELECTORS['card_number']).send_keys(card_number)
        driver.find_element(*SELECTORS['holder_name']).send_keys(holder_name)
        driver.find_element(*SELECTORS['expiry_month']).send_keys(expiry_month)

        # Se ajusta el año para que sea de 2 dígitos (ej: 2025 -> 25)
        if len(expiry_year) == 4:
            expiry_year = expiry_year[-2:]
        driver.find_element(*SELECTORS['expiry_year']).send_keys(expiry_year)
        driver.find_element(*SELECTORS['cvv']).send_keys(cvv)

        # Aceptar términos y condiciones
        driver.find_element(*SELECTORS['terms_checkbox']).click()

        # Enviar el formulario
        driver.find_element(*SELECTORS['submit_button']).click()

        time.sleep(10)  # Espera para el procesamiento

        # Comprobar si la donación fue exitosa (puedes ajustar las palabras clave)
        if "gracias" in driver.page_source.lower() or "thank you" in driver.page_source.lower():
            context.bot.send_message(chat_id=chat_id, text=f"Donación completada con la tarjeta que termina en {card_number[-4:]}")
        else:
            context.bot.send_message(chat_id=chat_id, text="La donación pudo haber fallado. Por favor, verifica manualmente.")

    except Exception as e:
        # Enviar captura de pantalla en caso de error
        error_screenshot = "error_screenshot.png"
        driver.save_screenshot(error_screenshot)
        context.bot.send_message(chat_id=chat_id, text=f"Ocurrió un error: {str(e)}")
        context.bot.send_photo(chat_id=chat_id, photo=open(error_screenshot, 'rb'), caption="Captura de pantalla del error.")
    finally:
        driver.quit()

def handle_message(update, context):
    message = update.message.text.strip()
    parts = message.split('|')
    if len(parts) == 5:
        card_number, holder_name, expiry_month, expiry_year, cvv = [p.strip() for p in parts]
        automate_donation(update, context, card_number, holder_name, expiry_month, expiry_year, cvv)
    else:
        update.message.reply_text("Formato inválido. Usa: numero_tarjeta|nombre_titular|mes_exp|año_exp|cvv")

def main():
    # --- Verificación del Token ---
    if TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN':
        print("Error: Debes reemplazar 'YOUR_TELEGRAM_BOT_TOKEN' con tu token real en el archivo bot.py.")
        sys.exit(1)

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("Bot iniciado. Envíale un mensaje para empezar.")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
