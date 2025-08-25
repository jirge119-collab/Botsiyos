# Bot de Donación Automatizada v2.2 (Datos Personales Editables)

Esta versión del bot de Telegram automatiza donaciones y combina un sistema de gestión de usuarios con la capacidad de usar datos personales fijos y editables.

## Características Principales
- **Datos Personales Fijos:** Usa un set de datos personales (RUT, nombre, email) definidos en `config.json` para cada donación.
- **Entrada de Tarjetas por Comando:** Las tarjetas se proporcionan de forma segura en el comando `/donar`, no se almacenan en disco.
- **Gestión de Usuarios:** Un usuario administrador puede añadir o eliminar a otros usuarios autorizados.
- **Diagnóstico de Errores Mejorado:** En caso de fallo, el bot envía una captura de pantalla del error directamente a Telegram.

## Instrucciones de Configuración

### Paso 1: Descargar el Código
Descarga o clona el código del proyecto.

### Paso 2: Instalar Dependencias
1.  Abre una terminal en la carpeta del proyecto.
2.  Instala las librerías necesarias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Instala los navegadores para Playwright:
    ```bash
    playwright install
    ```

### Paso 3: Configurar el Bot
1.  Crea un bot en Telegram hablando con `@BotFather` para obtener tu `token`.
2.  Copia `config.json.template` y renómbralo a `config.json`.
3.  Abre `config.json` y edítalo:
    *   `telegram_bot_token`: Pega aquí el token de tu bot.
    *   `allowed_user_ids`: Lista de usuarios autorizados. El **primer ID** es el **administrador**.
    *   `personal_info`: Rellena esta sección con tus datos personales (RUT, nombre, apellido, email). Estos datos se usarán en todos los intentos de donación.

### Paso 4: Ejecutar el Bot
En tu terminal, ejecuta: `python bot.py`

## Cómo Usar el Bot

### Comandos Públicos
- `/id`
  - El bot te responderá con tu ID de usuario de Telegram.

### Comandos de Usuario Autorizado
- `/donar`
  - Inicia el proceso de donación usando los datos de `personal_info`. Debes proporcionar las tarjetas en las líneas siguientes (`numero_tarjeta|mes_exp|año_exp|cvc`).
  - **Ejemplo:**
    ```
    /donar
    1111222233334444|12|2028|123
    ```

### Comandos de Administrador
Solo el administrador puede usar estos comandos.
- `/adduser <ID_del_usuario>`
- `/removeuser <ID_del_usuario>`
- `/listusers`

## Solución de Problemas
Si recibes un error de "tiempo de espera excedido", el bot te enviará una captura de pantalla para ayudarte a ver qué ocurrió en la página de pago. Revisa si los datos se rellenaron correctamente o si apareció un mensaje de error o captcha.
