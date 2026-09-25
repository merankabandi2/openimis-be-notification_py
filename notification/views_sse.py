import json
import logging
from datetime import timezone as dt_timezone

import jwt
from django.conf import settings
from django.http import StreamingHttpResponse, JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_GET
from graphql_jwt.exceptions import JSONWebTokenError
from graphql_jwt.shortcuts import get_user_by_token
from graphql_jwt.utils import get_credentials

from notification.models import Notification
from notification.timestamps import isoformat_with_offset

logger = logging.getLogger(__name__)

# The stream answers with the current state and closes; the browser's
# EventSource reconnects after this delay, so it is the effective polling
# period of one open tab. A stream that stays open holds a WSGI worker thread
# for its whole life, and a few tabs are enough to starve the worker pool.
RETRY_MS = 60_000


def _get_authenticated_user(request):
    """Extract and verify JWT token from the request, returning the user or None."""
    token = get_credentials(request)
    if not token:
        return None
    try:
        return get_user_by_token(token)
    except (jwt.PyJWTError, JSONWebTokenError, Exception):
        return None


def _parse_last_event_id(value):
    """Timestamp of the last event the browser saw (``Last-Event-ID``), or None."""
    if not value:
        return None
    parsed = parse_datetime(value.strip())
    if parsed is None:
        return None
    # Match the project's time-zone mode: the ORM rejects an aware datetime when
    # USE_TZ is off and a naive one when it is on.
    if settings.USE_TZ and timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, dt_timezone.utc)
    elif not settings.USE_TZ and timezone.is_aware(parsed):
        parsed = timezone.make_naive(parsed, dt_timezone.utc)
    return parsed


def _format_sse(data, event=None, event_id=None):
    lines = []
    if event_id:
        lines.append(f"id: {event_id}")
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
        "created_at": isoformat_with_offset(notif.created_at),
    }


def _stream_notifications(user, since=None):
    """Yield the reconnect delay, the notifications created after ``since``
    (none on a first connection), then the unread count, and stop.

    Every event carries the creation timestamp as ``id`` so the browser sends
    it back as ``Last-Event-ID`` and only newer notifications are replayed.
    """
    yield f"retry: {RETRY_MS}\n\n"

    stamp = timezone.now()
    last_seen = since
    if since is not None:
        new_notifications = (
            Notification.objects.filter(
                recipient=user,
                channel="in_app",
                created_at__gt=since,
            )
            .select_related("event_type")
            .order_by("created_at")
        )
        for notif in new_notifications:
            last_seen = notif.created_at
            yield _format_sse(
                _notification_to_dict(notif), event_id=notif.created_at.isoformat()
            )

    count = Notification.objects.filter(
        recipient=user, channel="in_app", is_read=False
    ).count()
    yield _format_sse(
        {"count": count},
        event="unread_count",
        event_id=(last_seen or stamp).isoformat(),
    )


@require_GET
def notification_stream(request):
    user = _get_authenticated_user(request)
    if not user:
        return JsonResponse({"error": "Authentication required"}, status=401)

    since = _parse_last_event_id(request.META.get("HTTP_LAST_EVENT_ID"))
    response = StreamingHttpResponse(
        _stream_notifications(user, since),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
