import graphene
from graphene_django import DjangoObjectType

from notification.models import Notification, NotificationEventType
from notification.gql_mutations import (
    MarkNotificationReadMutation,
    MarkAllNotificationsReadMutation,
)


class NotificationEventTypeGQLType(DjangoObjectType):
    class Meta:
        model = NotificationEventType
        fields = ("id", "code", "category", "default_channels", "is_active")


class NotificationGQLType(DjangoObjectType):
    category = graphene.String()

    class Meta:
        model = Notification
        fields = (
            "id", "title", "body", "channel", "entity_url",
            "is_read", "delivery_status", "created_at", "read_at",
        )

    def resolve_category(self, info):
        return self.event_type.category if self.event_type else None


class Query(graphene.ObjectType):
    notifications = graphene.List(
        NotificationGQLType,
        is_read=graphene.Boolean(),
        category=graphene.String(),
        first=graphene.Int(default_value=15),
        offset=graphene.Int(default_value=0),
    )
    notification_unread_count = graphene.Int()

    def resolve_notifications(self, info, is_read=None, category=None, first=15, offset=0):
        user = info.context.user
        if not user or not user.is_authenticated:
            return []
        qs = Notification.objects.filter(
            recipient=user,
            channel="in_app",
        ).select_related("event_type")
        if is_read is not None:
            qs = qs.filter(is_read=is_read)
        if category:
            qs = qs.filter(event_type__category=category)
        return qs[offset:offset + first]

    def resolve_notification_unread_count(self, info):
        user = info.context.user
        if not user or not user.is_authenticated:
            return 0
        return Notification.objects.filter(
            recipient=user, channel="in_app", is_read=False
        ).count()


class Mutation(graphene.ObjectType):
    mark_notification_read = MarkNotificationReadMutation.Field()
    mark_all_notifications_read = MarkAllNotificationsReadMutation.Field()
