#!/usr/bin/env python
"""
Script para crear datos de prueba en Pulse
Ejecutar: python populate_test_data.py
"""

import os
import django
import sys
from datetime import timedelta
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pulse_backend.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from pulse_app.models import User, Post, Like, Comment, Follow, Poll, PollOption

def create_test_users():
    """Crear usuarios de prueba"""
    print("📝 Creando usuarios de prueba...")
    
    users = []
    usernames = ['maria', 'juan', 'sofia', 'carlos', 'ana']
    
    for username in usernames:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'first_name': username.capitalize(),
                'bio': f'Soy {username}, ¡bienvenido a mi perfil!'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"  ✅ Usuario creado: @{username}")
        else:
            print(f"  ℹ️ Usuario existe: @{username}")
        users.append(user)
    
    return users

def create_test_follows(users):
    """Crear relaciones de seguimiento"""
    print("\n👥 Creando relaciones de seguimiento...")
    
    follow_pairs = [
        (users[0], users[1]),
        (users[1], users[0]),
        (users[0], users[2]),
        (users[2], users[0]),
        (users[1], users[3]),
        (users[3], users[1]),
    ]
    
    for follower, followee in follow_pairs:
        follow, created = Follow.objects.get_or_create(
            follower=follower,
            followee=followee,
            defaults={'status': 'accepted'}
        )
        if created:
            print(f"  ✅ @{follower.username} sigue a @{followee.username}")

def create_test_posts(users):
    """Crear posts de prueba"""
    print("\n📝 Creando posts de prueba...")
    
    posts_data = [
        {
            'author': users[0],
            'post_type': 'text',
            'text_content': '¡Hola Pulse! Este es mi primer post. ¿Qué opinan?'
        },
        {
            'author': users[1],
            'post_type': 'text',
            'text_content': 'Acabo de descubrir Pulse, ¡me encanta la idea del contenido efímero!'
        },
        {
            'author': users[2],
            'post_type': 'text',
            'text_content': 'Los posts desaparecen en 5 minutos... mejor que aproveche 😄'
        },
        {
            'author': users[3],
            'post_type': 'text',
            'text_content': 'Pulse es como Snapchat pero para todos. ¡Genial!'
        },
        {
            'author': users[0],
            'post_type': 'text',
            'text_content': 'Cada like suma 1 minuto de vida. ¡Veamos cuánto dura!'
        },
    ]
    
    posts = []
    for data in posts_data:
        post = Post.objects.create(
            author=data['author'],
            post_type=data['post_type'],
            text_content=data.get('text_content', ''),
            initial_life_seconds=300,
            life_seconds_remaining=300,
            expires_at=timezone.now() + timedelta(seconds=300)
        )
        posts.append(post)
        print(f"  ✅ Post creado por @{data['author'].username}")
    
    return posts

def create_test_likes(posts, users):
    """Crear likes de prueba"""
    print("\n❤️ Creando likes de prueba...")
    
    # Post 0 recibe likes de varios usuarios
    for user in users[1:4]:
        like, created = Like.objects.get_or_create(
            post=posts[0],
            user=user
        )
        if created:
            posts[0].likes_count += 1
            posts[0].life_seconds_remaining += 60
            print(f"  ✅ @{user.username} dio like al post de @{posts[0].author.username}")
    
    # Post 1 recibe likes
    for user in users[0:2]:
        like, created = Like.objects.get_or_create(
            post=posts[1],
            user=user
        )
        if created:
            posts[1].likes_count += 1
            posts[1].life_seconds_remaining += 60
            print(f"  ✅ @{user.username} dio like al post de @{posts[1].author.username}")
    
    # Post 2 recibe muchos likes
    for user in users:
        if user != posts[2].author:
            like, created = Like.objects.get_or_create(
                post=posts[2],
                user=user
            )
            if created:
                posts[2].likes_count += 1
                posts[2].life_seconds_remaining += 60
    
    print(f"  ✅ Post más popular: {posts[2].likes_count} likes")
    
    # Guardar cambios
    for post in posts:
        post.save()

def create_test_comments(posts, users):
    """Crear comentarios de prueba"""
    print("\n💬 Creando comentarios de prueba...")
    
    comments_data = [
        (posts[0], users[1], '¡Bienvenido a Pulse! 🎉'),
        (posts[0], users[2], 'Excelente primer post'),
        (posts[1], users[0], 'A mí también me encanta 😊'),
        (posts[2], users[0], 'Totalmente de acuerdo'),
        (posts[3], users[1], 'Pero un poco diferente en funcionalidad'),
    ]
    
    for post, user, text in comments_data:
        comment = Comment.objects.create(
            post=post,
            user=user,
            text=text
        )
        post.comments_count += 1
        post.save()
        print(f"  ✅ @{user.username} comentó en post de @{post.author.username}")

def create_test_poll(users):
    """Crear encuesta de prueba"""
    print("\n📊 Creando encuesta de prueba...")
    
    author = users[4]
    post = Post.objects.create(
        author=author,
        post_type='poll',
        initial_life_seconds=300,
        life_seconds_remaining=300,
        expires_at=timezone.now() + timedelta(seconds=300)
    )
    
    poll = Poll.objects.create(
        post=post,
        question='¿Cuál es tu red social favorita?'
    )
    
    options_data = [
        'Pulse',
        'Instagram',
        'TikTok',
        'Snapchat'
    ]
    
    for option_text in options_data:
        PollOption.objects.create(
            poll=poll,
            text=option_text
        )
    
    print(f"  ✅ Encuesta creada: {poll.question}")

def main():
    """Función principal"""
    print("╔════════════════════════════════════════╗")
    print("║ Creando datos de prueba para Pulse    ║")
    print("╚════════════════════════════════════════╝")
    
    try:
        # Crear datos
        users = create_test_users()
        create_test_follows(users)
        posts = create_test_posts(users)
        create_test_likes(posts, users)
        create_test_comments(posts, users)
        create_test_poll(users)
        
        print("\n" + "═" * 40)
        print("✨ ¡Datos de prueba creados exitosamente!")
        print("═" * 40)
        print("\n📊 Resumen:")
        print(f"  • Usuarios: {User.objects.count()}")
        print(f"  • Posts: {Post.objects.count()}")
        print(f"  • Likes: {Like.objects.count()}")
        print(f"  • Comentarios: {Comment.objects.count()}")
        print(f"  • Seguimientos: {Follow.objects.count()}")
        print(f"  • Encuestas: {Poll.objects.count()}")
        
        print("\n🧪 Credenciales de prueba:")
        print("  Usuario: maria")
        print("  Contraseña: password123")
        print("  (Aplica para todos los usuarios de prueba)")
        
        print("\n🌐 Accede a:")
        print("  http://localhost:8000")
        print("  http://localhost:8000/admin")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
