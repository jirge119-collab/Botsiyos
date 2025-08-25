# Bot de Donación Automatizada v2.4 (Formulario Completo)

Esta es la versión más reciente del bot, que vuelve a implementar la lógica para rellenar un formulario de donación completo, incluyendo datos personales y de tarjeta de crédito.

**LA CLAVE DEL ÉXITO:** Este bot **SÓLO FUNCIONARÁ** si tú, el usuario, proporcionas los **selectores CSS correctos** para cada campo del formulario en el archivo `automation.py`.

## Características
- **Relleno de Formulario Completo:** Intenta rellenar datos personales y de tarjeta.
- **Selectores Configurables:** Todos los selectores están en un solo lugar (`automation.py`) para que los puedas actualizar fácilmente.
- **Gestión de Usuarios:** Un administrador puede autorizar a otros usuarios.
- **Diagnóstico de Errores:** Envía capturas de pantalla a Telegram si algo falla.

## Instrucciones

### 1. Configurar el Bot
- Copia `config.json.template` a `config.json`.
- Rellena tu `telegram_bot_token`, la lista de `allowed_user_ids` (poniendo tu ID primero como admin) y la sección `personal_info`.

### 2. **ACTUALIZAR LOS SELECTORES (PASO OBLIGATORIO)**
- **Abre `automation.py`**. Verás un diccionario llamado `SELECTORS` al principio.
- **Abre la página web** de la donación en tu navegador.
- Para **CADA CAMPO** del formulario (RUT, nombre, número de tarjeta, etc.), haz lo siguiente:
    1. Clic derecho en el campo -> **Inspeccionar**.
    2. En el código que aparece, clic derecho en la línea resaltada -> **Copiar > Copiar selector**.
    3. **Pega** el selector que copiaste en el valor correspondiente dentro del diccionario `SELECTORS` en `automation.py`.
- **Guarda el archivo `automation.py`**.

### 3. Instalar Dependencias y Ejecutar
- Abre una terminal en la carpeta del bot.
- Ejecuta `pip install -r requirements.txt`.
- Ejecuta `playwright install`.
- Ejecuta `python bot.py`.

## Comandos
- Escribe `.cmds` para ver la lista de comandos.
- `/donar <numero_tarjeta|mes|año|cvc>`: Inicia el proceso de donación con la tarjeta indicada.
