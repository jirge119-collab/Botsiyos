# Bot de Donación Automatizada v2.3 (Final)

Esta es la versión final y más robusta del bot de Telegram, que automatiza donaciones de forma segura y flexible.

## Características Principales
- **Datos Personales Fijos:** Usa datos personales definidos en `config.json`.
- **Entrada de Tarjetas por Comando:** Las tarjetas se proporcionan de forma segura en el comando `/donar`.
- **Gestión de Usuarios:** Un administrador puede añadir o eliminar a otros usuarios.
- **Diagnóstico de Errores Mejorado:** Envía capturas de pantalla a Telegram en caso de fallo.
- **Resistente a Tiempos de Carga:** El bot espera explícitamente a que cada elemento de la página aparezca antes de interactuar con él.

## Instrucciones de Configuración

### Paso 1: Descargar el Código y Descomprimirlo

### Paso 2: Instalar Dependencias
Abre una terminal en la carpeta del proyecto y ejecuta:
```bash
pip install -r requirements.txt
playwright install
```

### Paso 3: Configurar el Bot
1.  Crea un bot en Telegram con `@BotFather` para obtener tu `token`.
2.  Copia `config.json.template` y renómbralo a `config.json`.
3.  Abre `config.json` y rellena `telegram_bot_token`, `allowed_user_ids` (poniendo tu ID como el primero para ser admin) y la sección `personal_info`.

### Paso 4: Ejecutar el Bot
En tu terminal, ejecuta: `python bot.py`

## Lista de Comandos (`.cmds`)
Puedes escribir `.cmds` en cualquier momento para ver esta lista de comandos.

### Comandos Públicos
- `/id`: Te responde con tu ID de usuario de Telegram.

### Comandos de Usuario Autorizado
- `/donar`: Inicia el proceso de donación. Formato: `numero_tarjeta|mes|año|cvc`.

### Comandos de Administrador
- `/adduser <ID>`: Autoriza a un nuevo usuario.
- `/removeuser <ID>`: Revoca el acceso a un usuario.
- `/listusers`: Muestra la lista de usuarios autorizados.

## Solución de Problemas

### Error: "el bot no rellena los campos"
Este error ocurre si la estructura de la página web cambia.
1.  **Sigue las instrucciones detalladas** en la sección "Cómo actualizar los selectores" más abajo para obtener los selectores correctos.
2.  **Pégalos** en el diccionario `SELECTORS` al principio del archivo `automation.py`.

### Error: "La operación excedió el tiempo de espera"
Este error ocurre si la página es demasiado lenta o si algo bloquea el proceso. El bot te enviará capturas de pantalla para ayudarte a ver qué pasó.

---
### Cómo actualizar los selectores
1.  **Abre la página de donación** en tu navegador.
2.  **Haz clic derecho** en el campo que falla (ej. "RUT") y selecciona **"Inspeccionar"**.
3.  En el panel de código, haz clic derecho sobre la línea resaltada -> **Copiar > Copiar selector**.
4.  **Abre `automation.py`**, busca el diccionario `SELECTORS` y pega el valor copiado.

**Nota Final:** Si después de actualizar los selectores el bot sigue sin funcionar, es muy probable que la página web tenga medidas de seguridad anti-bot avanzadas diseñadas específicamente para prevenir este tipo de automatización. Superar estas medidas es un desafío mucho más complejo que escapa al alcance de este script.
