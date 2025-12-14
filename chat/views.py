from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone as django_timezone # Renommé pour éviter les conflits
from datetime import datetime, timedelta, timezone # Importation de datetime, timedelta et timezone de la bibliothèque standard
import logging
from django.db.models import Q # Importation de Q pour les requêtes complexes
from django.contrib.auth.models import User # Importation du modèle User
# from django.views.decorators.csrf import csrf_exempt # Plus nécessaire avec un formulaire HTML standard
from .models import ChatRoom, Message
from accounts.models import UserProfile # Importation du UserProfile
from .forms import ChatRoomForm, InviteMembersForm # Importation du nouveau formulaire

logger = logging.getLogger(__name__) # Initialisation du logger

@login_required
def liste_salons(request):
    """Affiche la liste des salons de chat"""
    # Récupérer les salons où l'utilisateur est participant OU les salons publics
    salons = ChatRoom.objects.filter(
        Q(participants=request.user) | Q(est_prive=False)
    ).distinct().order_by('-cree_le') # Assurez-vous d'ordonner les résultats
    
    # --- Calcul des statistiques dynamiques ---
    
    # Fenêtre de 90 secondes pour considérer un utilisateur comme "en ligne"
    ninety_seconds_ago = django_timezone.now() - timedelta(seconds=2)
    
    # Récupérer les profils des utilisateurs en ligne (en excluant l'utilisateur actuel)
    online_users_profiles = UserProfile.objects.filter(
        last_activity__gte=ninety_seconds_ago
    ).exclude(user=request.user).select_related('user')
    
    online_users_count = online_users_profiles.count()
    
    # Messages (total des messages dans tous les salons accessibles)
    total_messages_count = Message.objects.filter(
        salon__in=salons # Compte les messages des salons que l'utilisateur peut voir
    ).count()
    
    # Nouveaux Salons (créés au cours des dernières 24 heures)
    twenty_four_hours_ago = django_timezone.now() - timedelta(hours=24)
    new_salons_count = ChatRoom.objects.filter(
        cree_le__gte=twenty_four_hours_ago
    ).count()
    
    context = {
        'salons': salons,
        'online_users_count': online_users_count,
        'online_users_profiles': online_users_profiles, # Ajout pour le débogage
        'total_messages_count': total_messages_count,
        'new_salons_count': new_salons_count,
    }
    return render(request, 'chat/liste_salons.html', context)


@login_required
def salon_chat(request, salon_id):
    """Affiche un salon de chat spécifique"""
    salon = get_object_or_404(ChatRoom, id=salon_id) # Ne filtre plus par participant ici
    
    # Vérifier si l'utilisateur est déjà membre du salon
    if not salon.participants.filter(id=request.user.id).exists():
        # Si l'utilisateur n'est pas membre, l'ajouter
        salon.participants.add(request.user)
        messages.info(request, f"Vous avez rejoint le salon '{salon.nom}'.")
        # Optionnel: Rediriger pour rafraîchir le contexte, ou continuer
        # return redirect('chat:salon_chat', salon_id=salon_id)

    messages_chat = salon.messages.all().order_by('timestamp') # Assurez-vous que les messages sont triés
    
    # Instancier le formulaire d'invitation pour le contexte
    invite_form = InviteMembersForm(chatroom=salon)

    context = {
        'salon': salon,
        'messages': messages_chat,
        'salon_id_json': salon_id,
        'invite_form': invite_form, # Ajouter le formulaire au contexte
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
@require_http_methods(["POST"])
def invite_members(request, salon_id):
    """Vue pour inviter des membres à un salon de chat."""
    salon = get_object_or_404(ChatRoom, id=salon_id)

    # Vérifier si l'utilisateur actuel a la permission d'inviter
    # Pour l'instant, tout membre peut inviter. Pour une logique plus stricte,
    # on pourrait vérifier si request.user est le créateur du salon, ou un admin.
    if not salon.participants.filter(id=request.user.id).exists():
        messages.error(request, "Vous n'êtes pas autorisé à inviter des membres dans ce salon.")
        return redirect('chat:salon_chat', salon_id=salon_id)

    form = InviteMembersForm(request.POST, chatroom=salon)
    if form.is_valid():
        users_to_invite = form.cleaned_data['users_to_invite']
        for user_to_add in users_to_invite:
            salon.participants.add(user_to_add)
        messages.success(request, f"{len(users_to_invite)} membre(s) invité(s) avec succès !")
    else:
        # Si le formulaire n'est pas valide, afficher les erreurs
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"Erreur dans le champ '{field}': {error}")

    return redirect('chat:salon_chat', salon_id=salon_id)


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
            # Utiliser `fromisoformat` qui est plus robuste
            since_datetime = datetime.fromisoformat(since_timestamp_str.replace('Z', '+00:00'))
            
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

@login_required
@require_http_methods(["GET"])
def online_users_api(request):
    """API pour récupérer les utilisateurs en ligne."""
    ninety_seconds_ago = django_timezone.now() - timedelta(seconds=90)
    
    online_users_profiles = UserProfile.objects.filter(
        last_activity__gte=ninety_seconds_ago
    ).exclude(user=request.user).select_related('user')
    
    online_users_data = [
        {'username': profile.user.username} for profile in online_users_profiles
    ]
    
    return JsonResponse({
        'online_users_count': len(online_users_data),
        'online_users': online_users_data,
    })
