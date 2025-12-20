from rest_framework import serializers
from .models import (
    User, Post, Like, Comment, Poll, PollOption, PollVote,
    Follow, Chat, Message, Notification, Repost
)
from django.contrib.auth import authenticate
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'bio', 'profile_photo', 'is_private', 'created_at',
                  'followers_count', 'following_count', 'posts_count']
        read_only_fields = ['id', 'created_at']

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_posts_count(self, obj):
        return obj.posts.count()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if not user:
            raise serializers.ValidationError("Credenciales inválidas")
        return {'user': user}


class PollOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollOption
        fields = ['id', 'text', 'votes']


class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True)

    class Meta:
        model = Poll
        fields = ['id', 'question', 'options', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'created_at']
        read_only_fields = ['id', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    poll = PollSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    time_remaining_seconds = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'post_type', 'content_url', 'text_content',
                  'created_at', 'expires_at', 'is_expired', 'initial_life_seconds',
                  'life_seconds_remaining', 'time_remaining_seconds', 'likes_count', 'comments_count',
                  'reposts_count', 'likes', 'comments', 'poll', 'is_liked']
        read_only_fields = ['id', 'created_at', 'expires_at', 'is_expired',
                           'likes_count', 'comments_count', 'reposts_count', 'time_remaining_seconds']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_time_remaining_seconds(self, obj):
        """Calcula el tiempo restante en el servidor basado en created_at + initial_life_seconds"""
        if obj.is_expired:
            return 0
        
        # Calcular el tiempo de expiración basado en created_at + initial_life_seconds
        def get_time_remaining_seconds(self, obj):
            if obj.is_expired or not obj.expires_at:
                return 0

            remaining = (obj.expires_at - timezone.now()).total_seconds()
            return max(0, int(remaining))



class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['post_type', 'content_url', 'text_content']


class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    followee = UserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followee', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'content_type', 'content', 
                  'is_read', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']


class ChatSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'participants', 'last_message', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_last_message(self, obj):
        message = obj.messages.first()
        if message:
            return MessageSerializer(message).data
        return None


class NotificationSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)
    post = PostSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'actor', 'post', 'payload',
                  'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class RepostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    original_post = PostSerializer(read_only=True)

    class Meta:
        model = Repost
        fields = ['id', 'user', 'original_post', 'created_at']
        read_only_fields = ['id', 'created_at']
