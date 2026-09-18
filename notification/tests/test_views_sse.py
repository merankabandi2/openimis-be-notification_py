from datetime import timedelta
from unittest.mock import patch

from core.test_helpers import create_test_interactive_user
from django.conf import settings
from django.test import RequestFactory, TestCase
from django.utils import timezone

from notification.models import Notification, NotificationEventType
from notification.views_sse import (
    RETRY_MS,
    _parse_last_event_id,
    _stream_notifications,
    notification_stream,
)


def _events(chunks):
    """Split the streamed text into SSE events (blank-line separated)."""
    text = "".join(chunks)
    return [block for block in text.split("\n\n") if block.strip()]


class NotificationStreamTest(TestCase):
    def setUp(self):
        self.user = create_test_interactive_user(username="sse_user")
        self.event_type = NotificationEventType.objects.create(
            code="sse_test", category="test"
        )

    def _notify(self, title, created_at=None, is_read=False):
        notif = Notification.objects.create(
            event_type=self.event_type,
            recipient=self.user,
            channel="in_app",
            title=title,
            body="",
            is_read=is_read,
        )
        if created_at is not None:
            Notification.objects.filter(pk=notif.pk).update(created_at=created_at)
            notif.refresh_from_db()
        return notif

    def test_first_connection_sends_retry_and_count_then_closes(self):
        self._notify("unread")
        self._notify("read", is_read=True)

        events = _events(_stream_notifications(self.user))

        self.assertEqual(events[0], f"retry: {RETRY_MS}")
        self.assertEqual(len(events), 2)
        self.assertIn("event: unread_count", events[1])
        self.assertIn('data: {"count": 1}', events[1])
        self.assertIn("id: ", events[1])

    def test_reconnection_replays_only_notifications_after_last_event_id(self):
        since = timezone.now() - timedelta(minutes=5)
        self._notify("old", created_at=since - timedelta(minutes=1))
        newer = self._notify("new", created_at=since + timedelta(minutes=1))

        events = _events(_stream_notifications(self.user, since=since))

        self.assertEqual(len(events), 3)
        self.assertIn('"title": "new"', events[1])
        self.assertNotIn("old", "".join(events))
        self.assertIn(f"id: {newer.created_at.isoformat()}", events[1])
        self.assertIn(f"id: {newer.created_at.isoformat()}", events[2])

    def test_reconnection_without_news_keeps_last_event_id(self):
        since = timezone.now() - timedelta(minutes=5)
        self._notify("old", created_at=since - timedelta(minutes=1))

        events = _events(_stream_notifications(self.user, since=since))

        self.assertEqual(len(events), 2)
        self.assertIn(f"id: {since.isoformat()}", events[1])

    def test_parse_last_event_id(self):
        stamp = timezone.now()
        self.assertEqual(_parse_last_event_id(stamp.isoformat()), stamp)
        self.assertIsNone(_parse_last_event_id(None))
        self.assertIsNone(_parse_last_event_id("not-a-date"))
        for raw in ("2026-09-18T10:00:00", "2026-09-18T10:00:00+00:00"):
            parsed = _parse_last_event_id(raw)
            self.assertEqual(timezone.is_aware(parsed), settings.USE_TZ, raw)
            self.assertEqual((parsed.hour, parsed.minute), (10, 0), raw)

    def test_view_streams_and_uses_last_event_id_header(self):
        since = timezone.now() - timedelta(minutes=5)
        self._notify("new", created_at=since + timedelta(minutes=1))
        request = RequestFactory().get(
            "/api/notification/stream/", HTTP_LAST_EVENT_ID=since.isoformat()
        )

        with patch("notification.views_sse._get_authenticated_user", return_value=self.user):
            response = notification_stream(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/event-stream")
        self.assertEqual(response["X-Accel-Buffering"], "no")
        events = _events(chunk.decode() for chunk in response.streaming_content)
        self.assertEqual(len(events), 3)
        self.assertIn('"title": "new"', events[1])

    def test_view_rejects_unauthenticated(self):
        request = RequestFactory().get("/api/notification/stream/")
        with patch("notification.views_sse._get_authenticated_user", return_value=None):
            response = notification_stream(request)
        self.assertEqual(response.status_code, 401)
