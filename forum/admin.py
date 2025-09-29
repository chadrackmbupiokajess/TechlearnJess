from django.contrib import admin
from .models import ForumCategory, ForumTopic, ForumPost


@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug', 'ordre', 'est_actif', 'nombre_sujets', 'cree_le']
    list_filter = ['est_actif', 'cree_le']
    search_fields = ['nom', 'description']
    list_editable = ['ordre', 'est_actif']
    prepopulated_fields = {'slug': ('nom',)}
    ordering = ['ordre', 'nom']


@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ['titre', 'categorie', 'auteur', 'est_epingle', 'est_ferme', 'est_resolu', 'vues', 'cree_le']
    list_filter = ['categorie', 'est_epingle', 'est_ferme', 'est_resolu', 'cree_le']
    search_fields = ['titre', 'contenu', 'auteur__username']
    list_editable = ['est_epingle', 'est_ferme', 'est_resolu']
    prepopulated_fields = {'slug': ('titre',)}
    readonly_fields = ['vues', 'cree_le', 'modifie_le', 'derniere_activite']
    
    fieldsets = (
        ('Contenu', {
            'fields': ('titre', 'slug', 'categorie', 'auteur', 'contenu')
        }),
        ('Statut', {
            'fields': ('est_epingle', 'est_ferme', 'est_resolu')
        }),
        ('Statistiques', {
            'fields': ('vues', 'cree_le', 'modifie_le', 'derniere_activite'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ['sujet', 'auteur', 'contenu_court', 'est_solution', 'nombre_likes', 'cree_le']
    list_filter = ['est_solution', 'cree_le', 'sujet__categorie']
    search_fields = ['contenu', 'auteur__username', 'sujet__titre']
    list_editable = ['est_solution']
    readonly_fields = ['cree_le', 'modifie_le']
    
    def contenu_court(self, obj):
        return obj.contenu[:100] + "..." if len(obj.contenu) > 100 else obj.contenu
    contenu_court.short_description = 'Contenu'