# Bot de Donación para TECHO Chile (v3)

Esta versión del bot de Telegram está diseñada **específicamente** para automatizar el proceso de donación en la página de **TECHO Chile**, operada por Getnet: `https://micrositios.getnet.cl/techochile`.

**LA CLAVE DEL ÉXITO:** Este bot **SÓLO FUNCIONARÁ** si tú, el usuario, proporcionas los **selectores CSS correctos** para cada campo del formulario en el archivo `automation.py`. Las suposiciones que he hecho probablemente necesiten ser corregidas.

## Flujo de Automatización
El bot intentará realizar las siguientes acciones:
1.  Hacer clic en "Otro monto".
2.  Ingresar un monto a donar.
3.  Rellenar nombre, apellido y email.
4.  Hacer clic en "Siguiente".
5.  Rellenar los datos de la tarjeta de crédito.
6.  Hacer clic en "Pagar".

## Instrucciones

### 1. Configurar el Bot
- Copia `config.json.template` a `config.json`.
- Rellena tu `telegram_bot_token` y `allowed_user_ids`.
- La sección `personal_info` en `config.json` se usará para rellenar los datos del donante.

### 2. **ACTUALIZAR LOS SELECTORES (PASO OBLIGATORIO)**
- **Abre `automation.py`**. Verás un diccionario llamado `SELECTORS` al principio. Contiene todas las "direcciones" de los campos que el bot necesita.
- **Abre la página de TECHO Chile** en tu navegador.
- Para **CADA CAMPO** y botón del flujo de donación, haz lo siguiente:
    1. Clic derecho en el elemento -> **Inspeccionar**.
    2. En el código que aparece, clic derecho en la línea resaltada -> **Copiar > Copiar selector**.
    3. **Pega** el selector que copiaste en el valor correspondiente dentro del diccionario `SELECTORS`.
- **Guarda el archivo `automation.py`**.

### 3. Instalar Dependencias y Ejecutar
- Abre una terminal en la carpeta del bot.
- Ejecuta `pip install -r requirements.txt`.
- Ejecuta `playwright install`.
- Ejecuta `python bot.py`.

## Comandos
- Escribe `.cmds` para ver la lista de comandos.
- `/donar <numero_tarjeta|mes|año|cvc>`: Inicia el proceso de donación con la tarjeta indicada.
- `/ping`, `/id`, `/adduser`, etc. siguen disponibles.
