from django.db import models
from django.contrib.auth.models import User


class SiteSettings(models.Model):
    """Paramètres généraux du site"""
    site_name = models.CharField(max_length=100, default="TechLearnJess")
    site_slogan = models.CharField(max_length=200, default="Apprendre ici, réussir partout.")
    site_description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/', blank=True, null=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    maintenance_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"

    def __str__(self):
        return self.site_name

    @classmethod
    def get_settings(cls):
        """Récupère les paramètres du site (singleton)"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class Testimonial(models.Model):
    """Témoignages d'utilisateurs"""
    name = models.CharField(max_length=100, verbose_name="Nom")
    position = models.CharField(max_length=100, verbose_name="Poste/Fonction", blank=True)
    company = models.CharField(max_length=100, verbose_name="Entreprise", blank=True)
    content = models.TextField(verbose_name="Témoignage")
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True, verbose_name="Photo")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5, verbose_name="Note")
    is_featured = models.BooleanField(default=False, verbose_name="Mis en avant")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Témoignage"
        verbose_name_plural = "Témoignages"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.rating}/5"


class FAQ(models.Model):
    """Questions fréquemment posées"""
    question = models.CharField(max_length=200, verbose_name="Question")
    answer = models.TextField(verbose_name="Réponse")
    category = models.CharField(max_length=50, choices=[
        ('general', 'Général'),
        ('courses', 'Cours'),
        ('payment', 'Paiement'),
        ('technical', 'Technique'),
        ('certificates', 'Certificats'),
    ], default='general', verbose_name="Catégorie")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"
        ordering = ['category', 'order', 'question']

    def __str__(self):
        return self.question