from django.contrib import admin

from notification.models import (
    NotificationEventType,
    NotificationTemplate,
    Notification,
    UserNotificationPreference,
)


class NotificationTemplateInline(admin.TabularInline):
    model = NotificationTemplate
    extra = 0
    fields = ("language", "subject", "body", "sms_body")


@admin.register(NotificationEventType)
class NotificationEventTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "category", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("code",)
    inlines = [NotificationTemplateInline]


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ("event_type", "language", "subject")
    list_filter = ("language", "event_type__category")
    search_fields = ("subject", "body", "event_type__code")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient", "channel", "delivery_status", "is_read", "created_at")
    list_filter = ("channel", "delivery_status", "is_read", "event_type__category")
    search_fields = ("title", "recipient__username")
    readonly_fields = ("id", "created_at", "read_at")
    date_hierarchy = "created_at"


@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "event_type", "channel", "is_enabled")
    list_filter = ("channel", "is_enabled")
    search_fields = ("user__username", "event_type__code")
