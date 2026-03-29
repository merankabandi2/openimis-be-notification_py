import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def _get_setting(name, default=""):
    return getattr(settings, name, default)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def deliver_email(self, notification_id):
    """Send email for a Notification record. Retries up to 3 times on failure."""
    from notification.models import Notification

    try:
        notif = Notification.objects.select_related("recipient", "event_type").get(
            id=notification_id
        )
    except Notification.DoesNotExist:
        logger.error("deliver_email: Notification %s not found.", notification_id)
        return

    recipient_email = getattr(notif.recipient, "email", None)
    if not recipient_email:
        logger.warning(
            "deliver_email: No email for user %s, marking failed.", notif.recipient
        )
        notif.delivery_status = "failed"
        notif.save(update_fields=["delivery_status"])
        return

    app_base_url = _get_setting("NOTIFICATION_APP_BASE_URL", "http://localhost:3000/front")
    from_email = _get_setting("NOTIFICATION_EMAIL_FROM", "noreply@merankabandi.bi")
    logo_url = _get_setting("NOTIFICATION_EMAIL_LOGO_URL", "")

    action_url = f"{app_base_url}{notif.entity_url}" if notif.entity_url else ""

    html_body = render_to_string(
        "notification/email_base.html",
        {
            "subject": notif.title,
            "body": notif.body,
            "action_url": action_url,
            "action_label": "Voir dans l'application",
            "logo_url": logo_url,
        },
    )

    try:
        send_mail(
            subject=notif.title,
            message=notif.body,
            from_email=from_email,
            recipient_list=[recipient_email],
            html_message=html_body,
            fail_silently=False,
        )
        notif.delivery_status = "delivered"
        notif.save(update_fields=["delivery_status"])
        logger.info("deliver_email: Sent to %s for event %s.", recipient_email, notif.event_type.code)
    except Exception as exc:
        logger.error("deliver_email: Failed for %s: %s", recipient_email, exc)
        try:
            self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            notif.delivery_status = "failed"
            notif.save(update_fields=["delivery_status"])
            logger.error("deliver_email: Max retries exceeded for %s.", notification_id)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def deliver_sms(self, notification_id):
    """Send SMS for a Notification record via the configured adapter."""
    from notification.models import Notification
    from notification.adapters import get_sms_adapter

    try:
        notif = Notification.objects.select_related("recipient", "event_type").get(
            id=notification_id
        )
    except Notification.DoesNotExist:
        logger.error("deliver_sms: Notification %s not found.", notification_id)
        return

    phone = getattr(notif.recipient, "phone", None) or ""
    if not phone:
        logger.warning("deliver_sms: No phone for user %s, marking failed.", notif.recipient)
        notif.delivery_status = "failed"
        notif.save(update_fields=["delivery_status"])
        return

    sms_text = notif.title
    if len(sms_text) > 160:
        sms_text = sms_text[:157] + "..."

    try:
        adapter = get_sms_adapter()
        success = adapter.send(phone, sms_text)
        notif.delivery_status = "delivered" if success else "failed"
        notif.save(update_fields=["delivery_status"])
    except Exception as exc:
        logger.error("deliver_sms: Failed for %s: %s", phone, exc)
        try:
            self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            notif.delivery_status = "failed"
            notif.save(update_fields=["delivery_status"])
