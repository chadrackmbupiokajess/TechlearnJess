from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from django.conf import settings
import os


class Certificate(models.Model):
    """Certificat de cours"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, verbose_name="Cours")
    certificate_id = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="ID Certificat")
    
    # Informations du certificat
    student_name = models.CharField(max_length=200, verbose_name="Nom de l'étudiant")
    course_title = models.CharField(max_length=200, verbose_name="Titre du cours")
    instructor_name = models.CharField(max_length=200, verbose_name="Nom du formateur")
    completion_date = models.DateField(verbose_name="Date de fin")
    issue_date = models.DateTimeField(auto_now_add=True, verbose_name="Date d'émission")
    
    # Fichiers
    pdf_file = models.FileField(upload_to='certificates/pdf/', blank=True, verbose_name="Fichier PDF")
    qr_code = models.ImageField(upload_to='certificates/qr/', blank=True, verbose_name="QR Code")
    
    # Métadonnées
    is_valid = models.BooleanField(default=True, verbose_name="Valide")
    verification_url = models.URLField(blank=True, verbose_name="URL de vérification")
    
    class Meta:
        verbose_name = "Certificat"
        verbose_name_plural = "Certificats"
        unique_together = ['user', 'course']
        ordering = ['-issue_date']

    def __str__(self):
        return f"Certificat de {self.student_name} pour {self.course_title}"

    def save(self, *args, **kwargs):
        if not self.student_name:
            self.student_name = self.user.get_full_name() or self.user.username
        if not self.course_title:
            self.course_title = self.course.title
        if not self.instructor_name:
            self.instructor_name = self.course.instructor.get_full_name() or self.course.instructor.username
        
        super().save(*args, **kwargs)
        
        # Générer le QR code et le PDF après la sauvegarde
        if not self.qr_code:
            self.generate_qr_code()
        if not self.pdf_file:
            self.generate_pdf()

    def get_absolute_url(self):
        return reverse('certificates:detail', kwargs={'certificate_id': self.certificate_id})

    def get_verification_url(self):
        """URL de vérification du certificat"""
        if not self.verification_url:
            from django.contrib.sites.models import Site
            current_site = Site.objects.get_current()
            self.verification_url = f"https://{current_site.domain}{self.get_absolute_url()}"
            self.save(update_fields=['verification_url'])
        return self.verification_url

    def generate_qr_code(self):
        """Générer le QR code pour la vérification"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.get_verification_url())
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Sauvegarder l'image
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        filename = f'qr_code_{self.certificate_id}.png'
        self.qr_code.save(filename, File(buffer), save=False)
        buffer.close()

    def generate_pdf(self):
        """Générer le certificat PDF"""
        buffer = BytesIO()
        
        # Créer le PDF en mode paysage
        p = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        # Couleurs
        primary_color = (59, 130, 246)  # Bleu primary
        secondary_color = (100, 116, 139)  # Gris secondary
        
        # Bordure décorative
        p.setStrokeColorRGB(*[c/255 for c in primary_color])
        p.setLineWidth(3)
        p.rect(30, 30, width-60, height-60)
        
        # Bordure intérieure
        p.setLineWidth(1)
        p.rect(50, 50, width-100, height-100)
        
        # Titre principal
        p.setFillColorRGB(*[c/255 for c in primary_color])
        p.setFont("Helvetica-Bold", 36)
        title_text = "CERTIFICAT DE RÉUSSITE"
        title_width = p.stringWidth(title_text, "Helvetica-Bold", 36)
        p.drawString((width - title_width) / 2, height - 120, title_text)
        
        # Logo TechLearnJess
        p.setFillColorRGB(*[c/255 for c in secondary_color])
        p.setFont("Helvetica-Bold", 24)
        logo_text = "TechLearnJess"
        logo_width = p.stringWidth(logo_text, "Helvetica-Bold", 24)
        p.drawString((width - logo_width) / 2, height - 160, logo_text)
        
        # Slogan
        p.setFont("Helvetica-Oblique", 12)
        slogan_text = "Apprendre ici, réussir partout."
        slogan_width = p.stringWidth(slogan_text, "Helvetica-Oblique", 12)
        p.drawString((width - slogan_width) / 2, height - 180, slogan_text)
        
        # Texte principal
        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica", 18)
        cert_text = "Ceci certifie que"
        cert_width = p.stringWidth(cert_text, "Helvetica", 18)
        p.drawString((width - cert_width) / 2, height - 230, cert_text)
        
        # Nom de l'étudiant
        p.setFillColorRGB(*[c/255 for c in primary_color])
        p.setFont("Helvetica-Bold", 28)
        name_width = p.stringWidth(self.student_name, "Helvetica-Bold", 28)
        p.drawString((width - name_width) / 2, height - 270, self.student_name)
        
        # Texte du cours
        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica", 18)
        course_text = "a terminé avec succès le cours"
        course_width = p.stringWidth(course_text, "Helvetica", 18)
        p.drawString((width - course_width) / 2, height - 320, course_text)
        
        # Titre du cours
        p.setFillColorRGB(*[c/255 for c in primary_color])
        p.setFont("Helvetica-Bold", 22)
        title_width = p.stringWidth(self.course_title, "Helvetica-Bold", 22)
        p.drawString((width - title_width) / 2, height - 360, self.course_title)
        
        # Date de fin
        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica", 14)
        date_text = f"Terminé le {self.completion_date.strftime('%d/%m/%Y')}"
        date_width = p.stringWidth(date_text, "Helvetica", 14)
        p.drawString((width - date_width) / 2, height - 400, date_text)
        
        # Signature et informations
        p.setFont("Helvetica", 12)
        
        # Formateur
        instructor_text = f"Formateur: {self.instructor_name}"
        p.drawString(100, 150, instructor_text)
        
        # Date d'émission
        issue_text = f"Émis le: {self.issue_date.strftime('%d/%m/%Y')}"
        p.drawString(100, 130, issue_text)
        
        # ID du certificat
        id_text = f"ID: {str(self.certificate_id)[:8]}"
        p.drawString(100, 110, id_text)
        
        # QR Code (si disponible)
        if self.qr_code:
            try:
                p.drawImage(self.qr_code.path, width - 150, 80, 80, 80)
            except:
                pass
        
        # URL de vérification
        p.setFont("Helvetica", 10)
        verify_text = f"Vérifiez ce certificat sur: {self.get_verification_url()}"
        p.drawString(100, 80, verify_text)
        
        p.showPage()
        p.save()
        
        # Sauvegarder le PDF
        filename = f'certificate_{self.certificate_id}.pdf'
        self.pdf_file.save(filename, File(buffer), save=False)
        buffer.close()


class CertificateTemplate(models.Model):
    """Modèle de certificat personnalisable"""
    name = models.CharField(max_length=100, verbose_name="Nom du modèle")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Design
    background_color = models.CharField(max_length=7, default="#FFFFFF", verbose_name="Couleur de fond")
    primary_color = models.CharField(max_length=7, default="#3B82F6", verbose_name="Couleur principale")
    secondary_color = models.CharField(max_length=7, default="#64748B", verbose_name="Couleur secondaire")
    
    # Textes personnalisables
    title_text = models.CharField(max_length=200, default="CERTIFICAT DE RÉUSSITE", verbose_name="Titre")
    subtitle_text = models.CharField(max_length=200, default="TechLearnJess", verbose_name="Sous-titre")
    completion_text = models.CharField(max_length=200, default="a terminé avec succès le cours", verbose_name="Texte de réussite")
    
    # Métadonnées
    is_default = models.BooleanField(default=False, verbose_name="Modèle par défaut")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Modèle de certificat"
        verbose_name_plural = "Modèles de certificats"

    def __str__(self):
        return self.name