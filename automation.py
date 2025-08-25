import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def realizar_donacion(card_info: dict, monto: int = 5000) -> tuple[bool, str]:
    """
    Automatiza el proceso de donación en el sitio de Techo Chile.

    Args:
        card_info (dict): Un diccionario con los datos de la tarjeta.
        monto (int): El monto a donar. Por defecto es 5000.

    Returns:
        tuple[bool, str]: Una tupla donde el primer elemento es True si fue exitoso,
                         False si falló. El segundo elemento es un mensaje de estado
                         o la ruta a la captura de pantalla del error.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in background without opening a browser window
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    url = "https://micrositios.getnet.cl/techochile"

    try:
        print(f"Automatizando donación para: {card_info['card_holder']}")
        driver.get(url)

        # --- Paso 1: Rellenar el monto ---
        # Esperamos a que el campo de monto esté visible y luego escribimos en él.
        monto_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "monto"))
        )
        monto_input.clear()
        monto_input.send_keys(str(monto))

        # Hacemos clic en el botón para continuar al siguiente paso
        driver.find_element(By.ID, "btn_continuar").click()

        # --- Paso 2: Rellenar datos de la tarjeta ---
        # Esperamos a que el iframe del formulario de pago esté presente y cambiamos a él.
        WebDriverWait(driver, 20).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "getnet-payment-iframe"))
        )

        # Rellenamos cada campo del formulario de pago
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "pan"))).send_keys(card_info["card_number"])
        driver.find_element(By.ID, "cardholder-name").send_keys(card_info["card_holder"])
        driver.find_element(By.ID, "expiry-date").send_keys(f"{card_info['expiry_month']}{card_info['expiry_year']}")
        driver.find_element(By.ID, "cvv").send_keys(card_info["cvv"])

        # El campo de email está fuera del iframe, volvemos al contenido principal
        driver.switch_to.default_content()

        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_input.send_keys(card_info["email"])

        # Volvemos al iframe para hacer clic en el botón de pagar
        driver.switch_to.frame(driver.find_element(By.ID, "getnet-payment-iframe"))

        # --- Paso 3: Enviar el formulario ---
        pay_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "pay-button"))
        )
        pay_button.click()

        # --- Paso 4: Verificación del resultado ---
        # Volvemos al contenido principal para buscar el mensaje de éxito
        driver.switch_to.default_content()

        # Esperamos hasta 60 segundos por un mensaje de éxito o fracaso.
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '¡Muchas gracias por tu donación!') or contains(text(), 'Tu donación fue rechazada')]"))
        )

        # Comprobamos si el pago fue exitoso
        if "¡Muchas gracias por tu donación!" in driver.page_source:
            print("Donación completada exitosamente.")
            return True, "Donación completada exitosamente."
        else:
            print("La donación fue rechazada por el banco.")
            error_screenshot_path = f"error_pago_rechazado_{int(time.time())}.png"
            driver.save_screenshot(error_screenshot_path)
            return False, error_screenshot_path


    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error: La operación tardó demasiado o no se encontró un elemento. {e}")
        error_screenshot_path = f"error_timeout_{int(time.time())}.png"
        driver.save_screenshot(error_screenshot_path)
        return False, error_screenshot_path

    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        error_screenshot_path = f"error_inesperado_{int(time.time())}.png"
        driver.save_screenshot(error_screenshot_path)
        return False, error_screenshot_path

    finally:
        print("Cerrando el navegador.")
        driver.quit()
