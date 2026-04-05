import json
import time
import logging

import jwt
from django.http import StreamingHttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
from graphql_jwt.exceptions import JSONWebTokenError
from graphql_jwt.shortcuts import get_user_by_token
from graphql_jwt.utils import get_credentials

from notification.models import Notification

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 5
KEEPALIVE_INTERVAL_SECONDS = 30
MAX_IDLE_SECONDS = 300


def _get_authenticated_user(request):
    """Extract and verify JWT token from the request, returning the user or None."""
    token = get_credentials(request)
    if not token:
        return None
    try:
        return get_user_by_token(token)
    except (jwt.PyJWTError, JSONWebTokenError, Exception):
        return None


def _format_sse(data, event=None):
    lines = []
    if event:
        lines.append(f"event: {event}")
    lines.append(f"data: {json.dumps(data)}")
    lines.append("")
    lines.append("")
    return "\n".join(lines)


def _notification_to_dict(notif):
    return {
        "id": str(notif.id),
        "title": notif.title,
        "body": notif.body,
        "entity_url": notif.entity_url,
        "event_type": notif.event_type.code,
        "category": notif.event_type.category,
        "created_at": notif.created_at.isoformat(),
    }


def _stream_notifications(user):
    count = Notification.objects.filter(
        recipient=user, channel="in_app", is_read=False
    ).count()
    yield _format_sse({"count": count}, event="unread_count")

    last_check = timezone.now()
    idle_since = time.monotonic()
    last_keepalive = time.monotonic()

    while True:
        time.sleep(POLL_INTERVAL_SECONDS)

        new_notifications = list(
            Notification.objects.filter(
                recipient=user,
                channel="in_app",
                created_at__gt=last_check,
            )
            .select_related("event_type")
            .order_by("created_at")
        )

        if new_notifications:
            last_check = new_notifications[-1].created_at
            idle_since = time.monotonic()
            for notif in new_notifications:
                yield _format_sse(_notification_to_dict(notif))
        else:
            now = time.monotonic()
            if now - last_keepalive >= KEEPALIVE_INTERVAL_SECONDS:
                yield ": keepalive\n\n"
                last_keepalive = now

            if now - idle_since >= MAX_IDLE_SECONDS:
                return


@require_GET
def notification_stream(request):
    user = _get_authenticated_user(request)
    if not user:
        return JsonResponse({"error": "Authentication required"}, status=401)

    response = StreamingHttpResponse(
        _stream_notifications(user),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
