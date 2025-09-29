from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image


class UserProfile(models.Model):
    """Profil étendu de l'utilisateur"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Photo de profil")
    bio = models.TextField(max_length=500, blank=True, verbose_name="Biographie")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Date de naissance")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    address = models.TextField(blank=True, verbose_name="Adresse")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    country = models.CharField(max_length=100, default="République Démocratique du Congo", verbose_name="Pays")
    
    # Préférences
    language = models.CharField(max_length=10, choices=[
        ('fr', 'Français'),
        ('en', 'English'),
    ], default='fr', verbose_name="Langue")
    
    timezone = models.CharField(max_length=50, default='Africa/Kinshasa', verbose_name="Fuseau horaire")
    
    # Notifications
    email_notifications = models.BooleanField(default=True, verbose_name="Notifications par email")
    push_notifications = models.BooleanField(default=True, verbose_name="Notifications push")
    
    # Réseaux sociaux
    website = models.URLField(blank=True, verbose_name="Site web")
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn")
    github = models.URLField(blank=True, verbose_name="GitHub")
    twitter = models.URLField(blank=True, verbose_name="Twitter")
    
    # Métadonnées
    is_instructor = models.BooleanField(default=False, verbose_name="Est formateur")
    is_verified = models.BooleanField(default=False, verbose_name="Compte vérifié")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def __str__(self):
        return f"Profil de {self.user.get_full_name() or self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Redimensionner l'avatar
        if self.avatar:
            img = Image.open(self.avatar.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def total_courses_completed(self):
        """Nombre total de cours terminés"""
        from courses.models import Enrollment
        return Enrollment.objects.filter(user=self.user, is_completed=True).count()

    @property
    def total_certificates(self):
        """Nombre total de certificats obtenus"""
        try:
            from certificates.models import Certificate
            return Certificate.objects.filter(user=self.user).count()
        except ImportError:
            return 0


class LoginHistory(models.Model):
    """Historique des connexions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    ip_address = models.GenericIPAddressField(verbose_name="Adresse IP")
    user_agent = models.TextField(verbose_name="User Agent")
    login_time = models.DateTimeField(auto_now_add=True, verbose_name="Heure de connexion")
    is_successful = models.BooleanField(default=True, verbose_name="Connexion réussie")
    location = models.CharField(max_length=200, blank=True, verbose_name="Localisation")

    class Meta:
        verbose_name = "Historique de connexion"
        verbose_name_plural = "Historiques de connexion"
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.user.username} - {self.login_time.strftime('%d/%m/%Y %H:%M')}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Créer automatiquement un profil lors de la création d'un utilisateur"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarder le profil lors de la sauvegarde de l'utilisateur"""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()