import asyncio
import random
from faker import Faker
from playwright.async_api import async_playwright, TimeoutError

# URL de la página de donación
DONATION_URL = "https://parroquiamariamadredemisericordia.trytoku.com/forms/abonosparroquia?portal=1"
DONATION_AMOUNT = "10000"

# Inicializar Faker para generar datos aleatorios
# Usamos 'es_ES' como una base genérica para nombres en español.
fake = Faker('es_ES')

def generate_rut():
    """Genera un RUT chileno aleatorio con formato XX.XXX.XXX-Y."""
    num = random.randint(5000000, 25000000)
    verifier = random.choice("0123456789K")
    return f"{num // 1000000}.{num // 1000 % 1000:03d}.{num % 1000:03d}-{verifier}"

async def perform_donation(card_info: dict) -> bool:
    """
    Realiza una donación automatizada usando datos aleatorios y la información de tarjeta proporcionada.
    """
    # Generar datos aleatorios para esta sesión
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    rut = generate_rut()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            print(f"Iniciando donación con RUT {rut} y tarjeta {card_info['card_number'][-4:]}")

            # 1. Navegar a la página
            await page.goto(DONATION_URL, timeout=60000)

            # 2. Rellenar información personal con datos aleatorios
            # NOTA: Estos selectores pueden cambiar.
            await page.locator('input[name="rut"]').fill(rut)
            await page.locator('input[name="nombre"]').fill(first_name)
            await page.locator('input[name="apellido"]').fill(last_name)
            await page.locator('input[name="email"]').fill(email)

            # 3. Seleccionar "Donación" y rellenar monto
            await page.locator('select[name="concepto"]').select_option(label="Donación")
            await page.locator('input[placeholder="Monto a donar"]').fill(DONATION_AMOUNT)

            # 4. Registrar el aporte para revelar el botón de pago
            await page.locator('button:has-text("Registrar")').click()

            # 5. Esperar y hacer clic en "Agregar medio de pago"
            # Este botón aparece dinámicamente.
            payment_button = page.locator('button:has-text("Agregar medio de pago")')
            await payment_button.wait_for(state="visible", timeout=30000)
            await payment_button.click()

            # 6. Rellenar datos de la tarjeta en el iframe de pago
            await page.wait_for_timeout(5000) # Espera para que el iframe cargue
            payment_frame = page.frame_locator('iframe[src*="wompi"]')

            if not await payment_frame.locator().is_visible():
                 print("Error: No se pudo encontrar el iframe del formulario de pago.")
                 await browser.close()
                 return False

            await payment_frame.locator('input[name="card-number"]').fill(card_info['card_number'])
            expiry_date = f"{card_info['expiry_month']}/{card_info['expiry_year'][-2:]}"
            await payment_frame.locator('input[name="card-exp"]').fill(expiry_date)
            await payment_frame.locator('input[name="card-cvc"]').fill(card_info['cvc'])
            await payment_frame.locator('input[name="card-holder-name"]').fill(f"{first_name} {last_name}")

            # 7. Enviar el formulario de pago
            await payment_frame.locator('button[type="submit"]').click()

            # 8. Esperar y verificar el resultado
            print("Pago enviado. Esperando resultado...")
            await page.wait_for_url('**/*success*', timeout=90000)

            print("¡Donación exitosa!")
            await browser.close()
            return True

        except TimeoutError:
            print("Error: La operación excedió el tiempo de espera. La donación probablemente falló.")
            await page.screenshot(path="error_screenshot.png")
            print("Se ha guardado una captura de pantalla en: error_screenshot.png")
            await browser.close()
            return False
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")
            await page.screenshot(path="error_screenshot.png")
            print(f"Se ha guardado una captura de pantalla en: error_screenshot.png")
            await browser.close()
            return False

# Bloque de prueba para ejecución independiente
# if __name__ == '__main__':
#     test_card = {"card_number": "4242424242424242", "expiry_month": "12", "expiry_year": "2025", "cvc": "123"}
#     success = asyncio.run(perform_donation(test_card))
#     if success:
#         print("Prueba de donación completada con éxito.")
#     else:
#         print("Prueba de donación fallida.")
