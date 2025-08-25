import asyncio
import os
from playwright.async_api import async_playwright, TimeoutError, Error

# --- CONFIGURACIÓN DE SELECTORES ---
# Si el bot falla, actualiza estos valores.
# Las instrucciones sobre cómo hacerlo están en el archivo README.md.
SELECTORS = {
    # --- Monto y botón inicial ---
    "monto_otro": 'label[for="otherAmount"]',
    "monto_input": 'input[name="amount"]',
    "boton_donar": 'button[type="submit"]', # Botón que avanza al siguiente paso

    # --- Datos Personales ---
    "nombre": 'input[name="name"]',
    "apellido": 'input[name="lastname"]',
    "email": 'input[name="email"]',
    "rut": 'input[name="rut"]',
    "telefono": 'input[name="phone"]',
    "boton_siguiente_datos": 'button[type="submit"]', # Botón para ir al pago

    # --- Iframe y Datos de Tarjeta ---
    # La página de Techo usa un iframe de "Flow", un procesador de pagos chileno.
    "iframe_pago": 'iframe[src*="flow.cl"]',
    "tarjeta": {
        "numero": 'input[name="pan"]',
        "nombre_titular": 'input[name="name"]',
        "expiracion": 'input[name="expiryDate"]', # Formato MM/YY
        "cvc": 'input[name="cvv"]',
        "boton_pagar": 'button[id="btn-pay"]'
    },

    # --- Resultado ---
    # Un selector que SÓLO aparece si el pago fue exitoso.
    "mensaje_exito": 'h1:has-text("¡Tu donación ha sido recibida!")'
}
# ------------------------------------

async def perform_donation(donation_config: dict) -> tuple[bool, str, list[str]]:
    """
    Realiza una donación automatizada, iterando a través de una lista de tarjetas.
    """
    screenshots = []

    for i, card_info in enumerate(donation_config['credit_cards']):
        card_suffix = card_info['card_number'][-4:]
        screenshot_path = f"error_card_{card_suffix}.png"
        print(f"--- Intento {i+1}/{len(donation_config['credit_cards'])} con tarjeta que termina en {card_suffix} ---")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(donation_config['donation_url'], timeout=60000)

                # --- Paso 1: Ingresar el monto ---
                await page.locator(SELECTORS["monto_otro"]).click()
                await page.locator(SELECTORS["monto_input"]).fill(donation_config['donation_amount'])
                await page.locator(SELECTORS["boton_donar"]).click()

                # --- Paso 2: Rellenar datos personales ---
                await page.wait_for_selector(SELECTORS["nombre"], timeout=15000)
                personal_info = donation_config['personal_info']
                await page.locator(SELECTORS["nombre"]).fill(personal_info['nombre'])
                await page.locator(SELECTORS["apellido"]).fill(personal_info['apellido'])
                await page.locator(SELECTORS["email"]).fill(personal_info['email'])
                await page.locator(SELECTORS["rut"]).fill(personal_info['rut'])
                # El campo teléfono no está en el config original, se puede añadir si es necesario.
                # await page.locator(SELECTORS["telefono"]).fill("912345678")
                await page.locator(SELECTORS["boton_siguiente_datos"]).click()

                # --- Paso 3: Rellenar datos de tarjeta en el iframe ---
                payment_frame_locator = page.frame_locator(SELECTORS["iframe_pago"])
                card_selectors = SELECTORS["tarjeta"]

                await payment_frame_locator.locator(card_selectors["numero"]).wait_for(state="visible", timeout=20000)

                await payment_frame_locator.locator(card_selectors["numero"]).fill(card_info['card_number'])
                await payment_frame_locator.locator(card_selectors["nombre_titular"]).fill(f"{personal_info['nombre']} {personal_info['apellido']}")
                expiry_date = f"{card_info['expiry_month']}{card_info['expiry_year'][-2:]}"
                await payment_frame_locator.locator(card_selectors["expiracion"]).fill(expiry_date)
                await payment_frame_locator.locator(card_selectors["cvc"]).fill(card_info['cvc'])

                await payment_frame_locator.locator(card_selectors["boton_pagar"]).click()

                # --- Paso 4: Verificar el resultado ---
                # Esperamos por el mensaje de éxito. Si no aparece, saltará al `except`.
                await page.wait_for_selector(SELECTORS["mensaje_exito"], timeout=90000)

                print(f"✅ ¡Donación exitosa con la tarjeta {card_suffix}!")
                # Si tuvimos errores previos, los limpiamos
                for s in screenshots:
                    if os.path.exists(s): os.remove(s)

                await browser.close()
                return True, f"Donación completada con tarjeta terminada en {card_suffix}.", []

            except (TimeoutError, Error) as e:
                error_message = str(e).splitlines()[0]
                print(f"❌ Fallo de Playwright con tarjeta {card_suffix}: {error_message}")
                await page.screenshot(path=screenshot_path)
                screenshots.append(screenshot_path)
                await browser.close()
                # Continuamos con la siguiente tarjeta en el bucle

            except Exception as e:
                error_text = f"Ocurrió un error inesperado con tarjeta {card_suffix}: {e}"
                print(error_text)
                await page.screenshot(path=screenshot_path)
                screenshots.append(screenshot_path)
                await browser.close()
                # Continuamos con la siguiente tarjeta

    # Si el bucle termina sin éxito
    return False, "Todas las tarjetas fallaron.", screenshots
