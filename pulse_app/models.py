from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from datetime import timedelta
from django.utils import timezone


class User(AbstractUser):
    """Custom User model for Pulse app"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bio = models.TextField(blank=True, null=True, max_length=500)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    is_private = models.BooleanField(default=False)
    
    # Nuevos campos de perfil
    display_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    pronouns = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="pulse_user_groups",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="pulse_user_permissions",
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"@{self.username}"


class Follow(models.Model):
    """Model for follow relationships"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    followee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='accepted')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followee')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} -> {self.followee.username}"


class Post(models.Model):
    """Model for posts (ephemeral content)"""
    TYPE_CHOICES = [
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('text', 'Text'),
        ('poll', 'Poll'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    content_url = models.FileField(upload_to='posts/', blank=True, null=True)
    text_content = models.TextField(blank=True, null=True, max_length=2000)
    
    # Ephemeral logic
    created_at = models.DateTimeField(auto_now_add=True)
    initial_life_seconds = models.IntegerField(default=300)  # 5 minutes
    life_seconds_remaining = models.IntegerField(default=300)
    total_life_seconds_reached = models.IntegerField(default=0)  # For metrics
    is_expired = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Interactions
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    reposts_count = models.IntegerField(default=0)
    
    # Post settings
    is_pinned = models.BooleanField(default=False)
    comments_disabled = models.BooleanField(default=False)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['-created_at', 'is_expired']),
        ]

    def __str__(self):
        return f"Post by {self.author.username} ({self.post_type})"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(seconds=self.initial_life_seconds)
        super().save(*args, **kwargs)


class Like(models.Model):
    """Model for likes on posts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
        indexes = [
            models.Index(fields=['post', 'user']),
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"


class Comment(models.Model):
    """Model for comments on posts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.id}"


class Poll(models.Model):
    """Model for poll posts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='poll')
    question = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Poll: {self.question[:50]}"


class PollOption(models.Model):
    """Model for poll options"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    @property
    def percentage(self):
        """Calculate the percentage of votes for this option"""
        total_votes = sum(option.votes for option in self.poll.options.all())
        if total_votes == 0:
            return 0
        return round((self.votes / total_votes) * 100, 1)

    def __str__(self):
        return self.text


class PollVote(models.Model):
    """Model for poll votes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='poll_votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poll_votes')
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('poll', 'user')

    def __str__(self):
        return f"{self.user.username} voted on {self.poll.id}"


class Chat(models.Model):
    """Model for direct message conversations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat {self.id}"


class Message(models.Model):
    """Model for direct messages"""
    CONTENT_TYPE_CHOICES = [
        ('text', 'Text'),
        ('post_share', 'Post Share'),
        ('media', 'Media'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='text')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['chat', '-created_at']),
        ]

    def __str__(self):
        return f"Message from {self.sender.username} in chat {self.chat.id}"


class Notification(models.Model):
    """Model for notifications"""
    TYPE_CHOICES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('message', 'Message'),
        ('expire', 'Post Expired'),
        ('mention', 'Mention'),
        ('repost', 'Repost'),
        ('follow_request', 'Follow Request'),
        ('post_expiring', 'Post Expiring Soon'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='actions')
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.ForeignKey('Comment', on_delete=models.SET_NULL, null=True, blank=True)
    payload = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['user', 'notification_type', '-created_at']),
        ]

    def __str__(self):
        return f"Notification for {self.user.username}: {self.notification_type}"


class Repost(models.Model):
    """Model for reposts/shares"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reposts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reposts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('original_post', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} reposted {self.original_post.id}"


class PostInteraction(models.Model):
    """Model to track post interactions (views, reactions) for feed algorithm"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_interactions')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='interactions')
    has_reacted = models.BooleanField(default=False)  # Like, comment, or repost
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['user', 'has_reacted']),
            models.Index(fields=['post', 'has_reacted']),
        ]

    def __str__(self):
        return f"{self.user.username} interacted with {self.post.id}"


class Mention(models.Model):
    """Model for user mentions in posts and comments"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mentioned_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentions')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='mentions')
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True, related_name='mentions')
    mentioned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentions_made')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['mentioned_user', '-created_at']),
        ]

    def __str__(self):
        return f"@{self.mentioned_user.username} mentioned by {self.mentioned_by.username}"


class Hashtag(models.Model):
    """Model for hashtags"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, db_index=True)
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-usage_count']

    def __str__(self):
        return f"#{self.name}"


class PostHashtag(models.Model):
    """Model for post-hashtag relationship"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='hashtags')
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'hashtag')
        indexes = [
            models.Index(fields=['hashtag', '-created_at']),
        ]

    def __str__(self):
        return f"{self.post.id} - {self.hashtag.name}"


class NotificationSettings(models.Model):
    """Model for user notification preferences"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    
    # Granular settings
    notify_likes = models.BooleanField(default=True)
    notify_comments = models.BooleanField(default=True)
    notify_mentions = models.BooleanField(default=True)
    notify_follows = models.BooleanField(default=True)
    notify_messages = models.BooleanField(default=True)
    notify_reposts = models.BooleanField(default=True)
    notify_post_expiring = models.BooleanField(default=True)
    notify_friend_reminder = models.BooleanField(default=False)
    
    # Time before expiry to notify (in seconds)
    expiring_threshold = models.IntegerField(default=60)  # 1 minute
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification settings for {self.user.username}"

