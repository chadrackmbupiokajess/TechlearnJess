from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Course
from notifications.models import Notification

@receiver(post_save, sender=Course)
def create_course_notification(sender, instance, **kwargs):
    """
    Crée une notification pour tous les utilisateurs lorsqu'un cours est publié
    pour la première fois.
    """
    # Vérifie si le cours est publié ET que la notification n'a pas encore été envoyée
    if instance.is_published and not instance.notification_sent:
        users = User.objects.all()
        title = "Nouveau cours disponible !"
        message = f"Le cours '{instance.title}' vient d'être ajouté. Inscrivez-vous dès maintenant !"
        
        # Construire l'URL de l'action
        try:
            action_url = instance.get_absolute_url()
        except Exception:
            action_url = reverse('courses:list')

        # Créer les notifications en masse
        Notification.create_bulk_notification(
            users=users,
            title=title,
            message=message,
            notification_type='course_new',
            action_url=action_url
        )
        
        # Marquer la notification comme envoyée pour ne pas la renvoyer
        # On utilise update() pour éviter de déclencher à nouveau le signal post_save
        Course.objects.filter(pk=instance.pk).update(notification_sent=True)
