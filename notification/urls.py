from django.urls import path

from notification.views import notification_list, unread_count, mark_read, mark_all_read
from notification.views_sse import notification_stream
from notification.views_preferences import get_preferences, update_preferences

urlpatterns = [
    path("", notification_list, name="notification-list"),
    path("unread_count/", unread_count, name="notification-unread-count"),
    path("<uuid:notification_id>/read/", mark_read, name="notification-mark-read"),
    path("read_all/", mark_all_read, name="notification-mark-all-read"),
    path("stream/", notification_stream, name="notification-stream"),
    path("preferences/", get_preferences, name="notification-preferences-get"),
    path("preferences/update/", update_preferences, name="notification-preferences-update"),
]
