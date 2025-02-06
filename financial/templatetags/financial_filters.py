from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtract the arg from the value."""
    try:
        return Decimal(str(value)) - Decimal(str(arg))
    except (ValueError, TypeError):
        return value

@register.filter
def format_amount(value):
    """Format amount with appropriate sign and decimal places."""
    try:
        amount = Decimal(str(value))
        return f"{'+' if amount > 0 else ''}{amount:.8f}"
    except (ValueError, TypeError):
        return value

@register.filter
def get_status_class(status):
    """Return appropriate Bootstrap class for transaction status."""
    status_classes = {
        'pending': 'warning',
        'completed': 'success',
        'failed': 'danger',
        'cancelled': 'secondary'
    }
    return status_classes.get(status, 'primary') 