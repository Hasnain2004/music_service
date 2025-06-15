from django import template

register = template.Library()

@register.filter(name='format_duration')
def format_duration(seconds):
    """Convert seconds to MM:SS format"""
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}" 