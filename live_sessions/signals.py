from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from .models import LiveSession
from notifications.models import Notification

@receiver(post_save, sender=LiveSession)
def create_live_session_notification(sender, instance, created, **kwargs):
    """
    Crée une notification pour tous les utilisateurs lorsqu'une nouvelle session live
    est programmée.
    """
    # On envoie la notification uniquement à la création de la session
    if created and not instance.scheduled_notification_sent:
        users = User.objects.all()
        title = "Nouvelle session live programmée !"
        message = f"La session '{instance.title}' est prévue pour le {instance.start_time.strftime('%d/%m/%Y à %H:%M')}. Ne manquez pas ça !"

        try:
            action_url = instance.get_absolute_url()
        except Exception:
            action_url = reverse('live_sessions:list')

        Notification.create_bulk_notification(
            users=users,
            title=title,
            message=message,
            notification_type='live_session_scheduled',
            action_url=action_url
        )

        # Marquer la notification comme envoyée
        LiveSession.objects.filter(pk=instance.pk).update(scheduled_notification_sent=True)
