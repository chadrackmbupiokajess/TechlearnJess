from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Course, Lesson, Enrollment
from notifications.models import Notification

@receiver(post_save, sender=Course)
def create_course_notification(sender, instance, **kwargs):
    """
    Crée une notification pour tous les utilisateurs lorsqu'un cours est publié
    pour la première fois.
    """
    if instance.is_published and not instance.notification_sent:
        users = User.objects.all()
        title = "Nouveau cours disponible !"
        message = f"Le cours '{instance.title}' vient d'être ajouté. Inscrivez-vous dès maintenant !"
        
        try:
            action_url = instance.get_absolute_url()
        except Exception:
            action_url = reverse('courses:list')

        Notification.create_bulk_notification(
            users=users,
            title=title,
            message=message,
            notification_type='course_new',
            action_url=action_url
        )
        
        Course.objects.filter(pk=instance.pk).update(notification_sent=True)


@receiver(post_save, sender=Lesson)
def create_lesson_notification(sender, instance, **kwargs):
    """
    Crée une notification pour tous les utilisateurs lorsqu'une nouvelle leçon est publiée.
    """
    if instance.is_published and not instance.notification_sent:
        # Récupérer tous les utilisateurs de la plateforme
        users = User.objects.all()

        if not users:
            return # Pas d'utilisateurs, pas de notification à envoyer

        title = f"Nouvelle leçon dans '{instance.course.title}'"
        message = f"La leçon '{instance.title}' est maintenant disponible. Plongez-vous dedans !"
        
        try:
            action_url = instance.get_absolute_url()
        except Exception:
            action_url = instance.course.get_absolute_url()

        Notification.create_bulk_notification(
            users=users,
            title=title,
            message=message,
            notification_type='lesson_new',
            action_url=action_url
        )
        
        Lesson.objects.filter(pk=instance.pk).update(notification_sent=True)
