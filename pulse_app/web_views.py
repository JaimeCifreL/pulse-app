from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Post, User, Like, Comment, Follow, Chat, Message, Repost, Poll, PollOption, PollVote, PostInteraction, Mention, Hashtag, Notification
from django.core.paginator import Paginator
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q, Count, Exists, OuterRef
from .utils import process_mentions, process_hashtags, create_notification


def index(request):
    """Home / Feed view with 'For You' and 'Following' tabs"""
    now = timezone.now()
    feed_type = request.GET.get('feed', 'for_you')  # 'for_you' or 'following'

    if request.user.is_authenticated:
        # Obtener usuarios que sigue (solo con status accepted)
        following_ids = Follow.objects.filter(
            follower=request.user, 
            status='accepted'
        ).values_list('followee_id', flat=True)
        
        if feed_type == 'following':
            # Feed "Siguiendo": solo posts de usuarios que sigue + propios
            posts = Post.objects.filter(
                Q(author_id__in=following_ids) | Q(author=request.user),
                expires_at__gt=now
            ).distinct().order_by('-created_at')
            
        else:  # for_you
            # Feed "Para Ti": usuarios que sigue + propios + recomendaciones del algoritmo
            
            # 1. Posts de usuarios que sigue
            posts_from_following = Post.objects.filter(
                author_id__in=following_ids,
                expires_at__gt=now
            )
            
            # 2. Posts propios del usuario
            own_posts = Post.objects.filter(
                author=request.user,
                expires_at__gt=now
            )
            
            # 3. Posts recomendados (solo de cuentas públicas o que ya sigue)
            # Excluir posts con los que ya ha reaccionado
            reacted_post_ids = PostInteraction.objects.filter(
                user=request.user,
                has_reacted=True
            ).values_list('post_id', flat=True)
            
            # Recomendaciones: cuentas públicas populares con las que no ha interactuado
            recommended_posts = Post.objects.filter(
                Q(author__is_private=False) | Q(author_id__in=following_ids),
                expires_at__gt=now
            ).exclude(
                id__in=reacted_post_ids
            ).exclude(
                author=request.user
            ).annotate(
                engagement_score=Count('likes') + Count('comments') + Count('reposts')
            ).order_by('-engagement_score', '-created_at')[:20]  # Top 20 posts populares
            
            # Combinar posts de seguidos, propios y recomendados
            posts = Post.objects.filter(
                Q(id__in=posts_from_following) | Q(id__in=own_posts) | Q(id__in=recommended_posts),
                expires_at__gt=now
            ).distinct().order_by('-created_at')
            
    else:
        # Posts públicos de usuarios públicos (no expirados)
        posts = Post.objects.filter(
            expires_at__gt=now, 
            author__is_private=False
        ).order_by('-created_at')

    # Calcular tiempo restante y agregar información de likes/reposts
    for p in posts:
        if not p.expires_at:
            p.time_remaining_seconds = 0
        else:
            p.time_remaining_seconds = max(0, int((p.expires_at - now).total_seconds()))
        
        # Agregar información de si el usuario actual dio like o reposteó
        if request.user.is_authenticated:
            p.is_liked = Like.objects.filter(post=p, user=request.user).exists()
            p.is_reposted = Repost.objects.filter(original_post=p, user=request.user).exists()
        else:
            p.is_liked = False
            p.is_reposted = False
        
        # Si es una encuesta, el porcentaje se calcula automáticamente desde la propiedad
        # del modelo PollOption, no necesita asignación manual
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Pasar timestamp actual en milisegundos para el JS
    import time
    now_timestamp = int(time.time() * 1000)
    
    context = {
        'page_obj': page_obj,
        'posts': page_obj.object_list,
        'now_timestamp': now_timestamp,
        'feed_type': feed_type,
    }
    return render(request, 'pulse_app/index.html', context)


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            return render(request, 'pulse_app/register.html', 
                        {'error': 'Las contraseñas no coinciden'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'pulse_app/register.html',
                        {'error': 'El usuario ya existe'})
        
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('index')
    
    return render(request, 'pulse_app/register.html')


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'pulse_app/login.html',
                        {'error': 'Credenciales inválidas'})
    
    return render(request, 'pulse_app/login.html')


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    return redirect('index')


