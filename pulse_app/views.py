from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import (
    User, Post, Like, Follow, Chat, Notification, Repost
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    PostSerializer, PostCreateSerializer, CommentSerializer, FollowSerializer, MessageSerializer, ChatSerializer,
    NotificationSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User management"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        request.user.auth_token.delete()
        return Response({'detail': 'Sesión cerrada'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        user = self.get_object()
        followers = user.followers.all()
        serializer = UserSerializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def following(self, request, pk=None):
        user = self.get_object()
        following = user.following.all()
        serializer = UserSerializer(following, many=True)
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet for Post management"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Filtra posts expirados.
        - Los posts expirados solo son visibles para su autor
        - Los demás ven solo posts activos (no expirados)
        """
        now = timezone.now()
        queryset = Post.objects.all()
        user = self.request.user
        
        if user.is_authenticated:
            # Si está autenticado, ve posts no expirados + sus propios posts (incluso expirados)
            from django.db.models import Q
            queryset = queryset.filter(Q(expires_at__gt=now) | Q(author=user))
        else:
            # Si no está autenticado, solo ve posts no expirados
            queryset = queryset.filter(expires_at__gt=now)
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        Obtener un post específico.
        Si está expirado, solo el autor puede verlo.
        """
        instance = self.get_object()
        now = timezone.now()
        # Si el post está expirado y el usuario no es el autor, denegar acceso
        if post.expires_at and post.expires_at <= now and request.user != post.author:
            from rest_framework.exceptions import NotFound
            raise NotFound("Post no encontrado")
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def likes(self, request):
        """Obtener likes de múltiples posts para actualizar en tiempo real"""
        post_ids = request.data.get('post_ids', [])
        likes_data = {}
        
        for post_id in post_ids:
            try:
                post = Post.objects.get(id=post_id)
                likes_data[post_id] = post.likes_count
            except Post.DoesNotExist:
                likes_data[post_id] = 0
        
        return Response(likes_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def likes(self, request, pk=None):
        """Obtener el número de likes actual de un post"""
        post = self.get_object()
        
        # Si el post está expirado y el usuario no es el autor, denegar acceso
        if post.is_expired and request.user != post.author:
            from rest_framework.exceptions import NotFound
            raise NotFound("Post no encontrado")
        
        return Response({
            'post_id': post.id,
            'likes_count': post.likes_count
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        
        # Si el post está expirado y el usuario no es el autor, no puede dar like
        if post.is_expired and request.user != post.author:
            from rest_framework.exceptions import NotFound
            raise NotFound("Post no encontrado")
        
        like, created = Like.objects.get_or_create(post=post, user=request.user)
        
        if created:
            now = timezone.now()

            post.likes_count += 1
            post.total_life_seconds_reached += 60

            # Si ya tiene expires_at y aún no expiró, extiende desde ahí.
            # Si está a punto de expirar o ya pasó, empieza desde "now".
            base = post.expires_at if post.expires_at and post.expires_at > now else now
            post.expires_at = base + timedelta(seconds=60)

            post.life_seconds_remaining = int((post.expires_at - now).total_seconds())
            post.save()

            
            # Crear notificación
            Notification.objects.create(
                user=post.author,
                notification_type='like',
                actor=request.user,
                post=post
            )
            return Response({'detail': 'Like agregado'}, status=status.HTTP_201_CREATED)
        else:
            like.delete()
            post.likes_count = max(0, post.likes_count - 1)
            post.save()
            return Response({'detail': 'Like removido'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        post = self.get_object()
        
        # Si el post está expirado, no se pueden hacer comentarios
        if post.is_expired:
            from rest_framework.exceptions import NotFound
            raise NotFound("Post expirado, no se pueden agregar comentarios")
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post, user=request.user)
            post.comments_count += 1
            post.save()
            
            # Crear notificación
            Notification.objects.create(
                user=post.author,
                notification_type='comment',
                actor=request.user,
                post=post,
                payload={'comment': serializer.data['text']}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def repost(self, request, pk=None):
        post = self.get_object()
        repost, created = Repost.objects.get_or_create(original_post=post, user=request.user)
        
        if created:
            post.reposts_count += 1
            post.save()
            return Response({'detail': 'Post compartido'}, status=status.HTTP_201_CREATED)
        else:
            repost.delete()
            post.reposts_count = max(0, post.reposts_count - 1)
            post.save()
            return Response({'detail': 'Repost removido'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def feed(self, request):
        """Get personalized feed for logged-in user"""
        from django.db.models import Q
        user = request.user
        
        # Posts de usuarios que sigue
        following_users = user.following.values_list('followee', flat=True)
        
        # Obtener posts originales de usuarios que sigue
        posts_from_following = Post.objects.filter(
            author_id__in=following_users, 
            is_expired=False
        )
        
        # Obtener reposts de usuarios que sigue
        reposts_from_following = Repost.objects.filter(
            user_id__in=following_users
        ).select_related('original_post').values_list('original_post_id', flat=True)
        
        # Combinar posts originales y posts reposteados
        posts = Post.objects.filter(
            Q(id__in=posts_from_following) | Q(id__in=reposts_from_following),
            is_expired=False
        ).distinct().order_by('-created_at')
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending posts"""
        posts = Post.objects.filter(is_expired=False).order_by('-likes_count')[:20]
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)


class FollowViewSet(viewsets.ModelViewSet):
    """ViewSet for Follow management"""
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def follow(self, request):
        followee_id = request.data.get('followee_id')
        followee = get_object_or_404(User, id=followee_id)
        
        if followee == request.user:
            return Response({'detail': 'No puedes seguirte a ti mismo'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            followee=followee,
            defaults={'status': 'accepted' if not followee.is_private else 'pending'}
        )
        
        if created:
            if not followee.is_private:
                Notification.objects.create(
                    user=followee,
                    notification_type='follow',
                    actor=request.user
                )
            return Response(FollowSerializer(follow).data, status=status.HTTP_201_CREATED)
        return Response({'detail': 'Ya sigues a este usuario'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def unfollow(self, request):
        followee_id = request.data.get('followee_id')
        follow = get_object_or_404(Follow, follower=request.user, followee_id=followee_id)
        follow.delete()
        return Response({'detail': 'Has dejado de seguir'}, status=status.HTTP_200_OK)


class ChatViewSet(viewsets.ModelViewSet):
    """ViewSet for Chat management"""
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        chat = self.get_object()
        messages = chat.messages.all().order_by('-created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        chat = self.get_object()
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(chat=chat, sender=request.user)
            
            # Mark all messages as read for the sender
            chat.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
            
            # Crear notificación
            for participant in chat.participants.exclude(id=request.user.id):
                Notification.objects.create(
                    user=participant,
                    notification_type='message',
                    actor=request.user,
                    payload={'chat_id': str(chat.id)}
                )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'detail': 'Notificación marcada como leída'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'detail': 'Todas las notificaciones marcadas como leídas'})
