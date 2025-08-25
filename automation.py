import asyncio
import os
from playwright.async_api import async_playwright, TimeoutError, Error

# --- CONFIGURACIÓN DE SELECTORES PARA TECHO CHILE (GETNET) ---
# Si el bot falla, es muy probable que necesites actualizar estos valores.
# Las instrucciones sobre cómo hacerlo están en el archivo README.md.
SELECTORS = {
    # --- Selección de Monto ---
    "otro_monto_button": "button:has-text('Otro monto')", # Botón para abrir el campo de monto personalizado
    "monto_input": "input[name='amount']", # Campo para ingresar el monto
    "nombre_input": "input[name='name']",
    "apellido_input": "input[name='lastname']",
    "email_input": "input[name='email']",
    "submit_personal_data_button": "button:has-text('Siguiente')", # Botón para pasar al pago

    # --- Formulario de Tarjeta ---
    # Es posible que estos campos estén dentro de un iframe. Si es así, necesitarás el selector del iframe.
    "iframe_pago": "iframe[id='getnet-payment-iframe']", # Suposición completa
    "tarjeta": {
        "numero": "input#cardNumber",
        "expiracion": "input#cardExpirationDate", # Formato MM/AA
        "cvv": "input#cardCvv",
        "nombre_titular": "input#cardHolder",
        "email_pago": "input#cardHolderMail", # A veces piden el email de nuevo
        "boton_pagar": "button#btn-pay"
    }
}
# ------------------------------------

DONATION_URL = "https://micrositios.getnet.cl/techochile"
DONATION_AMOUNT = "5000" # Monto de donación por defecto

async def perform_donation(personal_info: dict, card_info: dict) -> tuple[bool, str]:
    """
    Realiza una donación en la página de TECHO Chile (Getnet).
    """
    pre_payment_screenshot = "pre-payment-error.png"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            print(f"Iniciando donación a TECHO para {personal_info['email']}...")
            await page.goto(DONATION_URL, timeout=60000)

            # --- Lógica de llenado de formulario ---
            async def wait_and_click(selector):
                locator = page.locator(selector)
                await locator.wait_for(state="visible", timeout=15000)
                await locator.click()

            async def wait_and_fill(selector, value):
                locator = page.locator(selector)
                await locator.wait_for(state="visible", timeout=15000)
                await locator.fill(value)

            # 1. Seleccionar monto
            await wait_and_click(SELECTORS["otro_monto_button"])
            await wait_and_fill(SELECTORS["monto_input"], DONATION_AMOUNT)

            # 2. Rellenar datos personales
            await wait_and_fill(SELECTORS["nombre_input"], personal_info['nombre'])
            await wait_and_fill(SELECTORS["apellido_input"], personal_info['apellido'])
            await wait_and_fill(SELECTORS["email_input"], personal_info['email'])

            # 3. Continuar al pago
            await wait_and_click(SELECTORS["submit_personal_data_button"])

            # 4. Rellenar datos de tarjeta (posiblemente en iframe)
            # await page.wait_for_timeout(5000) # Espera a que cargue el iframe
            # iframe_locator = page.locator(SELECTORS["iframe_pago"])
            # await iframe_locator.wait_for(state="visible", timeout=15000)
            # payment_frame = page.frame_locator(SELECTORS["iframe_pago"])
            # NOTA: La lógica del iframe se comenta. Si el formulario está en un iframe,
            # descomenta las 3 líneas de arriba y cambia page.locator por payment_frame.locator
            # en la sección de tarjeta.

            card_selectors = SELECTORS["tarjeta"]
            await page.locator(card_selectors["numero"]).fill(card_info['card_number'])
            # Getnet podría pedir MM/AA en lugar de MM/AAAA
            expiry_date = f"{card_info['expiry_month']}/{card_info['expiry_year'][-2:]}"
            await page.locator(card_selectors["expiracion"]).fill(expiry_date)
            await page.locator(card_selectors["cvv"]).fill(card_info['cvc'])
            await page.locator(card_selectors["nombre_titular"]).fill(f"{personal_info['nombre']} {personal_info['apellido']}")
            await page.locator(card_selectors["email_pago"]).fill(personal_info['email'])

            await page.screenshot(path=pre_payment_screenshot)

            # 5. Hacer clic en el botón final de pagar
            await page.locator(card_selectors["boton_pagar"]).click()

            print("Pago enviado. Esperando resultado...")
            # La página de éxito puede tener una URL o un texto específico.
            # Usaremos una espera genérica a que la red se calme.
            await page.wait_for_load_state("networkidle", timeout=120000)

            # Verificar el resultado buscando un texto de éxito
            success_locator = page.locator("text=/¡Tu donación se ha realizado con éxito!/i")
            if not await success_locator.is_visible():
                raise TimeoutError("La página de éxito no apareció o no contiene el texto esperado.")

            if os.path.exists(pre_payment_screenshot):
                os.remove(pre_payment_screenshot)

            await browser.close()
            return True, "Donación a TECHO completada exitosamente."

        except (TimeoutError, Error) as e:
            error_message = str(e)
            print(f"Fallo de Playwright: {error_message}")
            await page.screenshot(path="post-payment-error.png")
            await browser.close()
            return False, f"Error durante la automatización: {error_message}"

        except Exception as e:
            error_text = f"Ocurrió un error inesperado: {e}"
            print(error_text)
            await page.screenshot(path="post-payment-error.png")
            await browser.close()
            return False, error_text
