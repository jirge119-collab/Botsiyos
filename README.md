# Bot Verificador de Tarjetas para Telegram

Este es un bot de Telegram diseñado para ayudar a validar números de tarjetas de crédito o débito. Su propósito principal es verificar que un número de tarjeta sea formalmente correcto (para evitar errores de tipeo en formularios) e identificar su marca.

## Características

- **Validación de Formato:** Comprueba si un número de tarjeta es válido según el **algoritmo de Luhn**.
- **Identificación de Marca:** Detecta la marca de la tarjeta (Visa, Mastercard, American Express, etc.).
- **Comando de Verificación Simple (`/validate`):** Ofrece una validación rápida de formato y marca.
- **Comando de Verificación Completa (`/check`):** Añade una comprobación de estado (simulada) a través de una pasarela de pago.
- **Extensible:** Diseñado para que un desarrollador pueda integrar fácilmente una pasarela de pago real (como Stripe, Braintree, etc.).

## Instalación y Configuración

Sigue estos pasos para poner en marcha tu propio bot.

### 1. Requisitos Previos

- Python 3.8 o superior.
- Una cuenta de Telegram.

### 2. Obtener el Código

Clona este repositorio o descarga los archivos en una carpeta de tu ordenador.

### 3. Instalar Dependencias

Abre una terminal en la carpeta del proyecto y ejecuta el siguiente comando para instalar las bibliotecas necesarias:

```bash
pip install -r requirements.txt
```

### 4. Obtener un Token de Bot de Telegram

Necesitas un "token" para que tu código se pueda conectar con Telegram.

1.  Abre Telegram y busca al bot llamado `@BotFather`.
2.  Inicia una conversación con él y envía el comando `/newbot`.
3.  Sigue las instrucciones: dale un nombre a tu bot y un nombre de usuario (que debe terminar en `bot`, ej. `MiVerificadorBot`).
4.  **BotFather** te dará un token. Será una cadena larga de letras y números, como `1234567890:ABC-DEF1234ghIkl-zyx57W2v1u1234567890`.
5.  **¡Guarda este token! Es secreto y muy importante.**

### 5. Configurar el Token

En la misma carpeta donde tienes los archivos del bot, crea un nuevo archivo llamado `.env`. Ábrelo y escribe lo siguiente, reemplazando `TU_TOKEN_AQUI` con el token que te dio BotFather:

```
TELEGRAM_TOKEN=TU_TOKEN_AQUI
```

## Ejecutar el Bot

Una vez que hayas configurado todo, puedes iniciar el bot. Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
python bot.py
```

Si todo está correcto, verás un mensaje en la terminal indicando que el bot se ha iniciado. ¡Ya puedes hablar con tu bot en Telegram!

## Cómo Usar el Bot

Abre una conversación con tu bot en Telegram y usa los siguientes comandos:

- `/start`: Muestra el mensaje de bienvenida.
- `/help`: Explica los comandos disponibles.
- `/validate <numero_de_tarjeta>`: Verifica el formato y la marca de la tarjeta.
  - *Ejemplo:* `/validate 49927398716`
- `/check <numero_de_tarjeta>`: Realiza la misma verificación que `/validate` y además comprueba el estado en la pasarela de pago (que por defecto no está configurada).
  - *Ejemplo:* `/check 5123456789012345`

## Para Desarrolladores: Configurar una Pasarela de Pago

El comando `/check` está preparado para que puedas conectarlo a una pasarela de pago real y verificar si una tarjeta está activa.

Para ello, debes editar el archivo `gateway.py`:

1.  **Abre `gateway.py`:** Encontrarás una función `check_card_status`.
2.  **Sigue las instrucciones:** El archivo contiene comentarios detallados y un ejemplo conceptual de cómo podrías integrar una pasarela como Stripe.
3.  **Instala la biblioteca necesaria:** Por ejemplo, `pip install stripe`.
4.  **Gestiona tus claves de API de forma segura:** Nunca escribas tus claves secretas directamente en el código. Usa variables de entorno (cargándolas con `os.getenv` como se hace con el token del bot).
5.  **Modifica la función:** Reemplaza la lógica de ejemplo con la implementación real de tu pasarela de pago.

---
*Este bot es una herramienta de utilidad y no almacena ninguna información de las tarjetas introducidas.*
