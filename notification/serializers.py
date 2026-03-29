from rest_framework import serializers

from notification.models import Notification, NotificationEventType


class NotificationSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="event_type.category", read_only=True)
    event_code = serializers.CharField(source="event_type.code", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "event_code",
            "category",
            "channel",
            "title",
            "body",
            "entity_url",
            "is_read",
            "delivery_status",
            "created_at",
            "read_at",
        ]
        read_only_fields = fields


class NotificationEventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationEventType
        fields = ["code", "category", "default_channels", "is_active"]