@login_required
def create_post_view(request):
    """Create post view"""
    if request.method == 'POST':
        post_type = request.POST.get('post_type')
        text_content = request.POST.get('text_content')
        file = request.FILES.get('content_file')
        
        post = Post.objects.create(
            author=request.user,
            post_type=post_type,
            text_content=text_content,
            content_url=file if file else None,
            initial_life_seconds=300,  # 5 minutos
            life_seconds_remaining=300
        )
        
        # Procesar menciones en el texto
        if text_content:
            process_mentions(text_content, post=post, mentioned_by=request.user)
            process_hashtags(text_content, post=post)
        
        # Si es una encuesta, crear el poll y las opciones
        if post_type == 'poll':
            from .models import Poll, PollOption
            poll_question = request.POST.get('poll_question')
            poll = Poll.objects.create(post=post, question=poll_question)
            
            # Obtener todas las opciones de la encuesta
            option_texts = request.POST.getlist('poll_options[]')
            for option_text in option_texts:
                if option_text.strip():  # Solo crear si no está vacío
                    PollOption.objects.create(poll=poll, text=option_text)
        
        return redirect('post_detail', post_id=post.id)
    
    return render(request, 'pulse_app/create_post.html')


def post_detail_view(request, post_id):
    """Post detail view"""
    post = get_object_or_404(Post, id=post_id)
    
    # Si el post está expirado, solo el autor puede verlo
    now = timezone.now()
    is_expired_now = post.expires_at and post.expires_at <= now

    if is_expired_now and request.user != post.author:
        return redirect('index')
    
    # Verificar privacidad
    if post.author.is_private and request.user != post.author:
        if not Follow.objects.filter(follower=request.user, followee=post.author, 
                                    status='accepted').exists():
            return redirect('index')
    
    comments = post.comments.all().order_by('-created_at')
    likes = post.likes.all()
    
    # Pasar timestamp actual en milisegundos para el JS
    import time
    now_timestamp = int(time.time() * 1000)
    
    # Calcular time_remaining_seconds en la vista para los templates
    from datetime import timedelta
    if post.is_expired:
        post.time_remaining_seconds = 0
    else:
        if post.is_expired or not post.expires_at:
            post.time_remaining_seconds = 0
        else:
            remaining = (post.expires_at - timezone.now()).total_seconds()
            post.time_remaining_seconds = max(0, int(remaining))

    
    context = {
        'post': post,
        'comments': comments,
        'likes': likes,
        'is_liked': likes.filter(user=request.user).exists() if request.user.is_authenticated else False,
        'now_timestamp': now_timestamp
    }
    return render(request, 'pulse_app/post_detail.html', context)


@login_required
@require_POST
def like_post(request, post_id):
    """Like/unlike a post"""
    post = get_object_or_404(Post, id=post_id)
    
    # No permitir likes en posts expirados
    now = timezone.now()
    if post.expires_at and post.expires_at <= now:
        return JsonResponse({'error': 'Post expirado'}, status=400)
    
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    
    if created:
        now = timezone.now()

        post.likes_count += 1
        post.total_life_seconds_reached += 60

        base = post.expires_at if post.expires_at and post.expires_at > now else now
        post.expires_at = base + timedelta(seconds=60)

        post.life_seconds_remaining = int((post.expires_at - now).total_seconds())
        post.save()

        # Marcar interacción para el algoritmo
        PostInteraction.objects.update_or_create(
            user=request.user,
            post=post,
            defaults={'has_reacted': True}
        )

        liked = True
    else:
        like.delete()
        post.likes_count = max(0, post.likes_count - 1)
        post.save()
        liked = False
    
    return JsonResponse({'liked': liked, 'likes_count': post.likes_count})


