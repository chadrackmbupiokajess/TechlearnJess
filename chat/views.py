from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import ChatRoom, Message
from .forms import ChatRoomForm # Nous allons créer ce formulaire


@login_required
def liste_salons(request):
    """Affiche la liste des salons de chat"""
    salons = ChatRoom.objects.filter(participants=request.user)
    context = {
        'salons': salons,
    }
    return render(request, 'chat/liste_salons.html', context)


@login_required
def salon_chat(request, salon_id):
    """Affiche un salon de chat spécifique"""
    salon = get_object_or_404(ChatRoom, id=salon_id, participants=request.user)
    messages_chat = salon.messages.all()
    
    context = {
        'salon': salon,
        'messages': messages_chat,
        'salon_id_json': salon_id,
    }
    
    return render(request, 'chat/salon_chat.html', context)


@login_required
@require_http_methods(["POST"])
def creer_salon(request):
    """Crée un nouveau salon de chat"""
    if request.method == 'POST':
        form = ChatRoomForm(request.POST)
        if form.is_valid():
            salon = form.save(commit=False)
            salon.save()
            salon.participants.add(request.user)
            messages.success(request, f"Le salon '{salon.nom}' a été créé avec succès !")
            return redirect('chat:liste_salons')
        else:
            # Si le formulaire n'est pas valide, nous devrons gérer les erreurs.
            # Pour un modal, on pourrait renvoyer un JsonResponse avec les erreurs.
            # Pour l'instant, nous allons simplement rediriger et afficher les messages d'erreur.
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans le champ '{field}': {error}")
            return redirect('chat:liste_salons') # Ou rendre la page avec le modal ouvert et les erreurs
    return redirect('chat:liste_salons') # Rediriger si la méthode n'est pas POST


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