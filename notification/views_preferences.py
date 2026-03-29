from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notification.models import NotificationEventType, UserNotificationPreference


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_preferences(request):
    event_types = NotificationEventType.objects.filter(is_active=True).order_by("category", "code")
    user_prefs = {
        (p.event_type_id, p.channel): p.is_enabled
        for p in UserNotificationPreference.objects.filter(user=request.user)
    }

    preferences = []
    for et in event_types:
        channels = {}
        for channel in ("in_app", "email", "sms"):
            default_enabled = et.default_channels.get(channel, False)
            pref_key = (et.id, channel)
            if pref_key in user_prefs:
                enabled = user_prefs[pref_key]
                is_default = False
            else:
                enabled = default_enabled
                is_default = True
            channels[channel] = {"enabled": enabled, "is_default": is_default}

        template = et.templates.filter(language="fr").first()
        label = template.subject if template else et.code

        preferences.append(
            {
                "event_type": et.code,
                "category": et.category,
                "label": label,
                "channels": channels,
            }
        )

    return Response({"preferences": preferences}, status=status.HTTP_200_OK)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_preferences(request):
    items = request.data
    if not isinstance(items, list):
        return Response(
            {"error": "Expected a list of preference objects."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    event_type_cache = {
        et.code: et
        for et in NotificationEventType.objects.filter(
            code__in=[item.get("event_type") for item in items]
        )
    }

    updated = 0
    for item in items:
        et = event_type_cache.get(item.get("event_type"))
        channel = item.get("channel")
        is_enabled = item.get("is_enabled")
        if not et or channel not in ("in_app", "email", "sms") or is_enabled is None:
            continue

        UserNotificationPreference.objects.update_or_create(
            user=request.user,
            event_type=et,
            channel=channel,
            defaults={"is_enabled": bool(is_enabled)},
        )
        updated += 1

    return Response({"updated": updated}, status=status.HTTP_200_OK)
