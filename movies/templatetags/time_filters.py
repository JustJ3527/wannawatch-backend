from django import template

register = template.Library()

@register.filter
def duration_format(value):
    if not value:
        return ""
    hours = value // 60
    minutes = value % 60
    return f"{hours}h{minutes:02d}" if hours else f"{minutes}min"

@register.filter
def year(value):
    if not value:
        return ""
    return str(value)[:4]