@login_required
def comment_post(request, post_id):
    """Add comment to post"""
    post = get_object_or_404(Post, id=post_id)
    
    # No permitir comentarios en posts expirados
    now = timezone.now()
    if post.expires_at and post.expires_at <= now:
        return redirect('index')

    if request.method == 'POST':
        text = request.POST.get('text')
        comment = Comment.objects.create(post=post, user=request.user, text=text)
        post.comments_count += 1
        post.save()
        
        # Procesar menciones en el comentario
        if text:
            process_mentions(text, comment=comment, mentioned_by=request.user)
        
        # Notificar al autor del post (si no es el mismo usuario)
        if post.author != request.user:
            create_notification(
                user=post.author,
                notification_type='comment',
                actor=request.user,
                post=post,
                comment=comment,
                payload={'comment_text': text[:100]}
            )
        
        # Marcar interacción para el algoritmo
        PostInteraction.objects.update_or_create(
            user=request.user,
            post=post,
            defaults={'has_reacted': True}
        )
    
    return redirect('post_detail', post_id=post_id)


@login_required
@require_POST
def repost_post(request, post_id):
    """Repost/unrepost a post"""
    post = get_object_or_404(Post, id=post_id)
    
    # No permitir repost de posts expirados
    now = timezone.now()
    if post.expires_at and post.expires_at <= now:
        return JsonResponse({'error': 'Post expirado'}, status=400)
    
    repost, created = Repost.objects.get_or_create(original_post=post, user=request.user)
    
    if created:
        post.reposts_count += 1
        post.save()
        
        # Marcar interacción para el algoritmo
        PostInteraction.objects.update_or_create(
            user=request.user,
            post=post,
            defaults={'has_reacted': True}
        )
        
        reposted = True
    else:
        repost.delete()
        post.reposts_count = max(0, post.reposts_count - 1)
        post.save()
        reposted = False
    
    return JsonResponse({'reposted': reposted, 'reposts_count': post.reposts_count})


@login_required
@require_POST
def vote_poll(request, post_id, option_id):
    """Vote on a poll option"""
    post = get_object_or_404(Post, id=post_id, post_type='poll')
    
    # No permitir votar en posts expirados
    now = timezone.now()
    if post.expires_at and post.expires_at <= now:
        return JsonResponse({'error': 'Post expirado'}, status=400)
    
    poll = post.poll
    option = get_object_or_404(PollOption, id=option_id, poll=poll)
    
    # Verificar si el usuario ya votó
    existing_vote = PollVote.objects.filter(poll=poll, user=request.user).first()
    
    if existing_vote:
        # Si votó por la misma opción, no hacer nada
        if existing_vote.option == option:
            return JsonResponse({'error': 'Ya votaste por esta opción'}, status=400)
        
        # Si votó por otra opción, cambiar el voto
        existing_vote.option.votes = max(0, existing_vote.option.votes - 1)
        existing_vote.option.save()
        
        existing_vote.option = option
        existing_vote.save()
    else:
        # Crear nuevo voto
        PollVote.objects.create(poll=poll, user=request.user, option=option)
    
    # Incrementar votos de la opción seleccionada
    option.votes += 1
    option.save()
    
    # Obtener todas las opciones actualizadas
    options_data = []
    total_votes = 0
    for opt in poll.options.all():
        options_data.append({
            'id': str(opt.id),
            'text': opt.text,
            'votes': opt.votes
        })
        total_votes += opt.votes
    
    return JsonResponse({
        'success': True,
        'options': options_data,
        'total_votes': total_votes
    })


def profile_view(request, username):
    """User profile view"""
    now = timezone.now()

    user = get_object_or_404(User, username=username)
    
    # Get user's posts
    if user.is_private and request.user != user:
        if not Follow.objects.filter(follower=request.user, followee=user, status='accepted').exists():
            posts = Post.objects.none()
        else:
            # Para seguidores, mostrar posts no expirados
            posts = user.posts.filter(expires_at__gt=now).order_by('-created_at')
    else:
        # Para perfil público o el autor mismo
        if request.user == user:
            # El autor ve todos sus posts (incluidos expirados)
            posts = user.posts.all().order_by('-created_at')
        else:
            # Otros usuarios ven solo posts no expirados
            posts = user.posts.filter(expires_at__gt=now).order_by('-created_at')
    
    # Obtener post fijado si existe
    pinned_post = user.posts.filter(is_pinned=True, expires_at__gt=now).first()
    
    followers = user.followers.filter(status='accepted')
    following = user.following.filter(status='accepted')
    
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user,
            followee=user,
            status='accepted'
        ).exists()
    
    context = {
        'profile_user': user,
        'posts': posts,
        'pinned_post': pinned_post,
        'followers_count': followers.count(),
        'following_count': following.count(),
        'is_following': is_following
    }
    return render(request, 'pulse_app/profile.html', context)


