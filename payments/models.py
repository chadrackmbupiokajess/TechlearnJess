from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class PaymentMethod(models.Model):
    """Méthodes de paiement disponibles"""
    PAYMENT_TYPES = [
        ('orange_money', 'Orange Money'),
        ('airtel_money', 'Airtel Money'),
        ('mpesa', 'M-Pesa'),
        ('bank_transfer', 'Virement bancaire'),
        ('cash', 'Espèces'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nom")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, verbose_name="Type")
    description = models.TextField(blank=True, verbose_name="Description")
    logo = models.ImageField(upload_to='payment_methods/', blank=True, verbose_name="Logo")
    
    # Configuration API
    api_key = models.CharField(max_length=200, blank=True, verbose_name="Clé API")
    api_secret = models.CharField(max_length=200, blank=True, verbose_name="Secret API")
    merchant_id = models.CharField(max_length=100, blank=True, verbose_name="ID Marchand")
    
    # Paramètres
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant minimum")
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, default=10000, verbose_name="Montant maximum")
    fees_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Frais (%)")
    fees_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Frais fixes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Méthode de paiement"
        verbose_name_plural = "Méthodes de paiement"

    def __str__(self):
        return self.name

    def calculate_fees(self, amount):
        """Calculer les frais pour un montant donné"""
        percentage_fee = amount * (self.fees_percentage / 100)
        total_fees = percentage_fee + self.fees_fixed
        return total_fees

    def calculate_total(self, amount):
        """Calculer le montant total avec frais"""
        return amount + self.calculate_fees(amount)


class Payment(models.Model):
    """Paiement effectué"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
        ('refunded', 'Remboursé'),
    ]
    
    # Identifiants
    payment_id = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="ID Paiement")
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name="ID Transaction")
    
    # Relations
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, verbose_name="Cours")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, verbose_name="Méthode de paiement")
    
    # Montants
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Frais")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant total")
    currency = models.CharField(max_length=3, default='USD', verbose_name="Devise")
    
    # Statut et dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Terminé le")
    
    # Informations supplémentaires
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Numéro de téléphone")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Données de réponse API
    api_response = models.JSONField(default=dict, blank=True, verbose_name="Réponse API")

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-created_at']

    def __str__(self):
        return f"Paiement {self.payment_id} - {self.user.username} - {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        if not self.fees:
            self.fees = self.payment_method.calculate_fees(self.amount)
        if not self.total_amount:
            self.total_amount = self.amount + self.fees
        super().save(*args, **kwargs)

    def mark_as_completed(self):
        """Marquer le paiement comme terminé"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        
        # Inscrire automatiquement l'utilisateur au cours
        from courses.models import Enrollment
        enrollment, created = Enrollment.objects.get_or_create(
            user=self.user,
            course=self.course
        )
        
        # Créer une notification
        from notifications.models import Notification
        Notification.create_notification(
            user=self.user,
            title="Paiement confirmé",
            message=f"Votre paiement pour le cours '{self.course.title}' a été confirmé. Vous pouvez maintenant accéder au cours.",
            notification_type='payment',
            action_url=self.course.get_absolute_url(),
            action_text="Accéder au cours"
        )

    def mark_as_failed(self, reason=""):
        """Marquer le paiement comme échoué"""
        self.status = 'failed'
        if reason:
            self.notes = reason
        self.save()
        
        # Créer une notification
        from notifications.models import Notification
        Notification.create_notification(
            user=self.user,
            title="Paiement échoué",
            message=f"Votre paiement pour le cours '{self.course.title}' a échoué. Veuillez réessayer.",
            notification_type='payment',
            action_url=f"/paiements/{self.payment_id}/",
            action_text="Voir les détails"
        )


class Invoice(models.Model):
    """Facture"""
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de facture")
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, verbose_name="Paiement")
    
    # Informations de facturation
    billing_name = models.CharField(max_length=200, verbose_name="Nom de facturation")
    billing_email = models.EmailField(verbose_name="Email de facturation")
    billing_address = models.TextField(blank=True, verbose_name="Adresse de facturation")
    billing_city = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    billing_country = models.CharField(max_length=100, default="République Démocratique du Congo", verbose_name="Pays")
    
    # Dates
    issue_date = models.DateTimeField(auto_now_add=True, verbose_name="Date d'émission")
    due_date = models.DateTimeField(verbose_name="Date d'échéance")
    
    # Fichier PDF
    pdf_file = models.FileField(upload_to='invoices/', blank=True, verbose_name="Fichier PDF")

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-issue_date']

    def __str__(self):
        return f"Facture {self.invoice_number}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Générer un numéro de facture unique
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            count = Invoice.objects.filter(invoice_number__startswith=f'TLJ-{date_str}').count() + 1
            self.invoice_number = f'TLJ-{date_str}-{count:04d}'
        
        if not self.billing_name:
            self.billing_name = self.payment.user.get_full_name() or self.payment.user.username
        if not self.billing_email:
            self.billing_email = self.payment.user.email
        
        super().save(*args, **kwargs)


class Refund(models.Model):
    """Remboursement"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('rejected', 'Rejeté'),
    ]
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, verbose_name="Paiement")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant à rembourser")
    reason = models.TextField(verbose_name="Raison du remboursement")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    
    # Dates
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name="Demandé le")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Traité le")
    
    # Informations de traitement
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_refunds', verbose_name="Traité par")
    admin_notes = models.TextField(blank=True, verbose_name="Notes administrateur")

    class Meta:
        verbose_name = "Remboursement"
        verbose_name_plural = "Remboursements"
        ordering = ['-requested_at']

    def __str__(self):
        return f"Remboursement {self.amount} pour {self.payment.payment_id}"