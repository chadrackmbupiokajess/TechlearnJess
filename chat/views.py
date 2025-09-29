from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import ChatRoom, Message


@login_required
def liste_salons(request):
    """Affiche la liste des salons de chat"""
    salons = ChatRoom.objects.filter(participants=request.user)
    return render(request, 'chat/liste_salons.html', {'salons': salons})


@login_required
def salon_chat(request, salon_id):
    """Affiche un salon de chat spécifique"""
    salon = get_object_or_404(ChatRoom, id=salon_id, participants=request.user)
    messages_chat = salon.messages.all()
    
    context = {
        'salon': salon,
        'messages': messages_chat,
        'salon_id_json': salon_id
    }
    
    return render(request, 'chat/salon_chat.html', context)


@login_required
@require_http_methods(["GET"])
def messages_api(request, salon_id):
    """API pour récupérer les messages d'un salon"""
    salon = get_object_or_404(ChatRoom, id=salon_id, participants=request.user)
    messages_data = []
    
    for message in salon.messages.all():
        messages_data.append({
            'id': message.id,
            'auteur': message.auteur.username,
            'contenu': message.contenu,
            'timestamp': message.timestamp.isoformat(),
        })
    
    return JsonResponse({'messages': messages_data})