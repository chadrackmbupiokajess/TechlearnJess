from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from .models import LiveSession
from notifications.models import Notification

@receiver(post_save, sender=LiveSession)
def live_session_notifications(sender, instance, created, **kwargs):
    """
    Gère les notifications pour les sessions live :
    - A la création (programmée).
    - Au passage en direct.
    """
    users = User.objects.all()
    
    # 1. Notification lors de la programmation de la session
    if created and instance.status == 'scheduled' and not instance.scheduled_notification_sent:
        title = "Nouvelle session live programmée !"
        message = f"La session '{instance.title}' est prévue pour le {instance.start_time.strftime('%d/%m/%Y à %H:%M')}. Ne manquez pas ça !"
        notification_type = 'live_session_scheduled'
        
        try:
            action_url = instance.get_absolute_url()
        except Exception:
            action_url = reverse('live_sessions:list')

        Notification.create_bulk_notification(
            users=users,
            title=title,
            message=message,
            notification_type=notification_type,
            action_url=action_url
        )
        
        LiveSession.objects.filter(pk=instance.pk).update(scheduled_notification_sent=True)

    # 2. Notification lors du passage en direct
    elif instance.status == 'live' and not instance.live_notification_sent:
        title = "La session live commence !"
        message = f"La session '{instance.title}' est maintenant en direct. Rejoignez-nous !"
        notification_type = 'live_session_live'
        
        try:
            action_url = instance.get_absolute_url()
        except Exception:
            action_url = reverse('live_sessions:list')

        Notification.create_bulk_notification(
            users=users,
            title=title,
            message=message,
            notification_type=notification_type,
            action_url=action_url
        )
        
        LiveSession.objects.filter(pk=instance.pk).update(live_notification_sent=True)
