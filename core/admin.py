from django.contrib import admin
from .models import SiteSettings, Testimonial, FAQ, GalleryImage


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'maintenance_mode', 'updated_at']
    fieldsets = (
        ('Informations Générales', {
            'fields': ('site_name', 'site_slogan', 'site_description', 'logo', 'favicon', 'founder_photo')
        }),
        ('Informations de Contact', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('Réseaux Sociaux', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'youtube_url')
        }),
        ('Contenu des Pages Légales', {
            'classes': ('collapse',),
            'fields': ('terms_of_service_content', 'privacy_policy_content', 'legal_notice_content')
        }),
        ('Informations Légales', {
            'classes': ('collapse',),
            'fields': (
                'company_name', 'legal_representative', 'legal_title', 
                'registration_number', 'tax_number', 'governing_law'
            )
        }),
        ('Informations sur l\'Hébergeur', {
            'classes': ('collapse',),
            'fields': ('host_name', 'host_address', 'host_website')
        }),
        ('Versions des Documents', {
            'classes': ('collapse',),
            'fields': ('terms_version', 'terms_date', 'privacy_policy_version', 'privacy_policy_date')
        }),
        ('Protection des Données', {
            'classes': ('collapse',),
            'fields': ('data_controller', 'data_protection_email')
        }),
        ('Mode Maintenance', {
            'fields': ('maintenance_mode',)
        }),
    )

    class Media:
        css = {
            'all': ('css/admin_fixes.css',)
        }

    def has_add_permission(self, request):
        # Empêcher la création de plusieurs instances
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression
        return False


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')
    search_fields = ('title', 'description')


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'company', 'rating', 'is_featured', 'is_active', 'created_at']
    list_filter = ['rating', 'is_featured', 'is_active', 'created_at']
    search_fields = ['name', 'position', 'company', 'content']
    list_editable = ['is_featured', 'is_active']
    ordering = ['-created_at']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question', 'answer']
    list_editable = ['category', 'order', 'is_active']
    ordering = ['category', 'order']