# Pulse - Red Social Efímera PWA

## Guía de Despliegue Gratuito en Render.com

### Paso 1: Preparar tu código

1. Crea un repositorio en GitHub
2. Sube todo el código de `pulse_backend`

### Paso 2: Registrarte en Render

1. Ve a https://render.com
2. Regístrate con tu cuenta de GitHub (gratis)

### Paso 3: Crear el servicio web

1. Click en "New +" → "Web Service"
2. Conecta tu repositorio de GitHub
3. Configura:
   - **Name**: `pulse-app` (o el nombre que quieras)
   - **Region**: Oregon (Free)
   - **Branch**: main
   - **Root Directory**: (déjalo vacío si el código está en la raíz)
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `daphne -b 0.0.0.0 -p $PORT pulse_backend.asgi:application`
   - **Instance Type**: Free

4. Variables de entorno (en "Environment"):
   ```
   PYTHON_VERSION=3.11.0
   SECRET_KEY=tu-clave-secreta-generada-aleatoriamente
   DEBUG=False
   ALLOWED_HOSTS=.render.com
   ```

5. Click en "Create Web Service"

### Paso 4: Esperar el despliegue

- El primer deploy tarda 5-10 minutos
- Una vez listo, tendrás una URL como: `https://pulse-app.onrender.com`

### Paso 5: Compartir con amigos

**Como PWA (Instalable):**
1. Comparte el link: `https://tu-app.onrender.com`
2. Tus amigos abren el link en el navegador móvil
3. En Chrome/Safari aparece "Agregar a pantalla de inicio"
4. ¡Se instala como app nativa!

**Importante:** 
- El plan gratuito de Render duerme después de 15 minutos sin uso
- La primera carga puede tardar 30-50 segundos (se "despierta")
- Después funciona normal

## Alternativas Gratuitas

### Railway.app
- 500 horas gratis al mes
- Más rápido que Render
- Setup: https://railway.app

### Fly.io  
- 3 VMs gratis
- Muy rápido
- Setup: https://fly.io

## Para crear APK nativo (opcional)

1. Usa PWA Builder: https://www.pwabuilder.com
2. Ingresa tu URL de Render
3. Descarga el APK generado
4. Comparte el APK por WhatsApp/Telegram

---

## Testing Local

Para probar la PWA localmente:
1. Abre Chrome en tu móvil
2. Conecta tu PC y móvil a la misma red WiFi
3. En tu PC obtén la IP: `ipconfig` (Windows) o `ifconfig` (Mac/Linux)
4. En el móvil abre: `http://TU-IP:8000`
5. Aparecerá el banner de instalación

**¡Tu app está lista para pre-alpha testing!** 🚀
