# Bot de Donación Automatizada para Telegram

Este proyecto contiene un bot de Telegram que automatiza el proceso de realizar una donación en la página de la Parroquia María Madre de Misericordia. El bot utiliza tus datos personales y una lista de tarjetas de crédito/débito para intentar realizar la donación y te notifica el resultado directamente en tu chat de Telegram.

**ADVERTENCIA DE SEGURIDAD IMPORTANTE:** Este bot requiere que almacenes información sensible (datos personales y detalles completos de tus tarjetas) en un archivo de configuración (`config.json`). Este método es inherentemente inseguro. Asegúrate de ejecutar este bot en un entorno privado y seguro, y de que nadie más tenga acceso al archivo de configuración. Úsalo bajo tu propio riesgo.

## Requisitos

- Python 3.8 o superior.
- Una cuenta de Telegram.
- Un bot de Telegram con su respectivo token de autenticación.

## Instrucciones de Configuración

Sigue estos pasos cuidadosamente para poner en marcha el bot.

### Paso 1: Descargar el Código

Descarga el código de este repositorio. Generalmente, puedes hacerlo yendo a la página principal del repositorio y seleccionando "Code" -> "Download ZIP". Descomprime el archivo en una carpeta de tu elección.

### Paso 2: Instalar Dependencias

1.  Abre una terminal o línea de comandos.
2.  Navega a la carpeta donde descomprimiste los archivos del proyecto.
3.  Instala las librerías de Python necesarias ejecutando el siguiente comando:
    ```bash
    pip install -r requirements.txt
    ```
4.  Playwright (la herramienta de automatización) necesita descargar los navegadores que controla. Ejecuta este comando para instalarlos:
    ```bash
    playwright install
    ```

### Paso 3: Crear y Configurar tu Bot de Telegram

1.  **Habla con BotFather:** En Telegram, busca el usuario `BotFather` (es el bot oficial para crear otros bots) e inicia una conversación.
2.  **Crea un nuevo bot:** Envía el comando `/newbot`. Sigue las instrucciones para darle un nombre y un nombre de usuario a tu bot.
3.  **Guarda tu token:** Al finalizar, BotFather te dará un **token de acceso (API Token)**. Es una cadena larga de caracteres. Cópialo y guárdalo en un lugar seguro, lo necesitarás en el siguiente paso.

### Paso 4: Rellenar el Archivo de Configuración

1.  En la carpeta del proyecto, encontrarás un archivo llamado `config.json.template`.
2.  Haz una copia de este archivo y renómbrala a `config.json`.
3.  Abre `config.json` con un editor de texto y rellena tus datos.
    *   `telegram_bot_token`: Pega aquí el token que te dio BotFather.
    *   `allowed_user_id`: Tu ID de usuario de Telegram. Esto es para asegurar que solo tú puedas usar el bot. Puedes obtener tu ID hablando con un bot como `@userinfobot`.
    *   `personal_info`: Rellena tus datos personales.
    *   `cards`: Añade una o más tarjetas a la lista. Puedes añadir tantas como quieras, manteniendo el formato.

### Paso 5: Ejecutar el Bot

1.  Abre una terminal en la carpeta del proyecto.
2.  Ejecuta el siguiente comando:
    ```bash
    python bot.py
    ```
3.  Si todo está configurado correctamente, verás un mensaje en la terminal indicando que el bot se ha iniciado.

### Paso 6: Usar el Bot

1.  Abre Telegram y busca el chat con tu bot.
2.  Envía el comando `/start` para verificar que está funcionando.
3.  Envía el comando `/donar` para iniciar el proceso de donación.
    *   El bot intentará realizar la donación con la primera tarjeta de tu lista.
    *   Si falla, te enviará un mensaje y probará con la siguiente.
    *   Si tiene éxito, te lo notificará y se detendrá.

## Nota sobre Selectores Web

El script `automation.py` utiliza "selectores" para encontrar los campos del formulario en la página web. Si la página cambia su estructura en el futuro, es posible que el bot deje de funcionar. En ese caso, sería necesario actualizar los selectores dentro del archivo `automation.py`. Hay comentarios en el código que te guiarán para encontrar los selectores correctos usando las herramientas de desarrollador de tu navegador.
