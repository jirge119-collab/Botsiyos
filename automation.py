import asyncio
import os
from playwright.async_api import async_playwright, TimeoutError, Error

# --- CONFIGURACIÓN DE SELECTORES ---
# Si el bot falla, actualiza el selector del botón de confirmación.
SELECTORS = {
    "confirm_payment_button": 'button:has-text("Pagar ahora")' # Suposición, ajustar si es necesario
}
# ------------------------------------

# La URL ahora es para un pago recurrente, es posible que deba ser actualizada si es dinámica.
DONATION_URL = "https://parroquiamariamadredemisericordia.trytoku.com/recurring/dG9rdV9jYXJkX29uX2ZpbGU?user=cus_6kDcEHFpXiTTwJuljlnmqzwiJTphagWr&portal=1&account=acc_XpxidNAn00eoiSDka9wKEyiQUwH4P6Gw&subscriptions=[\"sub_KsDqoKddW0wjElzEaiYqZRhmOPdzds_1\"]"

async def perform_donation() -> tuple[bool, str]:
    """
    Realiza un pago recurrente haciendo clic en el botón de confirmación.
    """
    pre_payment_screenshot = "pre-payment-error.png"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            print(f"Iniciando pago recurrente en la URL...")
            await page.goto(DONATION_URL, timeout=60000)

            # Esperar y hacer clic en el botón de confirmación
            confirm_button_locator = page.locator(SELECTORS["confirm_payment_button"])
            await confirm_button_locator.wait_for(state="visible", timeout=30000)

            print("Botón de confirmación encontrado. Tomando captura de pantalla pre-pago...")
            await page.screenshot(path=pre_payment_screenshot)

            await confirm_button_locator.click()

            print("Pago enviado. Esperando resultado...")
            await page.wait_for_url('**/*success*', timeout=120000)

            if os.path.exists(pre_payment_screenshot):
                os.remove(pre_payment_screenshot)

            await browser.close()
            return True, "Pago recurrente completado exitosamente."

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