@login_required
def edit_profile_view(request):
    """Edit user profile"""
    user = request.user
    
    if request.method == 'POST':
        # Verificar si se quiere eliminar la foto de perfil
        if request.POST.get('remove_photo') == 'true':
            if user.profile_photo:
                user.profile_photo.delete()
                user.profile_photo = None
                user.save()
            return redirect('edit_profile')
        
        # Actualizar datos del perfil
        username = request.POST.get('username')
        email = request.POST.get('email')
        display_name = request.POST.get('display_name', '')
        bio = request.POST.get('bio', '')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender', '')
        pronouns = request.POST.get('pronouns', '')
        is_private = request.POST.get('is_private') == 'on'
        
        # Verificar si el username ya existe (si se cambió)
        if username != user.username:
            if User.objects.filter(username=username).exists():
                context = {
                    'error': 'El nombre de usuario ya está en uso',
                    'user': user
                }
                return render(request, 'pulse_app/edit_profile.html', context)
        
        # Actualizar información básica
        user.username = username
        user.email = email
        user.display_name = display_name
        user.bio = bio
        user.is_private = is_private
        user.gender = gender
        user.pronouns = pronouns
        
        # Actualizar fecha de nacimiento
        if date_of_birth:
            user.date_of_birth = date_of_birth
        else:
            user.date_of_birth = None
        
        # Actualizar foto de perfil si se proporciona
        if 'profile_photo' in request.FILES:
            user.profile_photo = request.FILES['profile_photo']
        
        # Cambiar contraseña si se proporciona
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password:
            if new_password == confirm_password:
                if len(new_password) < 8:
                    context = {
                        'error': 'La contraseña debe tener al menos 8 caracteres',
                        'user': user
                    }
                    return render(request, 'pulse_app/edit_profile.html', context)
                user.set_password(new_password)
            else:
                context = {
                    'error': 'Las contraseñas no coinciden',
                    'user': user
                }
                return render(request, 'pulse_app/edit_profile.html', context)
        
        user.save()
        
        # Si cambió la contraseña, re-autenticar
        if new_password:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
        
        return redirect('profile', username=user.username)
    
    context = {'user': user}
    return render(request, 'pulse_app/edit_profile.html', context)


@login_required
def follow_user(request, user_id):
    """Follow a user"""
    user = get_object_or_404(User, id=user_id)
    
    if user == request.user:
        return redirect('profile', username=user.username)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        followee=user,
        defaults={'status': 'accepted' if not user.is_private else 'pending'}
    )
    
    return redirect('profile', username=user.username)


@login_required
def unfollow_user(request, user_id):
    """Unfollow a user"""
    user = get_object_or_404(User, id=user_id)
    follow = get_object_or_404(Follow, follower=request.user, followee=user)
    follow.delete()
    
    return redirect('profile', username=user.username)


@login_required
def messages_view(request):
    """Direct messages view"""
    search_query = request.GET.get('q', '')
    
    # Obtener chats existentes ordenados por última actividad
    chats = Chat.objects.filter(participants=request.user).order_by('-updated_at')
    
    # Agregar información del último mensaje y el otro participante a cada chat
    for chat in chats:
        # Obtener el otro participante
        chat.other_user = chat.participants.exclude(id=request.user.id).first()
        # Obtener el último mensaje
        chat.last_message = chat.messages.first()
    
    # Búsqueda de usuarios
    search_results = []
    if search_query:
        # Buscar usuarios por username o display_name
        search_results = User.objects.filter(
            Q(username__icontains=search_query) | 
            Q(display_name__icontains=search_query)
        ).exclude(id=request.user.id)[:10]
    
    # Usuarios recomendados (usuarios que sigues y no tienes chat activo)
    following_users = User.objects.filter(
        followers__follower=request.user,
        followers__status='accepted'
    ).exclude(id=request.user.id)[:5]
    
    context = {
        'chats': chats,
        'search_query': search_query,
        'search_results': search_results,
        'following_users': following_users,
    }
    return render(request, 'pulse_app/messages.html', context)


