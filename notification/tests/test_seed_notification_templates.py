import re
from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase

from notification.models import NotificationEventType, NotificationTemplate
from notification.seed_data import FRENCH_TEMPLATES

UNACCENTED_WORDS = (
    " ete ", "creee", "Categorie", "Priorite", "passee", "reouverte", "assignee",
    "approuve", "rejete", "reconcilie", "Activite", "validee", "rejetee",
    "Selection", "terminee", "menages", "beneficiaires", "Tache", "completee", "echoue",
)


class FrenchTemplatesTextTest(SimpleTestCase):

    def test_subjects_and_bodies_are_written_with_accents(self):
        for code, (subject, body, _) in FRENCH_TEMPLATES.items():
            for word in UNACCENTED_WORDS:
                with self.subTest(code=code, word=word):
                    self.assertNotIn(word, subject)
                    self.assertNotIn(word, body)

    def test_grievance_bodies(self):
        self.assertEqual(
            FRENCH_TEMPLATES["grievance.created"][1],
            "Une nouvelle plainte #{ticket_number} a été enregistrée.")
        self.assertEqual(
            FRENCH_TEMPLATES["grievance.status_changed"][1],
            "Le statut de la plainte #{ticket_number} a changé.")

    def test_grievance_templates_carry_the_ticket_number_only(self):
        for code, texts in FRENCH_TEMPLATES.items():
            if not code.startswith("grievance."):
                continue
            for text in texts:
                with self.subTest(code=code, text=text):
                    placeholders = set(re.findall(r"{(\w+)}", text))
                    self.assertLessEqual(placeholders, {"ticket_number"})


class SeedNotificationTemplatesCommandTest(TestCase):

    def test_reseed_rewrites_templates_and_keeps_event_type_settings(self):
        event_type = NotificationEventType.objects.get(code="grievance.created")
        event_type.default_channels = {"in_app": True, "email": False, "sms": False}
        event_type.is_active = False
        event_type.save()
        NotificationTemplate.objects.filter(event_type=event_type, language="fr").update(
            body="Une nouvelle plainte #{ticket_number} a ete creee.")

        call_command("seed_notification_templates", stdout=StringIO())

        event_type.refresh_from_db()
        self.assertEqual(event_type.default_channels, {"in_app": True, "email": False, "sms": False})
        self.assertFalse(event_type.is_active)
        template = NotificationTemplate.objects.get(event_type=event_type, language="fr")
        self.assertEqual(template.body, FRENCH_TEMPLATES["grievance.created"][1])

    def test_missing_event_type_is_created_with_its_defaults(self):
        NotificationEventType.objects.filter(code="grievance.reopened").delete()

        call_command("seed_notification_templates", stdout=StringIO())

        event_type = NotificationEventType.objects.get(code="grievance.reopened")
        self.assertTrue(event_type.is_active)
        self.assertEqual(event_type.default_channels, {"in_app": True, "email": True, "sms": False})
        self.assertTrue(NotificationTemplate.objects.filter(event_type=event_type, language="fr").exists())

    def test_analytics_export_events_are_seeded_in_app_only(self):
        call_command("seed_notification_templates", stdout=StringIO())

        for code, placeholders in (
            ("analytics.export_ready", {"export_format", "row_count"}),
            ("analytics.export_failed", {"export_format", "reason"}),
        ):
            with self.subTest(code=code):
                event_type = NotificationEventType.objects.get(code=code)
                self.assertEqual(event_type.category, "report")
                self.assertEqual(event_type.default_channels, {"in_app": True, "email": False, "sms": False})
                template = NotificationTemplate.objects.get(event_type=event_type, language="fr")
                self.assertEqual(set(re.findall(r"{(\w+)}", template.body)), placeholders)
