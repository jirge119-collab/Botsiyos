# -*- coding: utf-8 -*-

def check_card_status(card_number: str) -> str:
    """
    Esta es una función de marcador de posición para verificar el estado de una tarjeta.
    NO realiza una verificación real. Devuelve un estado predeterminado.

    Para una implementación real, necesitarías integrar una pasarela de pago.
    """

    # --- INSTRUCCIONES PARA EL DESARROLLADOR ---
    #
    # 1. Elige una pasarela de pago (ej. Stripe, Braintree, Adyen, etc.).
    # 2. Obtén tus claves de API (API Key y Secret Key) de esa pasarela.
    #    ¡NUNCA las escribas directamente en el código! Usa variables de entorno.
    #
    # 3. Instala la biblioteca de Python para esa pasarela (ej. `pip install stripe`).
    #
    # 4. Reemplaza el código de abajo con la lógica de tu pasarela.
    #
    # Ejemplo conceptual con Stripe (este código no funcionará sin una configuración real):
    #
    # import stripe
    # import os
    #
    # # Carga tu clave secreta de API desde una variable de entorno
    # stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    #
    # try:
    #     # Intenta crear un "PaymentMethod" o un "Customer" para verificar la tarjeta.
    #     # La forma exacta de hacer esto puede cambiar, consulta la documentación de Stripe.
    #     # Esto podría incurrir en costos o estar sujeto a las políticas de la pasarela.
    #     payment_method = stripe.PaymentMethod.create(
    #         type="card",
    #         card={"token": "tok_visa"}, # En un caso real, generarías un token en el frontend.
    #     )
    #     # Si la llamada tiene éxito, la tarjeta es probablemente válida y activa.
    #     return "Activa (Verificación simulada exitosa)"
    #
    # except stripe.error.CardError as e:
    #     # La tarjeta fue rechazada por alguna razón.
    #     # err = e.error
    #     # print(f"Código: {err.code}, Mensaje: {err.message}")
    #     return f"Inactiva o Inválida ({e.error.message})"
    #
    # except Exception as e:
    #     # Otro tipo de error (ej. problema de red, clave de API incorrecta).
    #     return f"Error de Verificación ({str(e)})"
    #

    # Mensaje predeterminado porque la pasarela no está configurada
    return "Estado: No verificado (Pasarela no configurada)"