@login_required
def chat_view(request, chat_id):
    """Individual chat view"""
    chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        Message.objects.create(chat=chat, sender=request.user, content=content)
        chat.updated_at = timezone.now()
        chat.save()
    
    chat_messages = chat.messages.all().order_by('-created_at')
    
    # Obtener el otro participante
    other_user = chat.participants.exclude(id=request.user.id).first()
    
    context = {
        'chat': chat,
        'chat_messages': chat_messages,
        'other_user': other_user,
    }
    return render(request, 'pulse_app/chat.html', context)


@login_required
def start_chat(request, user_id):
    """Start or get existing chat with a user"""
    other_user = get_object_or_404(User, id=user_id)
    
    # Verificar que no sea el mismo usuario
    if other_user == request.user:
        return redirect('messages')
    
    # Buscar si ya existe un chat entre estos dos usuarios
    existing_chat = Chat.objects.filter(participants=request.user).filter(participants=other_user).first()
    
    if existing_chat:
        return redirect('chat', chat_id=existing_chat.id)
    
    # Crear nuevo chat
    new_chat = Chat.objects.create()
    new_chat.participants.add(request.user, other_user)
    
    return redirect('chat', chat_id=new_chat.id)


def search_view(request):
    """Search view"""
    query = request.GET.get('q', '')
    
    users = User.objects.filter(username__icontains=query)
    now = timezone.now()
    posts = Post.objects.filter(text_content__icontains=query, expires_at__gt=now)
    
    context = {
        'query': query,
        'users': users,
        'posts': posts
    }
    return render(request, 'pulse_app/search.html', context)


@login_required
def trending_view(request):
    """Trending posts view"""
    now = timezone.now()

    posts = Post.objects.filter(expires_at__gt=now).order_by('-likes_count')[:50]

    for post in posts:
        if not post.expires_at:
            post.time_remaining_seconds = 0
        else:
            post.time_remaining_seconds = max(
                0, int((post.expires_at - now).total_seconds())
            )

    # Timestamp actual en milisegundos para JS
    import time
    now_timestamp = int(time.time() * 1000)

    context = {
        'posts': posts,
        'now_timestamp': now_timestamp
    }
    return render(request, 'pulse_app/trending.html', context)


@login_required
def delete_post(request, post_id):
    """Delete a post"""
    post = get_object_or_404(Post, id=post_id)
    
    # Verificar que el usuario es el autor
    if post.author != request.user:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    post.delete()
    return JsonResponse({'success': True})


@login_required
def toggle_pin_post(request, post_id):
    """Pin or unpin a post"""
    post = get_object_or_404(Post, id=post_id)
    
    # Verificar que el usuario es el autor
    if post.author != request.user:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    # Si se está fijando, desfija cualquier otro post fijado
    if not post.is_pinned:
        Post.objects.filter(author=request.user, is_pinned=True).update(is_pinned=False)
    
    post.is_pinned = not post.is_pinned
    post.save()
    
    return JsonResponse({'success': True, 'is_pinned': post.is_pinned})


@login_required
def toggle_comments(request, post_id):
    """Enable or disable comments on a post"""
    post = get_object_or_404(Post, id=post_id)
    
    # Verificar que el usuario es el autor
    if post.author != request.user:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    post.comments_disabled = not post.comments_disabled
    post.save()
    
    return JsonResponse({'success': True, 'comments_disabled': post.comments_disabled})


