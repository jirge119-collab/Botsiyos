# Bot de Donación Automatizada v2

Esta es la segunda versión del bot de Telegram, diseñada para automatizar donaciones con un enfoque en la seguridad y la flexibilidad. A diferencia de la primera versión, este bot no almacena información personal ni de tarjetas en archivos. En su lugar, genera datos personales aleatorios para cada donación y recibe la información de las tarjetas directamente a través de un comando de Telegram.

## Cambios Principales en v2
- **Datos Aleatorios:** El bot genera un RUT, nombre y email nuevos para cada intento de donación.
- **Entrada de Tarjetas por Comando:** Las tarjetas de crédito/débito se proporcionan directamente en el comando `/donar`, en lugar de leerlas de un archivo. Esto es más seguro ya que no se almacenan en disco.
- **Flujo de Automatización Actualizado:** El script ahora maneja un formulario de varios pasos (Registrar, Agregar medio de pago).

## Instrucciones de Configuración

### Paso 1: Descargar el Código
Descarga o clona el código y descomprímelo en una carpeta.

### Paso 2: Instalar Dependencias
1.  Abre una terminal o línea de comandos en la carpeta del proyecto.
2.  Instala las librerías de Python necesarias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Instala los navegadores para Playwright:
    ```bash
    playwright install
    ```

### Paso 3: Configurar el Bot
1.  **Obtén un token de bot de Telegram** hablando con `@BotFather` (si no lo tienes ya).
2.  **Obtén tu ID de usuario de Telegram** hablando con `@userinfobot`.
3.  Haz una copia del archivo `config.json.template` y renómbrala a `config.json`.
4.  Abre `config.json` y rellena tu `telegram_bot_token` y tu `allowed_user_id`. Esto asegura que solo tú puedas usar el bot.

### Paso 4: Ejecutar el Bot
1.  En tu terminal, dentro de la carpeta del proyecto, ejecuta:
    ```bash
    python bot.py
    ```
2.  Si todo está correcto, verás un mensaje indicando que el bot se ha iniciado.

## Cómo Usar el Bot

1.  Abre una conversación con tu bot en Telegram.
2.  Envía `/start` para ver el mensaje de bienvenida y las instrucciones.
3.  Para realizar una donación, envía el comando `/donar` seguido de los datos de tus tarjetas en las líneas siguientes.

### Formato del Comando `/donar`
Cada tarjeta debe estar en una nueva línea y sus datos deben estar separados por comas, sin espacios, en el siguiente orden:
`numero_de_tarjeta,mes_de_expiracion,año_de_expiracion,cvc`

**Ejemplo para una tarjeta:**
```
/donar
1111222233334444,12,2028,123
```

**Ejemplo para múltiples tarjetas:**
```
/donar
1111222233334444,12,2028,123
5555666677778888,06,2027,456
9876543210987654,01,2026,789
```

El bot procesará las tarjetas en el orden en que las enviaste. Si una falla, te lo notificará y continuará con la siguiente. Si una tiene éxito, el proceso se detendrá.
