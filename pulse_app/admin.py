from django.contrib import admin
from .models import (
    User, Post, Like, Comment, Poll, PollOption, PollVote,
    Follow, Chat, Message, Notification, Repost, PostInteraction,
    Mention, Hashtag, PostHashtag, NotificationSettings
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_private', 'created_at')
    search_fields = ('username', 'email', 'bio')
    list_filter = ('is_private', 'created_at')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'post_type', 'created_at', 'is_expired', 'likes_count')
    search_fields = ('author__username', 'text_content')
    list_filter = ('post_type', 'is_expired', 'created_at')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username', 'post__id')
    list_filter = ('created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username', 'text')
    list_filter = ('created_at',)


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'created_at')
    search_fields = ('question',)


@admin.register(PollOption)
class PollOptionAdmin(admin.ModelAdmin):
    list_display = ('poll', 'text', 'votes')
    list_filter = ('poll',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followee', 'status', 'created_at')
    search_fields = ('follower__username', 'followee__username')
    list_filter = ('status', 'created_at')


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')
    filter_horizontal = ('participants',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'chat', 'content_type', 'is_read', 'created_at')
    search_fields = ('sender__username', 'content')
    list_filter = ('is_read', 'content_type', 'created_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'actor', 'is_read', 'created_at')
    search_fields = ('user__username', 'actor__username')
    list_filter = ('notification_type', 'is_read', 'created_at')


@admin.register(Repost)
class RepostAdmin(admin.ModelAdmin):
    list_display = ('user', 'original_post', 'created_at')
    search_fields = ('user__username',)


@admin.register(PostInteraction)
class PostInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'has_reacted', 'created_at', 'updated_at')
    search_fields = ('user__username', 'post__id')
    list_filter = ('has_reacted', 'created_at')


@admin.register(Mention)
class MentionAdmin(admin.ModelAdmin):
    list_display = ('mentioned_user', 'mentioned_by', 'post', 'comment', 'created_at')
    search_fields = ('mentioned_user__username', 'mentioned_by__username')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ('name', 'usage_count', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)


@admin.register(PostHashtag)
class PostHashtagAdmin(admin.ModelAdmin):
    list_display = ('post', 'hashtag', 'created_at')
    search_fields = ('hashtag__name', 'post__author__username')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'notify_likes', 'notify_comments', 'notify_follows', 'notify_mentions')
    search_fields = ('user__username',)
    list_filter = ('notify_likes', 'notify_comments', 'notify_follows', 'notify_mentions')
