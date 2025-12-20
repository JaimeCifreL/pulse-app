"""Utility functions for Pulse app"""
import re
from .models import User, Mention, Hashtag, PostHashtag, Notification


def extract_mentions(text):
    """Extract @username mentions from text"""
    pattern = r'@(\w+)'
    mentions = re.findall(pattern, text)
    return list(set(mentions))  # Remove duplicates


def extract_hashtags(text):
    """Extract #hashtag from text"""
    pattern = r'#(\w+)'
    hashtags = re.findall(pattern, text)
    return list(set(hashtags))  # Remove duplicates


def process_mentions(text, post=None, comment=None, mentioned_by=None):
    """Process mentions in text and create Mention objects and notifications"""
    if not mentioned_by:
        return
    
    usernames = extract_mentions(text)
    mentioned_users = []
    
    for username in usernames:
        try:
            user = User.objects.get(username=username)
            if user != mentioned_by:  # Don't mention yourself
                # Create mention record
                mention = Mention.objects.create(
                    mentioned_user=user,
                    post=post,
                    comment=comment,
                    mentioned_by=mentioned_by
                )
                mentioned_users.append(user)
                
                # Create notification
                should_notify = True
                if hasattr(user, 'notification_settings'):
                    should_notify = user.notification_settings.notify_mentions
                
                if should_notify:
                    Notification.objects.create(
                        user=user,
                        notification_type='mention',
                        actor=mentioned_by,
                        post=post,
                        comment=comment,
                        payload={
                            'text_preview': text[:100] if text else '',
                            'content_type': 'post' if post else 'comment'
                        }
                    )
        except User.DoesNotExist:
            continue
    
    return mentioned_users


def process_hashtags(text, post):
    """Process hashtags in text and create/update Hashtag objects"""
    hashtag_names = extract_hashtags(text)
    hashtag_objects = []
    
    for name in hashtag_names:
        # Get or create hashtag
        hashtag, created = Hashtag.objects.get_or_create(
            name=name.lower(),
            defaults={'usage_count': 0}
        )
        
        # Increment usage count if not already associated with this post
        if not PostHashtag.objects.filter(post=post, hashtag=hashtag).exists():
            hashtag.usage_count += 1
            hashtag.save()
            
            # Create post-hashtag relationship
            PostHashtag.objects.create(post=post, hashtag=hashtag)
        
        hashtag_objects.append(hashtag)
    
    return hashtag_objects


def linkify_text(text):
    """Convert mentions and hashtags to clickable links"""
    # Replace @mentions
    text = re.sub(
        r'@(\w+)',
        r'<a href="/profile/\1/" class="mention">@\1</a>',
        text
    )
    
    # Replace #hashtags
    text = re.sub(
        r'#(\w+)',
        r'<a href="/search/?q=%23\1" class="hashtag">#\1</a>',
        text
    )
    
    return text


def create_notification(user, notification_type, actor=None, post=None, comment=None, payload=None):
    """Create a notification if user has it enabled"""
    # Check user notification settings
    should_notify = True
    if hasattr(user, 'notification_settings'):
        settings = user.notification_settings
        setting_map = {
            'like': settings.notify_likes,
            'comment': settings.notify_comments,
            'mention': settings.notify_mentions,
            'follow': settings.notify_follows,
            'message': settings.notify_messages,
            'repost': settings.notify_reposts,
            'post_expiring': settings.notify_post_expiring,
        }
        should_notify = setting_map.get(notification_type, True)
    
    if should_notify:
        return Notification.objects.create(
            user=user,
            notification_type=notification_type,
            actor=actor,
            post=post,
            comment=comment,
            payload=payload or {}
        )
    
    return None
