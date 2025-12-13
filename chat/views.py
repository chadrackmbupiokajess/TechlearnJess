from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone as django_timezone # Renommé pour éviter les conflits
from datetime import datetime, timezone # Importation de datetime et timezone de la bibliothèque standard
import logging
# from django.views.decorators.csrf import csrf_exempt # Plus nécessaire avec un formulaire HTML standard
from .models import ChatRoom, Message
from .forms import ChatRoomForm

logger = logging.getLogger(__name__) # Initialisation du logger

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
    messages_chat = salon.messages.all().order_by('timestamp') # Assurez-vous que les messages sont triés
    
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
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans le champ '{field}': {error}")
            return redirect('chat:liste_salons')
    return redirect('chat:liste_salons')


@login_required
@require_http_methods(["POST"])
def envoyer_message(request, salon_id):
    """Envoie un message dans un salon de chat spécifique via AJAX"""
    salon = get_object_or_404(ChatRoom, id=salon_id)
    
    # Vérifier si l'utilisateur est bien participant du salon
    if not salon.participants.filter(id=request.user.id).exists():
        return JsonResponse({'error': 'Vous n\'êtes pas membre de ce salon.'}, status=403)

    contenu = request.POST.get('contenu')
    if contenu:
        message = Message.objects.create(
            salon=salon,
            auteur=request.user,
            contenu=contenu
        )
        # Retourner les données du message créé pour l'affichage côté client
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'auteur_username': message.auteur.username,
                'auteur_avatar_url': message.auteur.userprofile.get_avatar_url() if hasattr(message.auteur, 'userprofile') else '', # Assurez-vous que UserProfile existe
                'contenu': message.contenu,
                'timestamp': message.timestamp.astimezone(timezone.utc).isoformat(timespec='microseconds'), # MODIFIÉ ICI
                'is_own': True # Indique que c'est le message de l'utilisateur actuel
            }
        })
    return JsonResponse({'error': 'Contenu du message vide.'}, status=400)


@login_required
@require_http_methods(["GET"])
def messages_api(request, salon_id):
    """API pour récupérer les messages d'un salon, éventuellement filtrés par timestamp"""
    salon = get_object_or_404(ChatRoom, id=salon_id, participants=request.user)
    
    # Récupérer le timestamp 'since' si fourni
    since_timestamp_str = request.GET.get('since')
    
    messages_query = salon.messages.all()

    if since_timestamp_str:
        try:
            # fromisoformat est sensible au format, notamment l'espace avant le décalage horaire
            # Nous allons tenter de remplacer l'espace par un '+' si le format est celui qui pose problème
            if ' ' in since_timestamp_str and since_timestamp_str.endswith('00:00'):
                since_timestamp_str = since_timestamp_str.replace(' ', '+', 1)
            
            since_datetime = datetime.fromisoformat(since_timestamp_str)
            
            messages_query = messages_query.filter(timestamp__gt=since_datetime)
        except ValueError as e:
            logger.error(f"Invalid 'since' timestamp format: '{since_timestamp_str}' - Error: {e}")
            return JsonResponse({'error': f'Format de timestamp "since" invalide: {e}'}, status=400)
            
    messages_query = messages_query.order_by('timestamp')
    
    messages_data = []
    for message in messages_query:
        messages_data.append({
            'id': message.id,
            'auteur_username': message.auteur.username,
            'auteur_avatar_url': message.auteur.userprofile.get_avatar_url() if hasattr(message.auteur, 'userprofile') else '',
            'contenu': message.contenu,
            'timestamp': message.timestamp.astimezone(timezone.utc).isoformat(timespec='microseconds'), # MODIFIÉ ICI
            'is_own': (message.auteur == request.user) # Indique si le message vient de l'utilisateur actuel
        })
    
    return JsonResponse({'messages': messages_data})