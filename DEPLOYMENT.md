# 🚀 Guía de Deployment - Pulse

## Compartir con tus amigos - 3 opciones

### Opción 1: Railway.app (Recomendado - GRATIS) ⭐

**Paso 1: Preparar el proyecto**
```bash
# Ya está listo! Tienes:
✅ Procfile
✅ runtime.txt
✅ requirements.txt
```

**Paso 2: Crear cuenta en Railway**
1. Ve a https://railway.app
2. Regístrate con GitHub (gratis)
3. Click en "New Project" → "Deploy from GitHub repo"
4. Conecta tu repositorio de Pulse

**Paso 3: Configurar variables de entorno**
En Railway, añade estas variables:
```
DEBUG=False
SECRET_KEY=cambia-esto-por-una-clave-segura-generada
ALLOWED_HOSTS=*.railway.app
```

**Paso 4: Añadir Redis**
- En Railway: Click en "+ New" → "Database" → "Add Redis"
- Se conectará automáticamente

**Paso 5: Desplegar**
- Railway detecta automáticamente Django
- Click en "Deploy"
- ¡Listo! Tu URL será: `https://tu-app.railway.app`

**Costo:** GRATIS ($5/mes de crédito incluido)

---

### Opción 2: Render.com (GRATIS pero más lento)

**Paso 1:** Ve a https://render.com
**Paso 2:** Regístrate y conecta GitHub
**Paso 3:** New → Web Service → Conecta tu repo
**Paso 4:** Configuración:
```
Name: pulse
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: daphne -b 0.0.0.0 -p $PORT pulse_backend.asgi:application
```
**Paso 5:** Añade Redis (New → Redis)
**Paso 6:** Deploy

**Costo:** GRATIS (con sleep después de inactividad)

---

### Opción 3: PythonAnywhere (Más complejo, pero estable)

1. Cuenta en https://www.pythonanywhere.com
2. Sube archivos vía SFTP
3. Configura Bash console
4. Sigue su wizard de Django

---

## 📱 Convertir en App Instalable (PWA)

Ya está configurado! Cuando tus amigos visiten tu sitio:

### En Android:
1. Abrir Chrome/Edge
2. Ir a tu-url.railway.app
3. Menu (⋮) → "Añadir a pantalla de inicio"
4. ¡Ya tienen la app instalada! 📲

### En iPhone:
1. Abrir Safari
2. Ir a tu-url.railway.app
3. Botón "Compartir" → "Añadir a inicio"
4. ¡Ya tienen la app instalada! 📲

### Características PWA activadas:
✅ Icono en pantalla de inicio
✅ Pantalla completa (sin barra del navegador)
✅ Funciona offline (caché)
✅ Notificaciones push (próximamente)
✅ Carga rápida

---

## 🌐 Compartir con Ngrok (Temporal - Para pruebas)

Si solo quieres compartir temporalmente:

```bash
# Instalar ngrok
winget install ngrok

# Ejecutar
ngrok http 8000
```

Te dará una URL tipo: `https://abc123.ngrok.io`
Compártela con tus amigos (válida por 2 horas gratis)

---

## 🔒 Seguridad antes de compartir

**1. Cambia SECRET_KEY en settings.py:**
```python
# Genera una nueva con:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**2. Actualiza ALLOWED_HOSTS:**
```python
ALLOWED_HOSTS = ['tu-dominio.railway.app', 'localhost']
```

**3. Configura HTTPS (Railway lo hace automático)**

**4. Usa variables de entorno para credenciales**

---

## 📊 Monitoreo

Railway te da:
- Logs en tiempo real
- Métricas de uso
- Alertas
- Rollback automático

---

## 💰 Costos estimados

### Railway (Recomendado):
- **Gratis:** $5/mes de crédito
- **Hobby:** $5/mes para más recursos
- **Redis:** Incluido en plan gratis

### Render:
- **Gratis:** Con limitaciones (sleep)
- **Starter:** $7/mes sin sleep

### PythonAnywhere:
- **Gratis:** Limitado
- **Hacker:** $5/mes

---

## 🚀 Comandos rápidos de Railway

```bash
# Instalar CLI
npm install -g @railway/cli

# Login
railway login

# Ver logs
railway logs

# Ejecutar comandos
railway run python manage.py migrate
railway run python manage.py createsuperuser

# Abrir en navegador
railway open
```

---

## ✅ Checklist antes de compartir

- [ ] SECRET_KEY cambiado
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configurado
- [ ] Migraciones aplicadas
- [ ] Superuser creado
- [ ] Archivos estáticos colectados
- [ ] Redis conectado
- [ ] Celery funcionando
- [ ] PWA testeada en móvil
- [ ] HTTPS activo

---

## 🆘 Problemas comunes

**Error: "DisallowedHost"**
→ Añade tu dominio a ALLOWED_HOSTS

**Error: "Static files not found"**
→ Ejecuta `railway run python manage.py collectstatic`

**Error: "Redis connection"**
→ Verifica variable REDIS_URL en Railway

**App muy lenta en Render**
→ Normal en plan gratis, upgrade o usa Railway

---

## 📞 Soporte

Railway: https://railway.app/help
Render: https://render.com/docs
Pulse Issues: [Tu GitHub]

---

**¡Ya puedes compartir Pulse con el mundo! 🌍**
