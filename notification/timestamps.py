from django.conf import settings
from django.utils import timezone


def storage_timezone():
    """Zone of the datetimes the ORM returns.

    With USE_TZ off they are naive wall-clock values in settings.TIME_ZONE.
    """
    if settings.USE_TZ:
        return timezone.get_current_timezone()
    return timezone.get_default_timezone()


def isoformat_with_offset(value):
    """ISO 8601 text with an explicit offset (``Z`` for UTC), as DRF renders it."""
    if timezone.is_naive(value):
        value = timezone.make_aware(value, storage_timezone())
    text = value.isoformat()
    if text.endswith("+00:00"):
        text = text[:-6] + "Z"
    return text
