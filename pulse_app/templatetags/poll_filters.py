from django import template
from django.utils.safestring import mark_safe
from pulse_app.utils import linkify_text

register = template.Library()

@register.filter
def sum_votes(options):
    """Sum all votes from poll options"""
    total = sum(option.votes for option in options)
    return total if total > 0 else 1  # Evitar división por cero


@register.filter(name='linkify')
def linkify(text):
    """Convert @mentions and #hashtags to links"""
    if not text:
        return ''
    return mark_safe(linkify_text(text))
