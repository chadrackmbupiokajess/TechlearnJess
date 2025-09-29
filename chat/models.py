from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatRoom(models.Model):
    """Salon de chat"""
    nom = models.CharField(max_length=100, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    participants = models.ManyToManyField(User, related_name='chat_rooms', verbose_name="Participants")
    est_prive = models.BooleanField(default=False, verbose_name="Privé")
    cree_le = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    class Meta:
        verbose_name = "Salon de Chat"
        verbose_name_plural = "Salons de Chat"
        ordering = ['-cree_le']
    
    def __str__(self):
        return self.nom


class Message(models.Model):
    """Message de chat"""
    salon = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', verbose_name="Salon")
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Auteur")
    contenu = models.TextField(verbose_name="Contenu")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Envoyé le")
    est_lu = models.BooleanField(default=False, verbose_name="Lu")
    
    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.auteur.username}: {self.contenu[:50]}..."