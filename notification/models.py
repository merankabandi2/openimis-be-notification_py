import uuid

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.models import User


class NotificationEventType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50)
    default_channels = models.JSONField(
        default=dict,
        help_text='e.g. {"in_app": true, "email": true, "sms": false}',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "notification_event_type"
        ordering = ["category", "code"]

    def __str__(self):
        return self.code


class NotificationTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.ForeignKey(
        NotificationEventType,
        on_delete=models.CASCADE,
        related_name="templates",
    )
    language = models.CharField(max_length=5, default="fr")
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sms_body = models.CharField(max_length=160, blank=True, default="")

    class Meta:
        db_table = "notification_template"
        unique_together = ("event_type", "language")

    def __str__(self):
        return f"{self.event_type.code} [{self.language}]"

    def render(self, context):
        rendered_subject = self.subject
        rendered_body = self.body
        rendered_sms = self.sms_body
        for key, value in context.items():
            placeholder = "{" + key + "}"
            str_value = str(value) if value is not None else ""
            rendered_subject = rendered_subject.replace(placeholder, str_value)
            rendered_body = rendered_body.replace(placeholder, str_value)
            rendered_sms = rendered_sms.replace(placeholder, str_value)
        return rendered_subject, rendered_body, rendered_sms


CHANNEL_CHOICES = [
    ("in_app", "In-App"),
    ("email", "Email"),
    ("sms", "SMS"),
]

DELIVERY_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("delivered", "Delivered"),
    ("failed", "Failed"),
]


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.ForeignKey(
        NotificationEventType,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    title = models.CharField(max_length=255)
    body = models.TextField()
    entity_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    entity_id = models.UUIDField(null=True, blank=True)
    entity = GenericForeignKey("entity_type", "entity_id")
    entity_url = models.CharField(max_length=255, blank=True, default="")
    is_read = models.BooleanField(default=False)
    delivery_status = models.CharField(
        max_length=20,
        choices=DELIVERY_STATUS_CHOICES,
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "notification_notification"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["recipient", "created_at", "is_read"],
                name="idx_notif_rcpt_created_read",
            ),
        ]

    def __str__(self):
        return f"[{self.channel}] {self.title} -> {self.recipient}"


class UserNotificationPreference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    event_type = models.ForeignKey(
        NotificationEventType,
        on_delete=models.CASCADE,
        related_name="user_preferences",
    )
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        db_table = "notification_user_preference"
        unique_together = ("user", "event_type", "channel")

    def __str__(self):
        return f"{self.user} | {self.event_type.code} | {self.channel} = {self.is_enabled}"
