from django.contrib import admin
from .models import SiteSettings, Testimonial, FAQ


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'site_slogan', 'maintenance_mode', 'updated_at']
    fieldsets = (
        ('Informations générales', {
            'fields': ('site_name', 'site_slogan', 'site_description', 'logo', 'favicon')
        }),
        ('Contact', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('Réseaux sociaux', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'youtube_url')
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode',)
        }),
    )

    def has_add_permission(self, request):
        # Empêcher la création de plusieurs instances
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression
        return False


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