@login_required
def post_stats_view(request, post_id):
    """View post statistics"""
    post = get_object_or_404(Post, id=post_id)
    
    # Verificar que el usuario es el autor
    if post.author != request.user:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    # Obtener usuarios que dieron like
    likes = Like.objects.filter(post=post).select_related('user').order_by('-created_at')
    
    # Obtener usuarios que repostearon
    reposts = Repost.objects.filter(original_post=post).select_related('user').order_by('-created_at')
    
    # Calcular tiempo de vida
    now = timezone.now()
    time_alive = now - post.created_at
    time_alive_str = str(time_alive).split('.')[0]  # Formato HH:MM:SS
    
    # Si aún no ha expirado, calcular tiempo restante
    if not post.is_expired and post.expires_at:
        time_remaining = post.expires_at - now
        time_remaining_seconds = max(0, int(time_remaining.total_seconds()))
    else:
        time_remaining_seconds = 0
    
    context = {
        'post': post,
        'likes': likes,
        'reposts': reposts,
        'time_alive': time_alive_str,
        'time_remaining_seconds': time_remaining_seconds,
    }
    
    return render(request, 'pulse_app/post_stats.html', context)


@login_required
def notifications_view(request):
    """Notifications center view"""
    filter_type = request.GET.get('filter', 'all')
    
    # Base queryset
    notifications = Notification.objects.filter(user=request.user).select_related(
        'actor', 'post', 'comment'
    )
    
    # Apply filters
    if filter_type == 'mentions':
        notifications = notifications.filter(notification_type='mention')
    elif filter_type == 'likes':
        notifications = notifications.filter(notification_type='like')
    elif filter_type == 'follows':
        notifications = notifications.filter(notification_type__in=['follow', 'follow_request'])
    elif filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    
    # Paginate
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Count unread
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    context = {
        'page_obj': page_obj,
        'notifications': page_obj.object_list,
        'filter_type': filter_type,
        'unread_count': unread_count,
    }
    
    return render(request, 'pulse_app/notifications.html', context)


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})


@login_required
@require_POST
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})


@login_required
def mentions_timeline(request):
    """Timeline of user mentions"""
    mentions = Mention.objects.filter(
        mentioned_user=request.user
    ).select_related('post', 'comment', 'mentioned_by').order_by('-created_at')
    
    paginator = Paginator(mentions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'mentions': page_obj.object_list,
    }
    
    return render(request, 'pulse_app/mentions.html', context)


@login_required
def hashtag_view(request, hashtag_name):
    """View posts with a specific hashtag"""
    now = timezone.now()
    hashtag = get_object_or_404(Hashtag, name=hashtag_name.lower())
    
    posts = Post.objects.filter(
        hashtags__hashtag=hashtag,
        expires_at__gt=now
    ).distinct().order_by('-created_at')
    
    # Calculate time remaining for each post
    for p in posts:
        if not p.expires_at:
            p.time_remaining_seconds = 0
        else:
            p.time_remaining_seconds = max(0, int((p.expires_at - now).total_seconds()))
        
        if request.user.is_authenticated:
            p.is_liked = Like.objects.filter(post=p, user=request.user).exists()
            p.is_reposted = Repost.objects.filter(original_post=p, user=request.user).exists()
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    import time
    now_timestamp = int(time.time() * 1000)
    
    context = {
        'hashtag': hashtag,
        'page_obj': page_obj,
        'posts': page_obj.object_list,
        'now_timestamp': now_timestamp,
    }
    
    return render(request, 'pulse_app/hashtag.html', context)


@login_required
def notification_settings_view(request):
    """View and edit notification settings"""
    from .models import NotificationSettings
    
    settings, created = NotificationSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        settings.notify_likes = request.POST.get('notify_likes') == 'on'
        settings.notify_comments = request.POST.get('notify_comments') == 'on'
        settings.notify_mentions = request.POST.get('notify_mentions') == 'on'
        settings.notify_follows = request.POST.get('notify_follows') == 'on'
        settings.notify_messages = request.POST.get('notify_messages') == 'on'
        settings.notify_reposts = request.POST.get('notify_reposts') == 'on'
        settings.notify_post_expiring = request.POST.get('notify_post_expiring') == 'on'
        settings.notify_friend_reminder = request.POST.get('notify_friend_reminder') == 'on'
        
        expiring_threshold = request.POST.get('expiring_threshold')
        if expiring_threshold:
            settings.expiring_threshold = int(expiring_threshold)
        
        settings.save()
        
        return redirect('notification_settings')
    
    context = {
        'settings': settings,
    }
    
    return render(request, 'pulse_app/notification_settings.html', context)

