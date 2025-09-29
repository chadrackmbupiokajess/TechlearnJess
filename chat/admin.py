from django.contrib import admin
from .models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['nom', 'est_prive', 'cree_le', 'nombre_participants']
    list_filter = ['est_prive', 'cree_le']
    search_fields = ['nom', 'description']
    filter_horizontal = ['participants']
    
    def nombre_participants(self, obj):
        return obj.participants.count()
    nombre_participants.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['auteur', 'salon', 'contenu_court', 'timestamp', 'est_lu']
    list_filter = ['salon', 'timestamp', 'est_lu']
    search_fields = ['auteur__username', 'contenu']
    readonly_fields = ['timestamp']
    
    def contenu_court(self, obj):
        return obj.contenu[:50] + "..." if len(obj.contenu) > 50 else obj.contenu
    contenu_court.short_description = 'Contenu'