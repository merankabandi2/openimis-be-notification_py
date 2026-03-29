from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notification.models import Notification
from notification.serializers import NotificationSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notification_list(request):
    qs = Notification.objects.filter(
        recipient=request.user, channel="in_app"
    ).select_related("event_type")

    category = request.query_params.get("category")
    if category:
        qs = qs.filter(event_type__category=category)
    is_read = request.query_params.get("is_read")
    if is_read is not None:
        qs = qs.filter(is_read=is_read.lower() == "true")

    limit = int(request.query_params.get("limit", 15))
    offset = int(request.query_params.get("offset", 0))
    total = qs.count()
    notifications = qs[offset : offset + limit]

    serializer = NotificationSerializer(notifications, many=True)
    return Response(
        {"total": total, "notifications": serializer.data},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def unread_count(request):
    count = Notification.objects.filter(
        recipient=request.user, channel="in_app", is_read=False
    ).count()
    return Response({"count": count}, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def mark_read(request, notification_id):
    try:
        notif = Notification.objects.get(id=notification_id, recipient=request.user)
    except Notification.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    notif.is_read = True
    notif.read_at = timezone.now()
    notif.save(update_fields=["is_read", "read_at"])
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    now = timezone.now()
    updated = Notification.objects.filter(
        recipient=request.user, channel="in_app", is_read=False
    ).update(is_read=True, read_at=now)
    return Response({"updated": updated}, status=status.HTTP_200_OK)
