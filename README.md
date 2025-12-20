# Pulse - Red Social

**Lo que importa, dura** ❤️

Red social efímera con posts que expiran, pero donde el contenido valioso perdura.

## Características

- 📱 PWA - Instalable como app móvil
- ⏱️ Posts efímeros con temporizador
- 💬 Comentarios y likes en tiempo real
- 🎨 Tema claro/oscuro
- 📊 Encuestas interactivas
- 🔔 Notificaciones
- #️⃣ Hashtags y @menciones
- ♾️ Infinite scroll (móvil)
- 🔄 Pull to refresh (móvil)
- 📈 Sistema de trending

## Tech Stack

- Django 5.2.7
- Celery + Redis (tareas en background)
- PWA (Progressive Web App)
- Responsive design (mobile-first)

## Instalación Local

```bash
# Clonar
git clone https://github.com/tu-usuario/pulse.git
cd pulse/pulse_backend

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
python manage.py migrate

# Crear superuser
python manage.py createsuperuser

# Colectar estáticos
python manage.py collectstatic

# Ejecutar servidor
python manage.py runserver
```

## Deployment en Railway

1. Fork este repo
2. Ve a [Railway.app](https://railway.app)
3. New Project → Deploy from GitHub
4. Añade Redis database
5. Deploy!

## License

MIT
