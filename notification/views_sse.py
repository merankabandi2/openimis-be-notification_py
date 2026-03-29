import json
import time
import logging

from django.http import StreamingHttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from notification.models import Notification

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 5
KEEPALIVE_INTERVAL_SECONDS = 30
MAX_IDLE_SECONDS = 300


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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notification_stream(request):
    response = StreamingHttpResponse(
        _stream_notifications(request.user),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
