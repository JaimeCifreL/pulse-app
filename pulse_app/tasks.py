from celery import shared_task
from django.utils import timezone
from .models import Post, Notification
from datetime import timedelta


@shared_task
def check_and_expire_posts():
    """
    Tarea para verificar y expirar posts cuyo tiempo de vida ha terminado.
    Se ejecuta cada minuto.
    """
    now = timezone.now()
    expired_posts = Post.objects.filter(
        expires_at__lte=now,
        is_expired=False
    )
    
    for post in expired_posts:
        post.is_expired = True
        post.life_seconds_remaining = 0
        post.save()
        
        # Crear notificación al autor
        Notification.objects.create(
            user=post.author,
            notification_type='expire',
            post=post,
            payload={
                'message': f'Tu publicación ha expirado',
                'total_life_seconds': post.total_life_seconds_reached,
                'final_likes': post.likes_count
            }
        )
    
    return f'{len(expired_posts)} posts expirados'


@shared_task
def update_post_life():
    """
    Tarea para actualizar el tiempo de vida restante de los posts.
    Se ejecuta cada 30 segundos.
    """
    now = timezone.now()
    active_posts = Post.objects.filter(
        is_expired=False,
        expires_at__gt=now
    )
    
    updated_count = 0
    for post in active_posts:
        time_remaining = (post.expires_at - now).total_seconds()
        if time_remaining > 0:
            post.life_seconds_remaining = int(time_remaining)
            post.save()
            updated_count += 1
    
    return f'{updated_count} posts actualizado'


@shared_task
def generate_trending_posts():
    """
    Tarea para calcular posts tendencia.
    Se ejecuta cada 5 minutos.
    """
    # Buscar posts con muchos likes en poco tiempo
    five_minutes_ago = timezone.now() - timedelta(minutes=5)
    trending = Post.objects.filter(
        created_at__gte=five_minutes_ago,
        is_expired=False
    ).order_by('-likes_count')[:20]
    
    return f'{len(trending)} posts tendencia calculados'
