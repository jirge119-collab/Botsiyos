import asyncio
from playwright.async_api import async_playwright, TimeoutError

# URL de la página de donación
DONATION_URL = "https://parroquiamariamadredemisericordia.trytoku.com/forms/abonosparroquia?portal=1"
DONATION_AMOUNT = "5000"

async def perform_donation(personal_info: dict, card_info: dict) -> bool:
    """
    Realiza una donación automatizada en la página web.

    Args:
        personal_info: Un diccionario con los datos personales (first_name, last_name, email, phone).
        card_info: Un diccionario con los datos de una tarjeta (card_number, expiry_month, expiry_year, cvc).

    Returns:
        True si la donación fue exitosa, False en caso contrario.
    """
    async with async_playwright() as p:
        # Puedes cambiar a headless=False para ver el navegador en acción mientras se ejecuta el script.
        # Esto es útil para depurar si algo falla.
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            print(f"Iniciando donación para {personal_info['email']} con tarjeta que termina en {card_info['card_number'][-4:]}")

            # 1. Navegar a la página
            await page.goto(DONATION_URL, timeout=60000)

            # 2. Rellenar información personal
            # NOTA: Los selectores pueden cambiar. Si el bot falla, usa las herramientas de desarrollador
            # de tu navegador (clic derecho -> Inspeccionar) para encontrar el selector correcto.
            await page.locator('input[name="nombre"]').fill(personal_info['first_name'])
            await page.locator('input[name="apellido"]').fill(personal_info['last_name'])
            await page.locator('input[name="email"]').fill(personal_info['email'])
            await page.locator('input[name="celular"]').fill(personal_info['phone'])

            # 3. Rellenar el monto de la donación
            await page.locator('input[placeholder="Monto a donar"]').fill(DONATION_AMOUNT)

            # 4. Hacer clic en el botón para pagar con tarjeta
            # Esto podría abrir el formulario de pago
            await page.locator('button:has-text("Pagar")').click()

            # Pequeña espera para que aparezca el formulario de pago, que puede estar en un iframe.
            await page.wait_for_timeout(5000)

            # 5. Rellenar datos de la tarjeta
            # Los formularios de pago a menudo están dentro de un 'iframe'.
            # Este es el selector más probable que necesites ajustar.
            # Intenta buscar iframes con 'wompi' o 'payment' en su URL o título.
            payment_frame_locator = page.frame_locator('iframe[src*="wompi"]') # Suposición basada en pasarelas comunes

            # Si el iframe no se encuentra, el bot fallará aquí.
            if not await payment_frame_locator.locator().is_visible():
                 print("Error: No se pudo encontrar el iframe del formulario de pago. El sitio puede haber cambiado.")
                 await browser.close()
                 return False

            payment_frame = payment_frame_locator

            await payment_frame.locator('input[name="card-number"]').fill(card_info['card_number'])

            # El formato de la fecha de expiración suele ser MM/YY
            expiry_date = f"{card_info['expiry_month']}/{card_info['expiry_year'][-2:]}"
            await payment_frame.locator('input[name="card-exp"]').fill(expiry_date)

            await payment_frame.locator('input[name="card-cvc"]').fill(card_info['cvc'])

            # 6. Enviar el formulario de pago
            # Busca el botón final de pago dentro del iframe.
            await payment_frame.locator('button[type="submit"]').click()

            # 7. Esperar y verificar el resultado
            # Después de pagar, la página a menudo redirige a una página de éxito o muestra un mensaje.
            # Esperamos un máximo de 90 segundos por una URL que indique éxito.
            print("Pago enviado. Esperando resultado...")
            await page.wait_for_url('**/*success*', timeout=90000)

            print("¡Donación exitosa!")
            await browser.close()
            return True

        except TimeoutError:
            print("Error: La operación excedió el tiempo de espera. La donación probablemente falló o la página es muy lenta.")
            print(f"URL final: {page.url}")
            await browser.close()
            return False
        except Exception as e:
            print(f"Ocurrió un error inesperado durante la automatización: {e}")
            # Guardar una captura de pantalla puede ayudar a depurar
            screenshot_path = "error_screenshot.png"
            await page.screenshot(path=screenshot_path)
            print(f"Se ha guardado una captura de pantalla en: {screenshot_path}")
            await browser.close()
            return False

# Para probar este script de forma independiente, puedes descomentar las siguientes líneas
# y ejecutar `python automation.py` desde tu terminal.
# if __name__ == "__main__":
#     # Datos de prueba (no usar datos reales aquí)
#     test_personal_info = {"first_name": "Test", "last_name": "User", "email": "test@example.com", "phone": "123456789"}
#     test_card_info = {"card_number": "4242424242424242", "expiry_month": "12", "expiry_year": "2025", "cvc": "123"}
#     # Ejecutar la prueba
#     success = asyncio.run(perform_donation(test_personal_info, test_card_info))
#     if success:
#         print("Prueba de donación completada con éxito.")
#     else:
#         print("Prueba de donación fallida.")
