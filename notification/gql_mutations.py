import graphene
from django.utils import timezone
from notification.models import Notification


class MarkNotificationReadMutation(graphene.Mutation):
    class Arguments:
        notification_id = graphene.UUID(required=True)
    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, notification_id):
        user = info.context.user
        try:
            notif = Notification.objects.get(id=notification_id, recipient=user)
            notif.is_read = True
            notif.read_at = timezone.now()
            notif.save()
            return MarkNotificationReadMutation(success=True)
        except Notification.DoesNotExist:
            return MarkNotificationReadMutation(success=False)


class MarkAllNotificationsReadMutation(graphene.Mutation):
    success = graphene.Boolean()
    count = graphene.Int()

    @classmethod
    def mutate(cls, root, info):
        user = info.context.user
        count = Notification.objects.filter(recipient=user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        return MarkAllNotificationsReadMutation(success=True, count=count)
