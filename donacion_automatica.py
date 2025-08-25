# -*- coding: utf-8 -*-

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- ADVERTENCIA DE SEGURIDAD ---
# Este script es una herramienta de automatización. Manejar datos de tarjetas de
# crédito de forma programática conlleva riesgos de seguridad.
# 1. NO guardes información real de tarjetas de crédito directamente en este archivo.
# 2. Considera usar variables de entorno o un gestor de secretos para cargar los datos.
# 3. Asegúrate de que el entorno donde se ejecuta este script es seguro.
# El uso de este script es bajo tu propia responsabilidad.

# --- CONFIGURACIÓN ---
URL_DONACION = "https://parroquiamariamadredemisericordia.trytoku.com/forms/abonosparroquia?portal=1"
MONTO_DONACION = "5000"

def realizar_donacion(datos_personales, datos_tarjeta):
    """
    Esta función abre un navegador, navega a la página de donación,
    rellena el formulario y procesa el pago.

    :param datos_personales: Un diccionario con 'nombres', 'apellidos', 'email', 'celular'.
    :param datos_tarjeta: Un diccionario con 'nombre_titular', 'numero', 'fecha_exp' (MM/YY), 'cvc'.
    """
    driver = None  # Inicializar driver a None
    try:
        # --- Inicialización del WebDriver ---
        # Esto instalará y configurará automáticamente el driver para Chrome.
        # No necesitas descargar chromedriver manualmente.
        print("Iniciando el navegador...")
        options = webdriver.ChromeOptions()
        # Descomenta la siguiente línea para ejecutar en modo "headless" (sin interfaz gráfica)
        # options.add_argument("--headless")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.get(URL_DONACION)

        print("Página cargada. Esperando a que los elementos del formulario estén disponibles...")
        # Espera explícita para asegurar que la página (y el JS) se carguen completamente.
        time.sleep(5)

        # --- Rellenar datos personales ---
        # NOTA: Los selectores (By.NAME, '...') son suposiciones. Si el script falla,
        # necesitarás encontrar los correctos. Para ello:
        # 1. Ve a la página en Chrome.
        # 2. Haz clic derecho en un campo (ej. "Nombres") y selecciona "Inspeccionar".
        # 3. Busca el atributo 'id' o 'name' en el elemento <input>.
        # 4. Reemplaza el valor en el script. Por ejemplo, si encuentras <input id="firstName">,
        #    usa By.ID, 'firstName'.

        print("Rellenando datos personales...")
        driver.find_element(By.NAME, 'name').send_keys(datos_personales['nombres'])
        driver.find_element(By.NAME, 'lastname').send_keys(datos_personales['apellidos'])
        driver.find_element(By.NAME, 'email').send_keys(datos_personales['email'])
        driver.find_element(By.NAME, 'phone').send_keys(datos_personales['celular'])

        # El campo de monto podría ser diferente, ajústalo si es necesario.
        # A veces es un input, otras un botón. Aquí asumimos que es un input.
        # Si el monto de 5000 ya está seleccionado por defecto o no es editable, puedes comentar estas líneas.
        print(f"Estableciendo monto a {MONTO_DONACION}...")
        amount_input = driver.find_element(By.NAME, 'amount')
        amount_input.clear()
        amount_input.send_keys(MONTO_DONACION)

        print("Datos personales rellenados.")
        time.sleep(1) # Pequeña pausa

        # --- Rellenar datos de la tarjeta ---
        # Los formularios de pago a menudo están dentro de un 'iframe'.
        # Es necesario cambiar el contexto del driver a ese iframe.
        print("Cambiando al iframe del formulario de pago...")

        # Espera a que el iframe esté presente y cambia a él.
        # El selector del iframe puede variar. Investiga en la página si este falla.
        wait = WebDriverWait(driver, 10)
        iframe_pago = wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[contains(@src, "kushki")]')))
        driver.switch_to.frame(iframe_pago)
        print("Dentro del iframe.")

        # Ahora, dentro del iframe, rellenamos los datos de la tarjeta
        print("Rellenando datos de la tarjeta...")
        driver.find_element(By.NAME, 'card-holder-name').send_keys(datos_tarjeta['nombre_titular'])
        driver.find_element(By.NAME, 'card-number').send_keys(datos_tarjeta['numero'])
        driver.find_element(By.NAME, 'card-expiry-date').send_keys(datos_tarjeta['fecha_exp'])
        driver.find_element(By.NAME, 'card-cvc').send_keys(datos_tarjeta['cvc'])

        print("Datos de tarjeta rellenados.")

        # Volver al contenido principal de la página
        driver.switch_to.default_content()
        time.sleep(1)

        # --- Enviar el formulario ---
        print("Haciendo clic en el botón de donar...")
        # Usamos XPath para encontrar un botón que contenga el texto "Donar". Es más robusto.
        boton_donar = driver.find_element(By.XPATH, '//button[contains(., "Donar")]')
        boton_donar.click()

        print("¡Donación enviada! Esperando 15 segundos para ver el resultado...")
        time.sleep(15) # Espera para que puedas ver la página de confirmación/error.

        print("Proceso de donación completado con éxito.")
        return True, "Éxito"

    except Exception as e:
        print(f"\n--- Ocurrió un error ---")
        print(f"Error: {e}")
        print("El script no pudo completar la donación. Revisa los selectores y la conexión.")
        return False, str(e)

    finally:
        if driver:
            print("Cerrando el navegador.")
            driver.quit()

