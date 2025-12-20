import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pulse_backend.settings')

app = Celery('pulse_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configuración de tareas periódicas
app.conf.beat_schedule = {
    'check-expired-posts': {
        'task': 'pulse_app.tasks.check_and_expire_posts',
        'schedule': 60.0,  # Cada 60 segundos
    },
    'update-post-life': {
        'task': 'pulse_app.tasks.update_post_life',
        'schedule': 30.0,  # Cada 30 segundos
    },
    'generate-trending': {
        'task': 'pulse_app.tasks.generate_trending_posts',
        'schedule': 300.0,  # Cada 5 minutos
    },
}
