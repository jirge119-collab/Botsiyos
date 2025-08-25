# Bot de Donación Automatizada v2.5 (Multi-Tarjeta y Configurable)

Esta versión del bot ha sido rediseñada para ser más robusta, configurable y fácil de usar. Ahora puedes gestionar múltiples tarjetas de crédito e intentar la donación con cada una de ellas de forma automática.

**LA CLAVE DEL ÉXITO:** Este bot **SÓLO FUNCIONARÁ** si tú, el usuario, proporcionas los **selectores CSS correctos** para cada campo del formulario en el archivo `automation.py`. La página de donación puede cambiar en cualquier momento, haciendo que los selectores fallen.

## Características Principales
- **Gestión de Múltiples Tarjetas:** Configura una lista de tarjetas de crédito en `config.json`. Si una falla, el bot intentará automáticamente con la siguiente.
- **Altamente Configurable:** La URL de donación y el monto ahora se gestionan desde `config.json`.
- **Comandos Intuitivos:** Todos los comandos ahora usan el prefijo `.` (ej: `.donar`).
- **Diagnóstico de Errores Mejorado:** Si una tarjeta falla, el bot te enviará una captura de pantalla del error específico para esa tarjeta antes de continuar con la siguiente.
- **Gestión de Usuarios:** Un administrador puede autorizar a otros usuarios de Telegram para que usen el bot.

## Instrucciones de Instalación y Uso

### 1. Rellena el Fichero de Configuración
-   Haz una copia de `config.json.template` y renómbrala a `config.json`.
-   Abre `config.json` y rellena **todos** los campos:
    -   `telegram_bot_token`: El token que te da @BotFather en Telegram.
    -   `allowed_user_ids`: Tu ID de usuario de Telegram. Para saber tu ID, puedes iniciar el bot y enviarle el comando `.id`. El primer ID en la lista es el administrador.
    -   `donation_url`: La URL a la página de donación. Ya está pre-configurada con la de Techo Chile.
    -   `donation_amount`: El monto a donar. Ya está pre-configurado en `5000`.
    -   `personal_info`: Tus datos personales (RUT, nombre, etc.).
    -   `credit_cards`: Una lista de **todas** tus tarjetas. Puedes añadir tantas como quieras. Rellena los datos de ejemplo con tus tarjetas reales.

### 2. **ACTUALIZA LOS SELECTORES CSS (PASO OBLIGATORIO)**
La efectividad del bot depende 100% de que los selectores CSS coincidan con la estructura de la página web.
-   **Abre `automation.py`**. Verás un diccionario llamado `SELECTORS`.
-   **Abre la `donation_url`** en tu navegador.
-   Para **CADA CAMPO** del formulario (monto, nombre, número de tarjeta, etc.), haz lo siguiente:
    1.  Clic derecho en el campo del formulario -> **Inspeccionar**.
    2.  En la ventana de desarrollador, busca la línea resaltada (que corresponde al campo).
    3.  Clic derecho en esa línea -> **Copiar > Copiar selector**.
    4.  **Pega** el selector que copiaste en el valor correspondiente dentro del diccionario `SELECTORS` en `automation.py`.
-   **Guarda el archivo `automation.py`**. Los selectores actuales son una guía, pero podrían no funcionar si la página cambia.

### 3. Instala las Dependencias
Abre una terminal en la carpeta del proyecto y ejecuta los siguientes comandos:
```bash
# Instalar las librerías de Python
pip install -r requirements.txt

# Instalar los navegadores para Playwright
playwright install
```

### 4. Ejecuta el Bot
Finalmente, para iniciar el bot, ejecuta:
```bash
python bot.py
```
Si todo está configurado correctamente, verás un mensaje en la terminal y podrás empezar a usar los comandos en Telegram.

## Comandos del Bot
-   `.cmds`: Muestra la lista de todos los comandos disponibles.
-   `.ping`: Responde "pong". Útil para ver si el bot está funcionando.
-   `.id`: Te devuelve tu ID de usuario de Telegram.
-   `.donar`: Inicia el proceso de donación, probando cada una de las tarjetas de tu `config.json` hasta que una funcione.

### Comandos de Administrador
-   `.adduser <ID>`: Permite a otro usuario de Telegram usar el bot.
-   `.listusers`: Muestra la lista de usuarios autorizados.
