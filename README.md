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

### Error: "el bot no rellena los campos" o "no se encuentra el elemento"
Este es el error más común y sucede cuando la estructura de la página web cambia. Para solucionarlo, debes actualizar los "selectores" en el archivo `automation.py`.

**Cómo actualizar los selectores:**

1.  **Abre la página de donación** en tu navegador (Chrome, Firefox, etc.).
2.  **Haz clic derecho** en el campo que el bot no está rellenando (por ejemplo, el campo "RUT").
3.  En el menú que aparece, selecciona **"Inspeccionar"** (o "Inspect"). Se abrirá un panel con el código HTML de la página.
4.  Verás una línea de código resaltada. **Haz clic derecho** sobre esa línea.
5.  En el nuevo menú, ve a **Copiar > Copiar selector** (o `Copy > Copy selector`). Esto copiará al portapapeles una cadena de texto como `input#rut` o `#main-content > div > input.rut-field`.
6.  **Abre el archivo `automation.py`** en un editor de texto.
7.  **Busca el diccionario `SELECTORS`** al principio del archivo.
8.  **Pega el selector que copiaste** como el nuevo valor para la clave correspondiente. Por ejemplo, si copiaste el selector para el campo RUT, la línea debería quedar así:
    ```python
    "rut": "input#rut", # <--- Pega tu selector aquí
    ```
9.  **Guarda el archivo** y vuelve a ejecutar el bot.

Repite este proceso para cualquier otro campo que esté fallando.

### Error: "La operación excedió el tiempo de espera"
Si recibes este error, el bot creará dos capturas de pantalla (`pre-payment-error.png` y `post-payment-error.png`) en su carpeta para ayudarte a diagnosticar qué ocurrió. Revisa si los datos se rellenaron correctamente o si apareció un mensaje de error o captcha.
