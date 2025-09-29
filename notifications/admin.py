from django.contrib import admin
from .models import Notification, NotificationSettings


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at', 'read_at']
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} notifications marquées comme lues.")
    mark_as_read.short_description = "Marquer comme lues"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False, read_at=None)
        self.message_user(request, f"{queryset.count()} notifications marquées comme non lues.")
    mark_as_unread.short_description = "Marquer comme non lues"


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_course_new', 'email_message', 'push_course_new', 'push_message']
    search_fields = ['user__username']
    list_filter = ['email_course_new', 'email_message', 'push_course_new', 'push_message']