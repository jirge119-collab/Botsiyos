import asyncio
import os
from playwright.async_api import async_playwright, TimeoutError, Error

# --- CONFIGURACIÓN DE SELECTORES ---
# Si el bot falla al rellenar los campos, actualiza estos valores.
# Las instrucciones sobre cómo hacerlo están en el archivo README.md.
SELECTORS = {
    "rut": 'input[name="rut"]',
    "nombre": 'input[name="nombre"]',
    "apellido": 'input[name="apellido"]',
    "email": 'input[name="email"]',
    "concepto_aporte": 'select[name="concepto"]',
    "monto": 'input[placeholder="Monto a donar"]',
    "boton_registrar": 'button:has-text("Registrar")',
    "boton_agregar_pago": 'button:has-text("Agregar medio de pago")',
    "iframe_pago": 'iframe[src*="wompi"]',
    "tarjeta": {
        "numero": 'input[name="card-number"]',
        "expiracion": 'input[name="card-exp"]',
        "cvc": 'input[name="card-cvc"]',
        "nombre_titular": 'input[name="card-holder-name"]',
        "boton_pagar": 'button[type="submit"]'
    }
}
# ------------------------------------

DONATION_URL = "https://parroquiamariamadredemisericordia.trytoku.com/forms/abonosparroquia?portal=1"
DONATION_AMOUNT = "10000"

async def perform_donation(personal_info: dict, card_info: dict) -> tuple[bool, str]:
    """
    Realiza una donación automatizada usando datos fijos y selectores configurables.
    """
    pre_payment_screenshot = "pre-payment-error.png"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            print(f"Iniciando donación para {personal_info['email']} con tarjeta {card_info['card_number'][-4:]}")
            await page.goto(DONATION_URL, timeout=60000)

            # --- Rellenar formulario con esperas explícitas ---
            async def wait_and_fill(selector, value):
                locator = page.locator(selector)
                await locator.wait_for(state="visible", timeout=15000)
                await locator.fill(value)

            async def wait_and_click(selector):
                locator = page.locator(selector)
                await locator.wait_for(state="visible", timeout=15000)
                await locator.click()

            await wait_and_fill(SELECTORS["rut"], personal_info['rut'])
            await wait_and_fill(SELECTORS["nombre"], personal_info['nombre'])
            await wait_and_fill(SELECTORS["apellido"], personal_info['apellido'])
            await wait_and_fill(SELECTORS["email"], personal_info['email'])

            concepto_locator = page.locator(SELECTORS["concepto_aporte"])
            await concepto_locator.wait_for(state="visible", timeout=15000)
            await concepto_locator.select_option(label="Donación")

            await wait_and_fill(SELECTORS["monto"], DONATION_AMOUNT)
            await wait_and_click(SELECTORS["boton_registrar"])
            await wait_and_click(SELECTORS["boton_agregar_pago"])

            await page.wait_for_timeout(5000)
            payment_frame = page.frame_locator(SELECTORS["iframe_pago"])

            if not await payment_frame.locator().is_visible():
                 return False, "No se pudo encontrar el iframe del formulario de pago."

            # --- Rellenar datos de tarjeta con esperas explícitas ---
            card_selectors = SELECTORS["tarjeta"]

            async def frame_wait_and_fill(selector, value):
                locator = payment_frame.locator(selector)
                await locator.wait_for(state="visible", timeout=15000)
                await locator.fill(value)

            await frame_wait_and_fill(card_selectors["numero"], card_info['card_number'])
            expiry_date = f"{card_info['expiry_month']}/{card_info['expiry_year'][-2:]}"
            await frame_wait_and_fill(card_selectors["expiracion"], expiry_date)
            await frame_wait_and_fill(card_selectors["cvc"], card_info['cvc'])
            await frame_wait_and_fill(card_selectors["nombre_titular"], f"{personal_info['nombre']} {personal_info['apellido']}")

            await page.screenshot(path=pre_payment_screenshot)

            pagar_locator = payment_frame.locator(card_selectors["boton_pagar"])
            await pagar_locator.wait_for(state="visible", timeout=15000)
            await pagar_locator.click()

            print("Pago enviado. Esperando resultado...")
            await page.wait_for_url('**/*success*', timeout=120000)

            if os.path.exists(pre_payment_screenshot):
                os.remove(pre_payment_screenshot)

            await browser.close()
            return True, "Donación completada exitosamente."

        except (TimeoutError, Error) as e:
            # Captura errores de Playwright (incluyendo TimeoutError)
            error_message = str(e)
            print(f"Fallo de Playwright: {error_message}")

            # Intentar obtener un mensaje de error más específico de la página
            try:
                error_locator = payment_frame.locator('div[class*="error"], div[class*="message"], span[class*="error"]').first
                await error_locator.wait_for(state="visible", timeout=5000)
                message_text = await error_locator.text_content()
                if message_text:
                    error_message = message_text.strip()
            except Exception:
                print("No se pudo capturar un mensaje de error de la pasarela de pago.")

            await page.screenshot(path="post-payment-error.png")
            await browser.close()
            return False, f"Error durante la automatización: {error_message}"

        except Exception as e:
            error_text = f"Ocurrió un error inesperado no relacionado con Playwright: {e}"
            print(error_text)
            await page.screenshot(path="post-payment-error.png")
            await browser.close()
            return False, error_text
