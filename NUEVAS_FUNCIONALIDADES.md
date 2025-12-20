# Pulse - Red Social

## Nuevas Funcionalidades Implementadas

### 1. Sistema de Expiración Automática de Posts (Celery)
- **Tareas periódicas configuradas:**
  - `check_and_expire_posts`: Verifica y expira posts cada 60 segundos
  - `update_post_life`: Actualiza tiempo restante cada 30 segundos
  - `generate_trending_posts`: Calcula posts trending cada 5 minutos

**Para ejecutar Celery:**
```bash
# Terminal 1: Worker de Celery
celery -A pulse_backend worker -l info

# Terminal 2: Beat de Celery (tareas periódicas)
celery -A pulse_backend beat -l info
```

**Requisito:** Redis debe estar ejecutándose
```bash
# Windows (con Redis instalado)
redis-server

# O usar Docker
docker run -d -p 6379:6379 redis
```

---

### 2. Parsing de Menciones y Hashtags
- **Menciones (@username):** Se convierten en enlaces clicables al perfil
- **Hashtags (#tag):** Se convierten en enlaces a búsqueda
- **Notificaciones:** Los usuarios mencionados reciben notificaciones
- **Estilos:** Menciones en rosa (primary color), hashtags en naranja (secondary color)

**Uso en templates:**
```django
{% load poll_filters %}
{{ post.text_content|linkify }}
```

---

### 3. Pull to Refresh (Móvil)
- **Activación:** Deslizar hacia abajo desde el top del feed
- **Indicador visual:** Icono rotatorio con texto
- **Estados:** "Desliza para actualizar" → "Suelta para actualizar" → "Actualizando..."
- **Solo móvil:** Se activa automáticamente en pantallas ≤768px

---

### 4. Infinite Scroll (Móvil)
- **Carga automática:** Posts se cargan al llegar al final
- **Indicador:** Spinner de carga con texto
- **Paginación oculta:** La paginación tradicional se oculta en móvil
- **Performance:** Usa `requestAnimationFrame` para scroll suave
- **Solo móvil:** Se activa automáticamente en pantallas ≤768px

---

### 5. Sistema de Toast Notifications
- **Tipos:** success, error, warning, info
- **Auto-dismiss:** Se ocultan automáticamente después de 3 segundos
- **Manual close:** Botón X para cerrar
- **Posición:** Top-right en desktop, full-width en móvil

**Uso en JavaScript:**
```javascript
toast.success('Post creado correctamente');
toast.error('Error al eliminar');
toast.warning('Tiempo expirando pronto');
toast.info('Nueva actualización disponible');
```

---

### 6. Diálogo de Confirmación
- **Uso:** Antes de eliminar posts
- **Overlay:** Fondo oscuro con blur
- **Acciones:** Confirmar o Cancelar
- **Responsive:** Se adapta a móvil

**Ejemplo:**
```javascript
showConfirmDialog({
    title: '¿Eliminar publicación?',
    message: 'Esta acción no se puede deshacer.',
    confirmText: 'Eliminar',
    type: 'danger',
    onConfirm: () => {
        // Ejecutar eliminación
    }
});
```

---

## Archivos Creados/Modificados

### JavaScript
- ✅ `static/js/pull-to-refresh.js` - Pull to refresh
- ✅ `static/js/infinite-scroll.js` - Scroll infinito
- ✅ `static/js/toast.js` - Notificaciones y confirmaciones
- ✅ `static/js/main.js` - Actualizado con toast

### CSS
- ✅ `static/css/style.css` - Estilos para toast, confirmaciones, menciones, hashtags

### Python
- ✅ `pulse_app/utils.py` - Ya existía con funciones de parsing
- ✅ `pulse_app/templatetags/poll_filters.py` - Filtro linkify añadido
- ✅ `pulse_app/models.py` - Propiedad percentage añadida a PollOption
- ✅ `pulse_backend/celery.py` - Configuración de tareas periódicas

### Templates
- ✅ `templates/pulse_app/index.html` - Usar filtro linkify
- ✅ `templates/base.html` - Scripts de toast añadidos

---

## Comandos de Deployment

### 1. Colectar archivos estáticos
```bash
python manage.py collectstatic --noinput
```

### 2. Aplicar migraciones
```bash
python manage.py migrate
```

### 3. Ejecutar servidor
```bash
python manage.py runserver
```

### 4. Ejecutar Celery (en producción)
```bash
# Supervisor o systemd para mantener workers activos
celery -A pulse_backend worker --beat -l info
```

---

## Testing

### Probar menciones y hashtags:
1. Crear un post con texto: "Hola @username esto es #trending"
2. Verificar que aparecen como enlaces
3. Click en @username debe ir al perfil
4. Click en #trending debe buscar el hashtag

### Probar Pull to Refresh (móvil):
1. Abrir en móvil o DevTools responsive mode
2. Scroll al top del feed
3. Deslizar hacia abajo
4. Soltar cuando dice "Suelta para actualizar"

### Probar Infinite Scroll (móvil):
1. Abrir feed en móvil
2. Scroll hacia abajo
3. Al llegar al final, debe cargar más posts automáticamente
4. Verificar spinner de carga

### Probar Confirmación de eliminación:
1. Intentar eliminar un post propio
2. Debe aparecer modal de confirmación
3. Cancelar → no elimina
4. Confirmar → elimina y muestra toast

---

## Dependencias

Asegúrate de tener instalado en `requirements.txt`:
```
Django>=5.0
celery>=5.3.0
redis>=4.5.0
Pillow
djangorestframework
django-cors-headers
```

---

## Notas Importantes

1. **Redis** es obligatorio para Celery
2. **Toast notifications** son globales, disponibles en `window.toast`
3. **Pull to refresh** y **infinite scroll** solo funcionan en móvil
4. **Menciones** crean notificaciones automáticamente
5. **Hashtags** incrementan contador de uso

---

## Próximas Mejoras Sugeridas

- [ ] WebSockets para notificaciones en tiempo real
- [ ] Chat en tiempo real con WebSockets
- [ ] Sistema de caché con Redis para trending
- [ ] Compresión de imágenes al subir
- [ ] PWA (Progressive Web App) con Service Worker
- [ ] Rate limiting en APIs
- [ ] Optimización de queries N+1
