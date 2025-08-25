# Bot de Pago Recurrente Automatizado

Esta versión del bot de Telegram está diseñada para automatizar un **pago recurrente** o con tarjeta guardada en una página específica.

**IMPORTANTE:** Este bot ya **NO** funciona con el formulario de donación público. Su única función es navegar a la URL de pago recurrente y hacer clic en el botón de confirmación.

## Características Principales
- **Automatización de Pago Recurrente:** Navega a la URL de pago y hace clic en el botón de confirmación.
- **Gestión de Usuarios:** Un administrador puede añadir o eliminar a otros usuarios autorizados.
- **Diagnóstico de Errores:** En caso de fallo, el bot envía una captura de pantalla del error directamente a Telegram.

## Instrucciones de Configuración

### Paso 1: Descargar el Código

### Paso 2: Instalar Dependencias
```bash
pip install -r requirements.txt
playwright install
```

### Paso 3: Configurar el Bot
1.  Copia `config.json.template` y renómbralo a `config.json`.
2.  Abre `config.json` y rellena `telegram_bot_token` y `allowed_user_ids` (poniendo tu ID como el primero para ser admin).
3.  **Abre `automation.py` y actualiza la variable `DONATION_URL`** con la URL de pago recurrente que desees automatizar. La URL en el código es un ejemplo y probablemente sea específica de una sesión.

### Paso 4: Ejecutar el Bot
`python bot.py`

## Lista de Comandos (`.cmds`)
Escribe `.cmds` para ver esta lista.

- `/id`: Te responde con tu ID de usuario.
- `/ping`: Responde "pong" para verificar que el bot está activo.
- `/donar`: **Inicia el proceso de pago recurrente.** Ya no necesitas pasar datos de tarjeta.
- `/adduser <ID>`: (Admin) Autoriza a un nuevo usuario.
- `/removeuser <ID>`: (Admin) Revoca el acceso a un usuario.
- `/listusers`: (Admin) Muestra la lista de usuarios autorizados.

## Solución de Problemas
Si el bot falla, lo más probable es que el selector del botón de confirmación haya cambiado.
- **Abre `automation.py`** y busca el diccionario `SELECTORS`.
- **Actualiza el valor de `confirm_payment_button`** con el selector CSS correcto del botón en la nueva página. Puedes obtenerlo haciendo clic derecho sobre el botón -> Inspeccionar -> Copiar -> Copiar selector.
