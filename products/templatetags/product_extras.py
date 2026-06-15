from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def days_since(value):
    """
    Returns the number of whole days since `value` (a datetime).
    Usage: {{ product.created_at|days_since }}
    Returns a very large number if value is None, so 'is new' checks
    safely evaluate to False.
    """
    if not value:
        return 9999

    delta = timezone.now() - value
    return delta.days


@register.filter
def is_new(value, days=7):
    """
    Returns True if `value` (a datetime) is within the last `days` days.
    Usage: {{ product.created_at|is_new }}  -> defaults to 7 days
            {{ product.created_at|is_new:3 }} -> custom window
    """
    if not value:
        return False

    delta = timezone.now() - value
    return delta.days < int(days)