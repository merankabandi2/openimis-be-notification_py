from datetime import datetime, timedelta, timezone as dt_timezone
from zoneinfo import ZoneInfo

from core.test_helpers import create_test_interactive_user
from django.test import TestCase, override_settings
from django.utils.dateparse import parse_datetime

from notification.models import Notification, NotificationEventType
from notification.serializers import NotificationSerializer
from notification.views_sse import _notification_to_dict

NAIVE = datetime(2026, 9, 25, 11, 12, 22, 106650)


def _unsaved_notification(created_at, read_at=None):
    event_type = NotificationEventType(code="ts_test", category="grievance")
    return Notification(
        event_type=event_type,
        channel="in_app",
        title="t",
        body="",
        created_at=created_at,
        read_at=read_at,
    )


class NotificationTimestampOffsetTest(TestCase):
    """Timestamps leave the API with an explicit offset, so a client in any
    time zone reads the same instant the server stored."""

    def assertInstant(self, text, expected):
        parsed = parse_datetime(text)
        self.assertIsNotNone(parsed, text)
        self.assertIsNotNone(parsed.tzinfo, f"no offset in {text!r}")
        self.assertEqual(parsed, expected)

    @override_settings(USE_TZ=False, TIME_ZONE="UTC")
    def test_serializer_marks_naive_utc_values_as_utc(self):
        data = NotificationSerializer(
            _unsaved_notification(NAIVE, read_at=NAIVE + timedelta(minutes=3))
        ).data

        self.assertEqual(data["created_at"], "2026-09-25T11:12:22.106650Z")
        self.assertInstant(data["created_at"], NAIVE.replace(tzinfo=dt_timezone.utc))
        self.assertInstant(
            data["read_at"],
            (NAIVE + timedelta(minutes=3)).replace(tzinfo=dt_timezone.utc),
        )

    @override_settings(USE_TZ=False, TIME_ZONE="Africa/Bujumbura")
    def test_serializer_reads_naive_values_in_the_configured_time_zone(self):
        data = NotificationSerializer(_unsaved_notification(NAIVE)).data

        self.assertInstant(
            data["created_at"], NAIVE.replace(tzinfo=ZoneInfo("Africa/Bujumbura"))
        )

    @override_settings(USE_TZ=False, TIME_ZONE="UTC")
    def test_serializer_keeps_null_read_at(self):
        data = NotificationSerializer(_unsaved_notification(NAIVE)).data

        self.assertIsNone(data["read_at"])

    @override_settings(USE_TZ=False, TIME_ZONE="UTC")
    def test_stream_payload_marks_naive_utc_values_as_utc(self):
        payload = _notification_to_dict(_unsaved_notification(NAIVE))

        self.assertEqual(payload["created_at"], "2026-09-25T11:12:22.106650Z")
        self.assertInstant(payload["created_at"], NAIVE.replace(tzinfo=dt_timezone.utc))

    @override_settings(USE_TZ=False, TIME_ZONE="Africa/Bujumbura")
    def test_stream_payload_reads_naive_values_in_the_configured_time_zone(self):
        payload = _notification_to_dict(_unsaved_notification(NAIVE))

        self.assertInstant(
            payload["created_at"], NAIVE.replace(tzinfo=ZoneInfo("Africa/Bujumbura"))
        )

    def test_fresh_notification_serializes_to_the_current_instant(self):
        user = create_test_interactive_user(username="ts_user")
        event_type = NotificationEventType.objects.create(
            code="ts_fresh", category="grievance"
        )
        notif = Notification.objects.create(
            event_type=event_type,
            recipient=user,
            channel="in_app",
            title="fresh",
            body="",
        )
        notif.refresh_from_db()

        now = datetime.now(dt_timezone.utc)
        for text in (
            NotificationSerializer(notif).data["created_at"],
            _notification_to_dict(notif)["created_at"],
        ):
            parsed = parse_datetime(text)
            self.assertIsNotNone(parsed.tzinfo, f"no offset in {text!r}")
            self.assertLess(abs(now - parsed), timedelta(minutes=1), text)
