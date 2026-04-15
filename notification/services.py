import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone

from core.models import User

logger = logging.getLogger(__name__)


def _active_user_q():
    """Q filter for active users (validity_to is null or in the future)."""
    now = timezone.now()
    return Q(validity_to__isnull=True) | Q(validity_to__gte=now)


class RecipientResolver:
    """Helpers for signal handlers to resolve notification recipients."""

    @staticmethod
    def by_role(right_id):
        """All active interactive users with a specific permission/right."""
        from core.models import UserRole, RoleRight
        role_ids = RoleRight.objects.filter(
            right_id=right_id,
        ).values_list('role_id', flat=True)
        i_user_ids = UserRole.objects.filter(
            role_id__in=role_ids,
        ).values_list('user_id', flat=True)
        return list(
            User.objects.filter(
                i_user__id__in=i_user_ids,
            ).distinct()
        )

    @staticmethod
    def by_task_group(task):
        """TaskExecutors assigned to the task's TaskGroup."""
        if not task or not task.task_group:
            return []
        from tasks_management.models import TaskExecutor

        executors = TaskExecutor.objects.filter(
            task_group=task.task_group,
            is_deleted=False,
        ).select_related("user")
        return [te.user for te in executors if te.user and te.user.is_active]

    @staticmethod
    def by_assignment(user):
        """Wrap a single assigned user into a list (or empty if None)."""
        if user and user.is_active:
            return [user]
        return []

    @staticmethod
    def merge(*lists):
        """Deduplicate multiple recipient lists by user id."""
        seen = set()
        merged = []
        for recipient_list in lists:
            for user in recipient_list:
                if user.id not in seen:
                    seen.add(user.id)
                    merged.append(user)
        return merged


class NotificationService:
    """Central notification engine."""

    @staticmethod
    def notify(event_code, actor, entity, entity_url, recipients, context, language="fr"):
        from notification.models import (
            Notification,
            NotificationEventType,
            NotificationTemplate,
            UserNotificationPreference,
        )
        from notification.tasks import deliver_email, deliver_sms

        # 1. Look up event type
        try:
            event_type = NotificationEventType.objects.get(code=event_code)
        except NotificationEventType.DoesNotExist:
            logger.warning("Notification event type '%s' not found, skipping.", event_code)
            return
        if not event_type.is_active:
            return

        # 2. Look up template
        template = NotificationTemplate.objects.filter(
            event_type=event_type, language=language
        ).first()
        if not template:
            template = NotificationTemplate.objects.filter(
                event_type=event_type
            ).first()
        if not template:
            logger.warning("No template for event '%s', skipping.", event_code)
            return

        # Add actor_name to context automatically
        if actor and "actor_name" not in context:
            context["actor_name"] = f"{actor.other_names or ''} {actor.last_name or ''}".strip() or str(actor)

        # 3. Render template
        rendered_subject, rendered_body, rendered_sms = template.render(context)

        # 4. Resolve entity content type
        entity_ct = None
        entity_pk = None
        if entity:
            entity_ct = ContentType.objects.get_for_model(entity)
            entity_pk = entity.pk

        # 5. Load user preferences for this event type in bulk
        actor_id = actor.id if actor else None
        user_ids = [u.id for u in recipients if u.id != actor_id]
        prefs = {}
        for pref in UserNotificationPreference.objects.filter(
            user_id__in=user_ids, event_type=event_type
        ):
            prefs[(pref.user_id, pref.channel)] = pref.is_enabled

        # 6. Create notifications
        default_channels = event_type.default_channels or {}
        notifications_to_create = []

        for recipient in recipients:
            if recipient.id == actor_id:
                continue
            for channel, is_default_enabled in default_channels.items():
                if not is_default_enabled:
                    continue
                # Check user preference override
                pref_key = (recipient.id, channel)
                if pref_key in prefs and not prefs[pref_key]:
                    continue

                delivery_status = "delivered" if channel == "in_app" else "pending"
                notifications_to_create.append(
                    Notification(
                        event_type=event_type,
                        recipient=recipient,
                        channel=channel,
                        title=rendered_subject,
                        body=rendered_body,
                        entity_type=entity_ct,
                        entity_id=entity_pk,
                        entity_url=entity_url,
                        delivery_status=delivery_status,
                    )
                )

        if not notifications_to_create:
            return

        created = Notification.objects.bulk_create(notifications_to_create)

        # 7. Enqueue async delivery for email/sms
        for notif in created:
            if notif.channel == "email":
                deliver_email.delay(str(notif.id))
            elif notif.channel == "sms":
                deliver_sms.delay(str(notif.id))

        logger.info(
            "Notification '%s': created %d notifications for %d recipients.",
            event_code,
            len(created),
            len(user_ids),
        )
