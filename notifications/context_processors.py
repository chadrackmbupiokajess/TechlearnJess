from .models import Notification

def unread_notifications(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        recent_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
        return {
            'unread_notification_count': unread_count,
            'recent_notifications': recent_notifications
        }
    return {}
