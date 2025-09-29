from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class ForumCategory(models.Model):
    """Catégorie de forum"""
    nom = models.CharField(max_length=100, verbose_name="Nom")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Description")
    couleur = models.CharField(max_length=7, default="#3B82F6", verbose_name="Couleur")
    icone = models.CharField(max_length=50, blank=True, verbose_name="Icône")
    ordre = models.IntegerField(default=0, verbose_name="Ordre")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie de Forum"
        verbose_name_plural = "Catégories de Forum"
        ordering = ['ordre', 'nom']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    @property
    def nombre_sujets(self):
        return self.sujets.count()

    @property
    def nombre_messages(self):
        return sum(sujet.nombre_reponses + 1 for sujet in self.sujets.all())


class ForumTopic(models.Model):
    """Sujet de forum"""
    titre = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(verbose_name="Slug")
    categorie = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='sujets', verbose_name="Catégorie")
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Auteur")
    contenu = models.TextField(verbose_name="Contenu")
    
    # Métadonnées
    est_epingle = models.BooleanField(default=False, verbose_name="Épinglé")
    est_ferme = models.BooleanField(default=False, verbose_name="Fermé")
    est_resolu = models.BooleanField(default=False, verbose_name="Résolu")
    vues = models.PositiveIntegerField(default=0, verbose_name="Vues")
    
    # Dates
    cree_le = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    modifie_le = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    derniere_activite = models.DateTimeField(auto_now_add=True, verbose_name="Dernière activité")

    class Meta:
        verbose_name = "Sujet de Forum"
        verbose_name_plural = "Sujets de Forum"
        ordering = ['-est_epingle', '-derniere_activite']
        unique_together = ['categorie', 'slug']

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('forum:topic_detail', kwargs={'category_slug': self.categorie.slug, 'slug': self.slug})

    @property
    def nombre_reponses(self):
        return self.reponses.count()

    @property
    def derniere_reponse(self):
        return self.reponses.order_by('-cree_le').first()

    def incrementer_vues(self):
        self.vues += 1
        self.save(update_fields=['vues'])


class ForumPost(models.Model):
    """Réponse de forum"""
    sujet = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='reponses', verbose_name="Sujet")
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Auteur")
    contenu = models.TextField(verbose_name="Contenu")
    
    # Métadonnées
    est_solution = models.BooleanField(default=False, verbose_name="Solution")
    likes = models.ManyToManyField(User, related_name='posts_likes', blank=True, verbose_name="J'aime")
    
    # Dates
    cree_le = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    modifie_le = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Réponse de Forum"
        verbose_name_plural = "Réponses de Forum"
        ordering = ['cree_le']

    def __str__(self):
        return f"Réponse de {self.auteur.username} sur {self.sujet.titre}"

    @property
    def nombre_likes(self):
        return self.likes.count()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Mettre à jour la dernière activité du sujet
        self.sujet.derniere_activite = self.cree_le
        self.sujet.save(update_fields=['derniere_activite'])