import asyncio
import random
import os
from faker import Faker
from playwright.async_api import async_playwright, TimeoutError

# URL de la página de donación
DONATION_URL = "https://parroquiamariamadredemisericordia.trytoku.com/forms/abonosparroquia?portal=1"
DONATION_AMOUNT = "10000"

# Inicializar Faker
fake = Faker('es_ES')

def generate_rut():
    """Genera un RUT chileno aleatorio con formato XX.XXX.XXX-Y."""
    num = random.randint(5000000, 25000000)
    verifier = random.choice("0123456789K")
    return f"{num // 1000000}.{num // 1000 % 1000:03d}.{num % 1000:03d}-{verifier}"

async def perform_donation(card_info: dict) -> tuple[bool, str]:
    """
    Realiza una donación automatizada.
    Returns:
        Una tupla (bool, str) donde el bool indica el éxito y el str es el mensaje de resultado.
    """
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    rut = generate_rut()

    pre_payment_screenshot = "pre-payment-error.png"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            print(f"Iniciando donación con RUT {rut} y tarjeta {card_info['card_number'][-4:]}")
            await page.goto(DONATION_URL, timeout=60000)

            await page.locator('input[name="rut"]').fill(rut)
            await page.locator('input[name="nombre"]').fill(first_name)
            await page.locator('input[name="apellido"]').fill(last_name)
            await page.locator('input[name="email"]').fill(email)

            await page.locator('select[name="concepto"]').select_option(label="Donación")
            await page.locator('input[placeholder="Monto a donar"]').fill(DONATION_AMOUNT)

            await page.locator('button:has-text("Registrar")').click()

            payment_button = page.locator('button:has-text("Agregar medio de pago")')
            await payment_button.wait_for(state="visible", timeout=30000)
            await payment_button.click()

            await page.wait_for_timeout(5000)
            payment_frame = page.frame_locator('iframe[src*="wompi"]')

            if not await payment_frame.locator().is_visible():
                 return False, "No se pudo encontrar el iframe del formulario de pago."

            await payment_frame.locator('input[name="card-number"]').fill(card_info['card_number'])
            expiry_date = f"{card_info['expiry_month']}/{card_info['expiry_year'][-2:]}"
            await payment_frame.locator('input[name="card-exp"]').fill(expiry_date)
            await payment_frame.locator('input[name="card-cvc"]').fill(card_info['cvc'])
            await payment_frame.locator('input[name="card-holder-name"]').fill(f"{first_name} {last_name}")

            # Tomar captura de pantalla justo antes de pagar para diagnóstico
            await page.screenshot(path=pre_payment_screenshot)

            await payment_frame.locator('button[type="submit"]').click()

            print("Pago enviado. Esperando resultado...")
            await page.wait_for_url('**/*success*', timeout=120000) # Timeout aumentado

            # Si la donación es exitosa, limpiar la captura de pre-pago
            if os.path.exists(pre_payment_screenshot):
                os.remove(pre_payment_screenshot)

            await browser.close()
            return True, "Donación completada exitosamente."

        except TimeoutError:
            print("Timeout esperando la página de éxito. Asumiendo fallo y buscando mensaje de error.")
            error_message = f"La operación excedió el tiempo de espera (120s). Revise las capturas '{pre_payment_screenshot}' y 'post-payment-error.png' para diagnóstico."

            # Renombrar la captura de pre-pago para que sea claro que es parte de un error
            # La captura post-pago se toma a continuación

            try:
                # Intentar encontrar un mensaje de error visible
                error_locator = payment_frame.locator('div[class*="error"], div[class*="message"], span[class*="error"]').first
                await error_locator.wait_for(state="visible", timeout=5000)
                message_text = await error_locator.text_content()
                if message_text:
                    error_message = message_text.strip()
            except Exception:
                print("No se pudo capturar el mensaje de error específico.")

            await page.screenshot(path="post-payment-error.png")
            await browser.close()
            return False, error_message

        except Exception as e:
            error_text = f"Ocurrió un error inesperado: {e}"
            print(error_text)
            await page.screenshot(path="post-payment-error.png")
            await browser.close()
            return False, error_text
