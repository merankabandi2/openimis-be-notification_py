from django.db import migrations


def seed_defaults(apps, schema_editor):
    from notification.seed_data import EVENT_TYPES, FRENCH_TEMPLATES
    NotificationEventType = apps.get_model("notification", "NotificationEventType")
    NotificationTemplate = apps.get_model("notification", "NotificationTemplate")

    for code, category, default_channels in EVENT_TYPES:
        event_type, _ = NotificationEventType.objects.update_or_create(
            code=code,
            defaults={"category": category, "default_channels": default_channels, "is_active": True},
        )
        if code in FRENCH_TEMPLATES:
            subject, body, sms_body = FRENCH_TEMPLATES[code]
            NotificationTemplate.objects.update_or_create(
                event_type=event_type,
                language="fr",
                defaults={"subject": subject, "body": body, "sms_body": sms_body},
            )


def reverse_seed(apps, schema_editor):
    from notification.seed_data import EVENT_TYPES
    NotificationEventType = apps.get_model("notification", "NotificationEventType")
    codes = [code for code, _, _ in EVENT_TYPES]
    NotificationEventType.objects.filter(code__in=codes).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_defaults, reverse_seed),
    ]
