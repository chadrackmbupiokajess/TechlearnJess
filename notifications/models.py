from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Notification(models.Model):
    """Modèle de notification"""
    NOTIFICATION_TYPES = [
        ('course_new', 'Nouveau cours'),
        ('course_update', 'Mise à jour de cours'),
        ('lesson_new', 'Nouvelle leçon'),
        ('message', 'Nouveau message'),
        ('forum_reply', 'Réponse au forum'),
        ('live_session', 'Session live'),
        ('certificate', 'Certificat disponible'),
        ('payment', 'Paiement'),
        ('system', 'Système'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    title = models.CharField(max_length=200, verbose_name="Titre")
    message = models.TextField(verbose_name="Message")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, verbose_name="Type")
    
    # Liens et actions
    action_url = models.URLField(blank=True, verbose_name="URL d'action")
    action_text = models.CharField(max_length=50, blank=True, verbose_name="Texte du bouton")
    
    # Métadonnées
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Lu le")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    # Données supplémentaires (JSON)
    extra_data = models.JSONField(default=dict, blank=True, verbose_name="Données supplémentaires")

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        """Marquer comme lu"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    @classmethod
    def create_notification(cls, user, title, message, notification_type, action_url='', action_text='', extra_data=None):
        """Créer une nouvelle notification"""
        return cls.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            action_url=action_url,
            action_text=action_text,
            extra_data=extra_data or {}
        )

    @classmethod
    def create_bulk_notification(cls, users, title, message, notification_type, action_url='', action_text='', extra_data=None):
        """Créer des notifications en masse"""
        notifications = []
        for user in users:
            notifications.append(cls(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                action_url=action_url,
                action_text=action_text,
                extra_data=extra_data or {}
            ))
        return cls.objects.bulk_create(notifications)


class NotificationSettings(models.Model):
    """Paramètres de notification par utilisateur"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    
    # Notifications par email
    email_course_new = models.BooleanField(default=True, verbose_name="Nouveaux cours")
    email_course_update = models.BooleanField(default=True, verbose_name="Mises à jour de cours")
    email_message = models.BooleanField(default=True, verbose_name="Messages")
    email_forum_reply = models.BooleanField(default=True, verbose_name="Réponses au forum")
    email_live_session = models.BooleanField(default=True, verbose_name="Sessions live")
    email_certificate = models.BooleanField(default=True, verbose_name="Certificats")
    email_payment = models.BooleanField(default=True, verbose_name="Paiements")
    
    # Notifications push
    push_course_new = models.BooleanField(default=True, verbose_name="Nouveaux cours")
    push_course_update = models.BooleanField(default=True, verbose_name="Mises à jour de cours")
    push_message = models.BooleanField(default=True, verbose_name="Messages")
    push_forum_reply = models.BooleanField(default=True, verbose_name="Réponses au forum")
    push_live_session = models.BooleanField(default=True, verbose_name="Sessions live")
    push_certificate = models.BooleanField(default=True, verbose_name="Certificats")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres de notification"
        verbose_name_plural = "Paramètres de notifications"

    def __str__(self):
        return f"Paramètres de {self.user.username}"