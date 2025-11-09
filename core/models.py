from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SiteSettings(models.Model):
    """Paramètres généraux et légaux du site"""
    # --- Informations générales ---
    site_name = models.CharField("Nom du site", max_length=100, default="Jessna TechLearn")
    site_slogan = models.CharField("Slogan du site", max_length=200, default="Apprendre ici, réussir partout.")
    site_description = models.TextField("Description du site", blank=True)
    logo = models.ImageField("Logo", upload_to='site/', blank=True, null=True)
    favicon = models.ImageField("Favicon", upload_to='site/', blank=True, null=True)

    # --- Informations de contact ---
    contact_email = models.EmailField("Email de contact", blank=True, default="jessnatechlearn@gmail.com")
    contact_phone = models.CharField("Téléphone de contact", max_length=20, blank=True, default="+243 891 433 419")
    address = models.TextField("Adresse", blank=True, default="Matadi, Kongo Central, RDC")

    # --- Réseaux sociaux ---
    facebook_url = models.URLField("URL Facebook", blank=True)
    twitter_url = models.URLField("URL Twitter", blank=True)
    linkedin_url = models.URLField("URL LinkedIn", blank=True)
    youtube_url = models.URLField("URL YouTube", blank=True)

    # --- Informations légales ---
    company_name = models.CharField("Dénomination sociale", max_length=150, default="Jessna TechLearn")
    legal_representative = models.CharField("Représentant légal", max_length=100, default="Chadrack Mbu Jess")
    legal_title = models.CharField("Fonction du représentant", max_length=100, default="Fondateur & Directeur Général")
    registration_number = models.CharField("Numéro d'enregistrement", max_length=100, blank=True, default="En cours")
    tax_number = models.CharField("Numéro fiscal", max_length=100, blank=True, default="En cours")
    governing_law = models.CharField("Droit applicable", max_length=100, default="République Démocratique du Congo")

    # --- Hébergeur ---
    host_name = models.CharField("Nom de l'hébergeur", max_length=100, default="PythonAnywhere")
    host_address = models.CharField("Adresse de l'hébergeur", max_length=255, default="525 Brannan Street, Suite 300, San Francisco, CA 94107, USA")
    host_website = models.URLField("Site web de l'hébergeur", default="https://pythonanywhere.com")

    # --- Versions des documents ---
    terms_version = models.CharField("Version des CGU", max_length=20, default="1.0.2")
    terms_date = models.DateField("Date des CGU", default=timezone.now)
    privacy_policy_version = models.CharField("Version de la politique de confidentialité", max_length=20, default="1.0.2")
    privacy_policy_date = models.DateField("Date de la politique de confidentialité", default=timezone.now)
    
    # --- Protection des données ---
    data_controller = models.CharField("Contrôleur des données", max_length=100, default="Chadrack Mbu Jess")
    data_protection_email = models.EmailField("Email protection des données", default="jessnatechlearn@gmail.com")

    # --- Maintenance ---
    maintenance_mode = models.BooleanField("Mode maintenance", default=False)
    
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