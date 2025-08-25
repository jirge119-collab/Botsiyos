# Bot de Donación Automatizada v2.1 (con Gestión de Usuarios)

Esta versión del bot de Telegram automatiza donaciones y añade un completo sistema de gestión de usuarios para permitir que varias personas usen el bot de forma segura.

## Características Principales
- **Datos Aleatorios:** Genera un RUT, nombre y email nuevos para cada donación.
- **Entrada de Tarjetas por Comando:** Las tarjetas se proporcionan de forma segura en el comando `/donar`, no se almacenan en disco.
- **Gestión de Usuarios:** Un usuario administrador (el primero en la lista de configuración) puede añadir o eliminar a otros usuarios autorizados.
- **Comandos de Administración:** `/adduser`, `/removeuser`, `/listusers`.
- **Comando de Usuario:** `/id` para que cualquiera pueda obtener su ID de Telegram.

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
    *   `allowed_user_ids`: Esta es la lista de usuarios autorizados.
        *   **Importante:** El **primer ID** de la lista es el **administrador** del bot. Pon tu propio ID de Telegram aquí. Puedes añadir otros IDs si lo deseas. Para encontrar tu ID, puedes iniciar el bot y enviarle el comando `/id`.

### Paso 4: Ejecutar el Bot
En tu terminal, ejecuta: `python bot.py`

## Cómo Usar el Bot

### Comandos Públicos
Cualquier usuario de Telegram puede usar este comando.
- `/id`
  - El bot te responderá con tu ID de usuario de Telegram. Es útil si necesitas dárselo al administrador para que te añada.

### Comandos de Usuario Autorizado
Solo los usuarios en la lista `allowed_user_ids` pueden usar este comando.
- `/donar`
  - Inicia el proceso de donación. Debes proporcionar las tarjetas en las líneas siguientes, usando `|` como separador.
  - **Formato:** `numero_tarjeta|mes_exp|año_exp|cvc`
  - **Ejemplo:**
    ```
    /donar
    1111222233334444|12|2028|123
    5555666677778888|06|2027|456
    ```

### Comandos de Administrador
Solo el **primer usuario** de la lista `allowed_user_ids` puede usar estos comandos.
- `/adduser <ID_del_usuario>`
  - Añade un nuevo usuario a la lista de autorizados.
  - Ejemplo: `/adduser 987654321`
- `/removeuser <ID_del_usuario>`
  - Elimina a un usuario de la lista. No puedes eliminar al administrador.
  - Ejemplo: `/removeuser 987654321`
- `/listusers`
  - Muestra una lista de todos los usuarios actualmente autorizados y quién es el administrador.

## Solución de Problemas

### Error: "La operación excedió el tiempo de espera"

Si recibes un mensaje de error que dice `La operación excedió el tiempo de espera (120s)`, significa que el bot no recibió una confirmación de la página de pago a tiempo.

Para ayudarte a diagnosticar el problema, el bot creará automáticamente dos archivos de imagen en su carpeta:

1.  `pre-payment-error.png`: Una captura de pantalla de cómo se veía la página justo **antes** de que el bot hiciera clic en el botón final de pago. Úsala para verificar que todos los datos de la tarjeta se rellenaron correctamente.
2.  `post-payment-error.png`: Una captura de pantalla de la página en el momento en que se agotó el tiempo de espera. Úsala para ver si apareció algún mensaje de error extraño, un captcha, o si la página simplemente se quedó cargando.

Revisar estas imágenes es el primer paso para entender por qué puede estar fallando el proceso.
