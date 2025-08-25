# Guía de Instalación y Uso del Bot de Donaciones para Telegram

¡Hola! Esta guía te llevará paso a paso a través de todo el proceso para poner en funcionamiento tu bot de Telegram. El bot está diseñado para automatizar el proceso de donación en un sitio web específico usando la aplicación Termux en Android.

Sigue cada paso con atención.

---

## Índice
1. [Paso 1: Preparar el Entorno en Termux](#paso-1-preparar-el-entorno-en-termux)
2. [Paso 2: Crear y Configurar tu Bot de Telegram](#paso-2-crear-y-configurar-tu-bot-de-telegram)
3. [Paso 3: Obtener los Selectores del Formulario Web (¡MUY IMPORTANTE!)](#paso-3-obtener-los-selectores-del-formulario-web-muy-importante)
4. [Paso 4: Configurar y Ejecutar el Script del Bot](#paso-4-configurar-y-ejecutar-el-script-del-bot)
5. [Paso 5: Usar el Bot](#paso-5-usar-el-bot)
6. [Solución de Problemas Comunes](#solución-de-problemas-comunes)

---

### Paso 1: Preparar el Entorno en Termux

Termux es una aplicación para Android que te da un entorno de línea de comandos. La usaremos para ejecutar nuestro bot.

1.  **Instala Termux**: Descárgalo desde F-Droid para asegurar que recibes las últimas actualizaciones. Búscalo en la tienda de F-Droid o en su sitio web.

2.  **Actualiza los paquetes**: Abre Termux y ejecuta los siguientes comandos. Escribe uno, presiona Enter, espera a que termine, y luego escribe el siguiente.
    ```bash
    pkg update
    pkg upgrade
    ```

3.  **Instala las herramientas necesarias**: Necesitamos Python (el lenguaje del bot), Chromium (el navegador que se usará en segundo plano) y algunas herramientas de desarrollo.
    ```bash
    pkg install python git clang make
    ```

4.  **Instala las librerías de Python**: Estas son las dependencias que el script `bot.py` necesita para funcionar.
    ```bash
    pip install python-telegram-bot selenium
    ```

5. **Instala Chromium y Chromedriver**: Selenium necesita un navegador (Chromium) y un controlador (Chromedriver) para poder interactuar con las páginas web.
    ```bash
    # Instala el navegador Chromium
    pkg install chromium

    # Instala el controlador para el navegador
    pkg install chromedriver
    ```
    **Nota Importante**: `chromedriver` debe ser compatible con la versión de `chromium` que instalaste. Generalmente, al instalarlos desde `pkg`, se instalan versiones compatibles. Si tienes problemas, este suele ser el motivo.

---

### Paso 2: Crear y Configurar tu Bot de Telegram

1.  **Habla con BotFather**: En Telegram, busca el bot llamado `@BotFather` (es el oficial, tiene una marca de verificación azul).
2.  **Crea un nuevo bot**:
    *   Envía el comando `/newbot`.
    *   BotFather te pedirá un nombre para tu bot (ej: "Bot de Donaciones").
    *   Luego te pedirá un nombre de usuario, que debe terminar en `bot` (ej: `midonacion_bot`).
3.  **Guarda tu Token**: Si el nombre de usuario está disponible, BotFather te felicitará y te dará un **Token de API**. Es una cadena larga de letras y números, algo como `1234567890:ABC-DEF1234ghIkl-zyx57W2v1u1234567890`.
    **¡Este token es secreto! No lo compartas con nadie.**

4.  **Añade el Token al script**:
    *   Abre el archivo `bot.py` (puedes usar un editor de texto en tu teléfono o computadora).
    *   Busca esta línea cerca del principio del archivo:
        ```python
        TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
        ```
    *   Reemplaza `'YOUR_TELEGRAM_BOT_TOKEN'` con el token que te dio BotFather. Asegúrate de que el token quede entre las comillas simples.
        ```python
        # Ejemplo:
        TOKEN = '1234567890:ABC-DEF1234ghIkl-zyx57W2v1u1234567890'
        ```

---

### Paso 3: Obtener los Selectores del Formulario Web (¡MUY IMPORTANTE!)

Este es el paso más técnico, pero crucial. Como no puedo ver el contenido de la página web (requiere JavaScript), **necesito que tú encuentres las "direcciones" de cada campo del formulario**.

Usa un navegador de escritorio (Chrome, Firefox) para esto.

1.  **Abre la página de donación** en tu navegador: [https://parroquiamariamadredemisericordia.trytoku.com/forms/abonosparroquia?portal=1](https://parroquiamariamadredemisericordia.trytoku.com/forms/abonosparroquia?portal=1)

2.  **Haz clic derecho** sobre el primer campo del formulario, por ejemplo, donde dice "Nombres", y en el menú que aparece, selecciona **"Inspeccionar"** o **"Inspect"**.

    ![Ejemplo de menú inspeccionar](https://i.imgur.com/Q3Q9g5l.png)

3.  Se abrirá una ventana de herramientas para desarrolladores. Verás el código HTML de la página. Una línea estará resaltada, algo así:
    ```html
    <input type="text" class="form-control" name="name" id="name" value="" required>
    ```

4.  **Busca el atributo `id` o `name`**. En el ejemplo de arriba, el `id` es `"name"` y el `name` también es `"name"`. El `id` es el mejor selector.

5.  **Anota el `id`** para el campo "Nombres". En este caso, es `name`.

6.  **Repite este proceso para CADA CAMPO** del formulario que el bot necesita rellenar. Aquí está la lista de los que necesitas buscar y dónde ponerlos en el archivo `bot.py`:

    *   Nombres -> `id_del_campo_nombre`
    *   Apellidos -> `id_del_campo_apellido`
    *   Email -> `id_del_campo_email`
    *   Celular -> `id_del_campo_celular`
    *   Cédula -> `id_del_campo_cedula`
    *   Valor (Monto) -> `id_del_campo_valor`
    *   Número de tarjeta -> `id_del_campo_numero_tarjeta`
    *   Nombre del tarjetahabiente -> `id_del_campo_nombre_tarjetahabiente`
    *   Mes de expiración -> `id_del_campo_mes_expiracion`
    *   Año de expiración -> `id_del_campo_ano_expiracion`
    *   Código de seguridad (CVV) -> `id_del_campo_cvv`
    *   Checkbox de "Acepto los Términos" -> `id_del_checkbox_terminos`

    **Si un campo no tiene `id`**:
    *   Busca el atributo `name`. Si lo encuentras, lo usarás con `By.NAME`.
    *   Si no tiene ni `id` ni `name`, haz clic derecho sobre la línea de código HTML > `Copy` > `Copy XPath`. Este será tu selector, y lo usarás con `By.XPATH`.

7.  **Actualiza `bot.py`** con los IDs que encontraste. Por ejemplo, si para "Nombres" encontraste el `id="name"`, cambiarías la línea en `bot.py` así:
    ```python
    # DE:
    'name': (By.ID, 'id_del_campo_nombre'),
    # A:
    'name': (By.ID, 'name'),
    ```
    Si usaste `name` o `XPath`, también cambia `By.ID` por `By.NAME` o `By.XPATH` respectivamente.

---

### Paso 4: Configurar y Ejecutar el Script del Bot

1.  **Abre `bot.py` por última vez**:
    *   Verifica que tu **Token** esté puesto.
    *   Rellena tu **información personal** en las variables `NAME`, `LAST_NAME`, `EMAIL`, etc.
    *   Verifica que todos los **selectores** del `Paso 3` estén correctos.

2.  **Transfiere `bot.py` a tu teléfono**: Si editaste el archivo en una PC, muévelo a tu dispositivo Android. En Termux, los archivos suelen estar en `/data/data/com.termux/files/home`.

3.  **Ejecuta el bot**: Abre Termux y navega a la carpeta donde guardaste `bot.py`. Luego, ejecuta:
    ```bash
    python bot.py
    ```

4.  Si todo está bien, verás el mensaje: `Bot iniciado. Envíale un mensaje para empezar.` ¡El bot ya está funcionando! Para detenerlo, vuelve a Termux y presiona `Ctrl + C`.

---

### Paso 5: Usar el Bot

1.  Ve al chat con tu bot en Telegram.
2.  Envíale un mensaje con los datos de la tarjeta que quieres usar, separados por `|` (sin espacios). El formato es:
    `numero_de_tarjeta|nombre_del_titular|mes_de_vencimiento|año_de_vencimiento|cvv`

    **Ejemplo**:
    `4111111111111111|Juan Perez|12|2025|123`

3.  El bot recibirá el mensaje, abrirá la página web en segundo plano, rellenará todos los datos (los tuyos y los de la tarjeta) e intentará completar la donación. Te notificará el resultado.

---

### Solución de Problemas Comunes

*   **Error `command not found`**: Significa que no instalaste la herramienta. Revisa los comandos del `Paso 1`.
*   **Error `ModuleNotFoundError`**: Te faltó instalar una librería de Python. Revisa el comando `pip install` del `Paso 1`.
*   **Error relacionado con `chromedriver` o `selenium`**: Generalmente, la versión de `chromedriver` y `chromium` no coincide. Asegúrate de haberlos instalado como se indica. Otra causa puede ser que Termux no encuentra el `chromedriver`.
*   **El bot se ejecuta pero no rellena los campos del formulario**: ¡Casi seguro que los selectores del `Paso 3` son incorrectos! Vuelve a inspeccionar la página con mucho cuidado. A veces las páginas cambian y los `id` se actualizan.
*   **El bot dice "La donación pudo haber fallado"**: Puede que el mensaje de "Gracias" en la página haya cambiado, o que la donación realmente falló (tarjeta rechazada, etc.). El bot también te enviará una captura de pantalla del error para que puedas ver qué pasó.
