from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()


@register.filter
def friendly_datetime(value):
    if not value:
        return ""

    now = timezone.localtime()
    value = timezone.localtime(value)

    if value.date() == now.date():
        return "Today at " + value.strftime("%I:%M %p")
    elif value.date() == (now - timedelta(days=1)).date():
        return "Yesterday at " + value.strftime("%I:%M %p")
    else:
        return value.strftime("%B %d, %Y at %I:%M %p")
