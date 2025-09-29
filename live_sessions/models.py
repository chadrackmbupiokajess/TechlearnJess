from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import uuid


class LiveSession(models.Model):
    """Session live"""
    STATUS_CHOICES = [
        ('scheduled', 'Programmée'),
        ('live', 'En direct'),
        ('ended', 'Terminée'),
        ('cancelled', 'Annulée'),
    ]
    
    # Informations de base
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_sessions', verbose_name="Formateur")
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, blank=True, null=True, verbose_name="Cours associé")
    
    # Planification
    start_time = models.DateTimeField(verbose_name="Heure de début")
    end_time = models.DateTimeField(verbose_name="Heure de fin")
    timezone = models.CharField(max_length=50, default='Africa/Kinshasa', verbose_name="Fuseau horaire")
    
    # Participants
    participants = models.ManyToManyField(User, through='SessionParticipant', related_name='attended_sessions', verbose_name="Participants")
    max_participants = models.PositiveIntegerField(default=100, verbose_name="Nombre max de participants")
    
    # Statut et métadonnées
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Statut")
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="ID Session")
    
    # Liens et ressources
    meeting_url = models.URLField(blank=True, verbose_name="URL de la réunion")
    recording_url = models.URLField(blank=True, verbose_name="URL d'enregistrement")
    presentation_file = models.FileField(upload_to='live_sessions/presentations/', blank=True, verbose_name="Fichier de présentation")
    
    # Paramètres
    is_recorded = models.BooleanField(default=True, verbose_name="Enregistrer la session")
    is_public = models.BooleanField(default=False, verbose_name="Session publique")
    requires_enrollment = models.BooleanField(default=True, verbose_name="Inscription requise")
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Session Live"
        verbose_name_plural = "Sessions Live"
        ordering = ['start_time']

    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%d/%m/%Y %H:%M')}"

    def get_absolute_url(self):
        return reverse('live_sessions:detail', kwargs={'session_id': self.session_id})

    @property
    def is_upcoming(self):
        return self.start_time > timezone.now()

    @property
    def is_live_now(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.status == 'live'

    @property
    def duration_minutes(self):
        return int((self.end_time - self.start_time).total_seconds() / 60)

    @property
    def participants_count(self):
        return self.participants.count()

    @property
    def available_spots(self):
        return max(0, self.max_participants - self.participants_count)

    def can_join(self, user):
        """Vérifier si un utilisateur peut rejoindre la session"""
        if not self.is_upcoming and not self.is_live_now:
            return False, "La session n'est pas disponible"
        
        if self.requires_enrollment and not self.participants.filter(id=user.id).exists():
            return False, "Vous devez vous inscrire à cette session"
        
        if self.participants_count >= self.max_participants:
            return False, "La session est complète"
        
        return True, "Vous pouvez rejoindre la session"

    def start_session(self):
        """Démarrer la session"""
        self.status = 'live'
        self.save()
        
        # Notifier les participants
        from notifications.models import Notification
        for participant in self.participants.all():
            Notification.create_notification(
                user=participant,
                title="Session live démarrée",
                message=f"La session '{self.title}' a commencé.",
                notification_type='live_session',
                action_url=self.get_absolute_url(),
                action_text="Rejoindre"
            )

    def end_session(self):
        """Terminer la session"""
        self.status = 'ended'
        self.save()


class SessionParticipant(models.Model):
    """Participant à une session live"""
    session = models.ForeignKey(LiveSession, on_delete=models.CASCADE, verbose_name="Session")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Rejoint le")
    left_at = models.DateTimeField(null=True, blank=True, verbose_name="Quitté le")
    is_present = models.BooleanField(default=False, verbose_name="Présent")
    
    class Meta:
        verbose_name = "Participant de session"
        verbose_name_plural = "Participants de session"
        unique_together = ['session', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.session.title}"

    @property
    def attendance_duration(self):
        """Durée de présence en minutes"""
        if self.left_at:
            return int((self.left_at - self.joined_at).total_seconds() / 60)
        elif self.is_present:
            return int((timezone.now() - self.joined_at).total_seconds() / 60)
        return 0


class SessionQuestion(models.Model):
    """Question posée pendant une session live"""
    session = models.ForeignKey(LiveSession, on_delete=models.CASCADE, related_name='questions', verbose_name="Session")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    question = models.TextField(verbose_name="Question")
    answer = models.TextField(blank=True, verbose_name="Réponse")
    is_answered = models.BooleanField(default=False, verbose_name="Répondu")
    is_public = models.BooleanField(default=True, verbose_name="Question publique")
    asked_at = models.DateTimeField(auto_now_add=True, verbose_name="Posée le")
    answered_at = models.DateTimeField(null=True, blank=True, verbose_name="Répondu le")

    class Meta:
        verbose_name = "Question de session"
        verbose_name_plural = "Questions de session"
        ordering = ['asked_at']

    def __str__(self):
        return f"Question de {self.user.username} - {self.session.title}"


class SessionResource(models.Model):
    """Ressource partagée pendant une session"""
    session = models.ForeignKey(LiveSession, on_delete=models.CASCADE, related_name='resources', verbose_name="Session")
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    file = models.FileField(upload_to='live_sessions/resources/', blank=True, verbose_name="Fichier")
    url = models.URLField(blank=True, verbose_name="URL")
    shared_at = models.DateTimeField(auto_now_add=True, verbose_name="Partagé le")

    class Meta:
        verbose_name = "Ressource de session"
        verbose_name_plural = "Ressources de session"
        ordering = ['shared_at']

    def __str__(self):
        return f"{self.title} - {self.session.title}"