import asyncio
import os
from playwright.async_api import async_playwright, TimeoutError, Error

# --- CONFIGURACIÓN DE SELECTORES ---
# Si el bot falla, actualiza estos valores.
# Las instrucciones sobre cómo hacerlo están en el archivo README.md.
SELECTORS = {
    # --- Formulario Principal ---
    "rut": 'input[name="rut"]',
    "nombre": 'input[name="nombre"]',
    "apellido": 'input[name="apellido"]',
    "email": 'input[name="email"]',
    "concepto_aporte": 'select[name="concepto"]',
    "monto": 'input[placeholder="Monto a donar"]',
    "boton_registrar": 'button:has-text("Registrar")',
    "boton_agregar_pago": 'button:has-text("Agregar medio de pago")',

    # --- Formulario de Tarjeta (probablemente dentro de un iframe) ---
    "iframe_pago": 'iframe[src*="wompi"]', # O el proveedor que sea
    "tarjeta": {
        "numero": 'input[name="card-number"]',
        "nombre_titular": 'input[name="card-holder-name"]',
        "expiracion": 'input[name="card-exp"]', # Formato MM/YY
        "cvc": 'input[name="card-cvc"]',
        "inscribir_tarjeta_checkbox": 'input[type="checkbox"]', # Suposición, puede ser un botón
        "boton_pagar": 'button[type="submit"]'
    }
}
# ------------------------------------

DONATION_URL = "https://parroquiamariamadredemisericordia.trytoku.com/recurring/dG9rdV9jYXJkX29uX2ZpbGU?user=cus_6kDcEHFpXiTTwJuljlnmqzwiJTphagWr&portal=1&account=acc_XpxidNAn00eoiSDka9wKEyiQUwH4P6Gw&subscriptions=[\"sub_KsDqoKddW0wjElzEaiYqZRhmOPdzds_1\"]"
DONATION_AMOUNT = "10000"

async def perform_donation(personal_info: dict, card_info: dict) -> tuple[bool, str]:
    """
    Realiza una donación automatizada rellenando todos los campos.
    """
    pre_payment_screenshot = "pre-payment-error.png"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            print(f"Iniciando donación para {personal_info['email']} con tarjeta {card_info['card_number'][-4:]}")
            await page.goto(DONATION_URL, timeout=60000)

            # --- Rellenar formulario principal con esperas explícitas ---
            async def wait_and_fill(selector, value):
                locator = page.locator(selector)
                await locator.wait_for(state="visible", timeout=15000)
                await locator.fill(value)

            async def wait_and_click(selector):
                locator = page.locator(selector)
                await locator.wait_for(state="visible", timeout=15000)
                await locator.click()

            # Esta sección se asume que ya no es necesaria en la nueva URL, pero se deja por si acaso.
            # Si la página SÍ requiere estos datos, descomenta las siguientes líneas y asegúrate
            # de que los selectores en el diccionario de arriba son correctos.
            # await wait_and_fill(SELECTORS["rut"], personal_info['rut'])
            # await wait_and_fill(SELECTORS["nombre"], personal_info['nombre'])
            # await wait_and_fill(SELECTORS["apellido"], personal_info['apellido'])
            # await wait_and_fill(SELECTORS["email"], personal_info['email'])
            # ... y así para los demás campos del formulario principal.

            # --- Lógica de llenado de tarjeta ---
            payment_frame = page.frame_locator(SELECTORS["iframe_pago"])
            if not await payment_frame.locator().is_visible():
                 return False, "No se pudo encontrar el iframe del formulario de pago."

            card_selectors = SELECTORS["tarjeta"]

            async def frame_wait_and_fill(selector, value):
                locator = payment_frame.locator(selector)
                await locator.wait_for(state="visible", timeout=15000)
                await locator.fill(value)

            async def frame_wait_and_click(selector):
                locator = payment_frame.locator(selector)
                await locator.wait_for(state="visible", timeout=15000)
                await locator.click()

            # Rellenar los campos de la tarjeta
            await frame_wait_and_fill(card_selectors["numero"], card_info['card_number'])
            await frame_wait_and_fill(card_selectors["nombre_titular"], f"{personal_info['nombre']} {personal_info['apellido']}")
            expiry_date = f"{card_info['expiry_month']}/{card_info['expiry_year'][-2:]}"
            await frame_wait_and_fill(card_selectors["expiracion"], expiry_date)
            await frame_wait_and_fill(card_selectors["cvc"], card_info['cvc'])

            # Hacer clic en "Inscribir tarjeta"
            await frame_wait_and_click(card_selectors["inscribir_tarjeta_checkbox"])

            await page.screenshot(path=pre_payment_screenshot)

            # Hacer clic en el botón final de pagar
            await frame_wait_and_click(card_selectors["boton_pagar"])

            print("Pago enviado. Esperando resultado...")
            await page.wait_for_url('**/*success*', timeout=120000)

            if os.path.exists(pre_payment_screenshot):
                os.remove(pre_payment_screenshot)

            await browser.close()
            return True, "Donación completada exitosamente."

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