# --- Cómo integrar con un Bot de Telegram ---
#
# 1. Instala la librería: pip install python-telegram-bot
# 2. El bot necesitaría un comando, por ejemplo /donar.
# 3. El handler de ese comando podría pedir al usuario los datos de la tarjeta.
#    (¡CUIDADO! No es seguro pedir datos de tarjeta por Telegram).
# 4. Una forma más segura es que el bot lea los datos de un lugar seguro
#    previamente configurado por ti (ej. un archivo local o variables de entorno).
#
# Ejemplo de un handler de Telegram:
#
# from telegram.ext import CommandHandler, Updater
#
# def comando_donar(update, context):
#     # NO ES SEGURO OBTENER DATOS ASÍ. ES SOLO UN EJEMPLO CONCEPTUAL.
#     # Lo ideal es que los datos se lean de una fuente segura, no del mensaje.
#     user_id = update.effective_user.id
#
#     # Aquí cargarías los datos de forma segura para este usuario
#     datos_personales_usuario = DATOS_PERSONALES_EJEMPLO
#     datos_tarjeta_usuario = ... # Cargar desde una base de datos, archivo, etc.
#
#     update.message.reply_text("Iniciando proceso de donación...")
#     exito, mensaje = realizar_donacion(datos_personales_usuario, datos_tarjeta_usuario)
#     if exito:
#         update.message.reply_text(f"Donación finalizada. Estado: {mensaje}")
#     else:
#         update.message.reply_text(f"Error en la donación: {mensaje}")
#
# updater = Updater("TU_TOKEN_DE_TELEGRAM", use_context=True)
# updater.dispatcher.add_handler(CommandHandler('donar', comando_donar))
# updater.start_polling()


if __name__ == '__main__':
    # --- DATOS DE EJEMPLO ---
    # RELLENA ESTA SECCIÓN CON TUS DATOS REALES ANTES DE EJECUTAR
    # O, mejor aún, cárgalos desde un archivo o variables de entorno.

    datos_personales_ejemplo = {
        "nombres": "Juan",
        "apellidos": "Pérez",
        "email": "juan.perez@example.com",
        "celular": "912345678" # Sin prefijos, solo números
    }

    # --- ¡¡¡NO GUARDES DATOS REALES AQUÍ DE FORMA PERMANENTE!!! ---
    # Este diccionario es el que debes modificar para cada tarjeta.
    # Pega aquí los datos de la tarjeta que quieras usar para una ejecución.
    datos_tarjeta_ejemplo = {
        "nombre_titular": "Juan Perez",
        "numero": "4242424242424242", # Número de tarjeta de prueba
        "fecha_exp": "12/25", # Formato MM/YY
        "cvc": "123" # CVC de prueba
    }

    print("--- INICIANDO SCRIPT DE DONACIÓN AUTOMÁTICA ---")
    print("ADVERTENCIA: Estás a punto de ejecutar una automatización de pago.")

    # input("Presiona Enter para continuar o Ctrl+C para cancelar...")

    realizar_donacion(datos_personales_ejemplo, datos_tarjeta_ejemplo)
