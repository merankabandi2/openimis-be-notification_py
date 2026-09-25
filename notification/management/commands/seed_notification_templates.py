from django.core.management.base import BaseCommand

from notification.seed_data import EVENT_TYPES, FRENCH_TEMPLATES
from notification.models import NotificationEventType, NotificationTemplate


class Command(BaseCommand):
    help = (
        "Seed or re-seed default notification event types and French templates (idempotent). "
        "Missing event types are created with their default channels; existing ones keep "
        "their channels and active flag. French templates are overwritten."
    )

    def handle(self, *args, **options):
        created_events = 0
        created_templates = 0
        updated_templates = 0

        for code, category, default_channels in EVENT_TYPES:
            event_type, was_created = NotificationEventType.objects.get_or_create(
                code=code,
                defaults={
                    "category": category,
                    "default_channels": default_channels,
                    "is_active": True,
                },
            )
            if was_created:
                created_events += 1
            elif event_type.category != category:
                event_type.category = category
                event_type.save(update_fields=["category"])

        for code, (subject, body, sms_body) in FRENCH_TEMPLATES.items():
            try:
                event_type = NotificationEventType.objects.get(code=code)
            except NotificationEventType.DoesNotExist:
                self.stderr.write(f"Event type '{code}' not found, skipping template.")
                continue
            _, was_created = NotificationTemplate.objects.update_or_create(
                event_type=event_type,
                language="fr",
                defaults={"subject": subject, "body": body, "sms_body": sms_body},
            )
            if was_created:
                created_templates += 1
            else:
                updated_templates += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {created_events} new event types, "
                f"{created_templates} new templates, {updated_templates} templates rewritten."
            )
        )
