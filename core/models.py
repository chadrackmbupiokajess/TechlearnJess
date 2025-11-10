from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from ckeditor.fields import RichTextField

LEGAL_NOTICE_DEFAULT_CONTENT = """
<div class="info-box">
    <p><strong>Dénomination sociale :</strong> {{ settings.company_name }}</p>
    <p><strong>Adresse du siège social :</strong> {{ settings.address }}</p>
    <p><strong>Téléphone :</strong> {{ settings.contact_phone }}</p>
    <p><strong>Email :</strong> <a href="mailto:{{ settings.contact_email }}">{{ settings.contact_email }}</a></p>
    <p><strong>Site web :</strong> <a href="{{ settings.company_website }}">{{ settings.company_website }}</a></p>
</div>
<h2>2. Représentant légal</h2>
<div class="info-box">
    <p><strong>{{ settings.legal_representative }}</strong></p>
    <p><strong>Fonction :</strong> {{ settings.legal_title }}</p>
    <p>En qualité de représentant légal de {{ settings.company_name }}</p>
</div>
<h2>3. Informations d'enregistrement</h2>
<div class="success-box">
    <p><strong>Numéro d'enregistrement :</strong> {{ settings.registration_number }}</p>
    <p><strong>Numéro fiscal :</strong> {{ settings.tax_number }}</p>
    <p><strong>Juridiction :</strong> {{ settings.governing_law }}</p>
</div>
<h2>4. Activité</h2>
<p>{{ settings.company_name }} est une plateforme d'apprentissage en ligne spécialisée dans la formation technologique. Nous proposons des cours, formations et certifications dans les domaines de l'informatique, du développement web, de la programmation et des nouvelles technologies.</p>
<h2>5. Hébergement</h2>
<div class="purple-box">
    <p><strong>Hébergeur :</strong> {{ settings.host_name }}</p>
    <p><strong>Adresse :</strong> {{ settings.host_address }}</p>
    <p><strong>Site web :</strong> <a href="{{ settings.host_website }}" target="_blank">{{ settings.host_website }}</a></p>
</div>
<h2>6. Propriété intellectuelle</h2>
<p>L'ensemble des éléments composant le site {{ settings.company_name }} (textes, images, vidéos, sons, logos, structure, logiciels, etc.) sont protégés par le droit d'auteur, le droit des marques et/ou le droit des producteurs de bases de données.</p>
<p>Ces éléments sont la propriété exclusive de {{ settings.company_name }} ou de ses partenaires. Toute reproduction, représentation, adaptation, traduction et/ou transformation, partielle ou intégrale, par quelque procédé que ce soit, est strictement interdite sans l'autorisation écrite préalable de {{ settings.company_name }}.</p>
<h2>7. Données personnelles</h2>
<p>Les informations recueillies sur ce site sont nécessaires à la gestion de votre compte et à la fourniture de nos services. Elles font l'objet d'un traitement informatique conforme à notre <a href="/politique-confidentialite/">politique de confidentialité</a>.</p>
<h2>8. Cookies</h2>
<p>Ce site utilise des cookies techniques nécessaires à son bon fonctionnement. Ces cookies permettent notamment de maintenir votre session de connexion et de mémoriser vos préférences d'utilisation.</p>
<h2>9. Droit applicable et juridiction</h2>
<p>Les présentes mentions légales sont régies par le droit de la République Démocratique du Congo. En cas de litige, les tribunaux de Matadi, Kongo-Central seront seuls compétents.</p>
<h2>10. Signalement de contenu</h2>
<p>Si vous constatez la présence sur notre site d'un contenu illicite ou portant atteinte à vos droits, vous pouvez nous le signaler à l'adresse : <a href="mailto:{{ settings.contact_email }}">{{ settings.contact_email }}</a></p>
<h2>11. Contact</h2>
<div class="warning-box">
    <p>Pour toute question concernant ces mentions légales :</p>
    <p><strong>{{ settings.company_name }}</strong></p>
    <p>{{ settings.address }}</p>
    <p>Email : <a href="mailto:{{ settings.contact_email }}">{{ settings.contact_email }}</a></p>
    <p>Téléphone : {{ settings.contact_phone }}</p>
</div>
"""

TERMS_OF_SERVICE_DEFAULT_CONTENT = """
<h2>1. Objet</h2>
<p>Les présentes conditions générales d'utilisation (CGU) régissent l'utilisation de la plateforme d'apprentissage en ligne {{ settings.company_name }}, accessible à l'adresse <a href="{{ settings.company_website }}">{{ settings.company_website }}</a>.</p>
<h2>2. Éditeur</h2>
<div class="info-box">
    <p><strong>{{ settings.company_name }}</strong></p>
    <p>{{ settings.address }}</p>
    <p>Email : <a href="mailto:{{ settings.contact_email }}">{{ settings.contact_email }}</a></p>
    <p>Téléphone : {{ settings.contact_phone }}</p>
</div>
<h2>3. Acceptation des conditions</h2>
<p>L'utilisation de la plateforme {{ settings.company_name }} implique l'acceptation pleine et entière des présentes conditions d'utilisation. Si vous n'acceptez pas ces conditions, vous ne devez pas utiliser nos services.</p>
"""

PRIVACY_POLICY_DEFAULT_CONTENT = """
<h2>1. Responsable du traitement</h2>
<p>Le responsable du traitement des données personnelles est :</p>
<div class="info-box">
    <p><strong>{{ settings.company_name }}</strong></p>
    <p>{{ settings.address }}</p>
    <p>Email : <a href="mailto:{{ settings.contact_email }}">{{ settings.contact_email }}</a></p>
    <p>Téléphone : {{ settings.contact_phone }}</p>
</div>
<h2>2. Données collectées</h2>
<p>Nous collectons les données suivantes :</p>
<ul>
    <li><strong>Données d'identification :</strong> nom, prénom, adresse email</li>
    <li><strong>Données de connexion :</strong> mot de passe chiffré, date de dernière connexion</li>
</ul>
"""

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

    # --- Contenu des pages légales ---
    terms_of_service_content = RichTextField("Contenu des CGU", blank=True, default=TERMS_OF_SERVICE_DEFAULT_CONTENT, help_text="Le texte complet des Conditions Générales d'Utilisation.")
    privacy_policy_content = RichTextField("Contenu de la Politique de Confidentialité", blank=True, default=PRIVACY_POLICY_DEFAULT_CONTENT, help_text="Le texte complet de la Politique de Confidentialité.")
    legal_notice_content = RichTextField("Contenu des Mentions Légales", blank=True, default=LEGAL_NOTICE_DEFAULT_CONTENT, help_text="Le texte complet des Mentions Légales.")

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