from django.contrib import admin
from .models import Certificate, CertificateTemplate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'course_title', 'instructor_name', 'completion_date', 'issue_date', 'is_valid']
    list_filter = ['is_valid', 'issue_date', 'completion_date', 'course']
    search_fields = ['student_name', 'course_title', 'instructor_name', 'certificate_id']
    readonly_fields = ['certificate_id', 'issue_date', 'verification_url']
    list_editable = ['is_valid']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'course', 'certificate_id')
        }),
        ('Détails du certificat', {
            'fields': ('student_name', 'course_title', 'instructor_name', 'completion_date')
        }),
        ('Fichiers', {
            'fields': ('pdf_file', 'qr_code')
        }),
        ('Validation', {
            'fields': ('is_valid', 'verification_url', 'issue_date')
        }),
    )
    
    actions = ['regenerate_certificates', 'invalidate_certificates', 'validate_certificates']
    
    def regenerate_certificates(self, request, queryset):
        for certificate in queryset:
            certificate.pdf_file.delete()
            certificate.qr_code.delete()
            certificate.generate_qr_code()
            certificate.generate_pdf()
            certificate.save()
        self.message_user(request, f"{queryset.count()} certificats régénérés.")
    regenerate_certificates.short_description = "Régénérer les certificats sélectionnés"
    
    def invalidate_certificates(self, request, queryset):
        queryset.update(is_valid=False)
        self.message_user(request, f"{queryset.count()} certificats invalidés.")
    invalidate_certificates.short_description = "Invalider les certificats sélectionnés"
    
    def validate_certificates(self, request, queryset):
        queryset.update(is_valid=True)
        self.message_user(request, f"{queryset.count()} certificats validés.")
    validate_certificates.short_description = "Valider les certificats sélectionnés"


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'is_active', 'created_at']
    list_filter = ['is_default', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_default', 'is_active']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'description', 'is_default', 'is_active')
        }),
        ('Couleurs', {
            'fields': ('background_color', 'primary_color', 'secondary_color')
        }),
        ('Textes', {
            'fields': ('title_text', 'subtitle_text', 'completion_text')
        }),
    )