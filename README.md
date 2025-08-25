# Bot de Donación Automatizada para Telegram

Este proyecto contiene un bot de Telegram diseñado para automatizar el proceso de donación en una página web específica. El bot puede manejar una lista de tarjetas y probarlas una por una hasta que el pago sea exitoso.

**ADVERTENCIA DE SEGURIDAD:** Este bot maneja información financiera extremadamente sensible (números de tarjetas de crédito). Úsalo bajo tu propio riesgo y asegúrate de que el bot se ejecuta en un entorno seguro. Nunca compartas tu token de bot de Telegram ni expongas tus datos de tarjetas. Se recomienda encarecidamente utilizar este bot únicamente en un chat privado contigo mismo.

## Características

-   Rellena formularios con datos aleatorios.
-   Prueba una lista de tarjetas de crédito/débito en secuencia.
-   Notifica el resultado de cada intento de pago.
-   Toma una captura de pantalla si un pago falla y la envía por Telegram.
-   Sistema de permisos para controlar quién puede usar el bot.

## Prerrequisitos

-   Python 3.8 o superior
-   `pip` (gestor de paquetes de Python)

## 1. Configuración Inicial

Sigue estos pasos para dejar el bot listo para funcionar.

### a. Descargar el código

Descarga todos los archivos de este proyecto y guárdalos en una carpeta en tu ordenador.

### b. Instalar dependencias

Abre una terminal o línea de comandos, navega a la carpeta donde guardaste los archivos y ejecuta el siguiente comando para instalar las librerías de Python necesarias:

```bash
pip install -r requirements.txt
```

### c. Instalar los navegadores de Playwright

Playwright necesita descargar los navegadores que utiliza para la automatización. Ejecuta este comando en tu terminal:

```bash
playwright install
```

### d. Obtener un Token de Bot de Telegram

1.  Habla con [@BotFather](https://t.me/BotFather) en Telegram.
2.  Crea un nuevo bot enviando el comando `/newbot`.
3.  Sigue las instrucciones y BotFather te dará un **token**. Se verá algo como `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`.
4.  Copia este token. Es tu secreto para controlar el bot.

### e. Configurar la variable de entorno

Para que el bot pueda usar el token de forma segura, debes configurarlo como una variable de entorno.

**En Windows:**
```bash
set TELEGRAM_BOT_TOKEN="TU_TOKEN_AQUI"
```

**En macOS/Linux:**
```bash
export TELEGRAM_BOT_TOKEN="TU_TOKEN_AQUI"
```

**Importante:** Reemplaza `"TU_TOKEN_AQUI"` con el token que te dio BotFather. Debes ejecutar este comando en la misma terminal que usarás para iniciar el bot.

## 2. Ejecutar el Bot

Una vez que hayas completado toda la configuración, puedes iniciar el bot con el siguiente comando:

```bash
python donation_bot/main.py
```

Si todo está configurado correctamente, verás un mensaje en la terminal indicando que el bot se ha iniciado.

## 3. Cómo Usar el Bot

1.  **Conviértete en Propietario:** Abre Telegram y busca el bot que creaste. Envía el comando `/start`. La primera persona que inicie el bot se convertirá en el propietario y tendrá acceso a todos los comandos.

2.  **Ver Comandos:** Envía `.cmds` para ver la lista de comandos disponibles.

3.  **Agregar Usuarios (Opcional):** Si quieres que otra persona pueda usar el bot, primero necesita saber su ID de Telegram. Luego, como propietario, puedes usar el comando:
    `.add_user <ID_DEL_USUARIO>`
    *Ejemplo: `.add_user 123456789`*

4.  **Realizar Donación:** Este es el comando principal. Para usarlo, envía un mensaje con el siguiente formato:

    ```
    .donate
    NUMERO_TARJETA_1 MM/AA CVC1
    NUMERO_TARJETA_2 MM/AA CVC2
    NUMERO_TARJETA_3 MM/AA CVC3
    ```

    -   La primera línea es solo el comando `.donate`.
    -   Cada línea siguiente contiene los datos de una tarjeta: número, fecha de expiración (formato MM/AA) y CVC, todo separado por espacios.
    -   El bot procesará las tarjetas en el orden en que las envíes. Se detendrá tan pronto como un pago sea exitoso.

    **Ejemplo de uso:**
    ```
    .donate
    4929000000000000 12/25 123
    5555000000000000 08/26 456
    ```
    *(Estos son números de prueba, no uses tarjetas reales en este ejemplo).*

## Código Editable

Todos los archivos `.py` están comentados para que puedas entender qué hace cada parte. Si necesitas cambiar la lógica, puedes editar los archivos:
-   `donation_bot/main.py`: Contiene la lógica del bot de Telegram (comandos, respuestas).
-   `donation_bot/automation.py`: Contiene la lógica de automatización web con Playwright. **Si la estructura de la página web cambia, necesitarás actualizar los "selectores" en este archivo.**
-   `donation_bot/user_manager.py`: Gestiona los usuarios autorizados.
