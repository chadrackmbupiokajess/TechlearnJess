from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator

from .models import LiveSession, SessionParticipant, SessionQuestion


def session_list(request):
    """Liste des sessions live"""
    now = timezone.now()
    
    # Sessions à venir
    upcoming_sessions = LiveSession.objects.filter(
        start_time__gt=now,
        status='scheduled'
    ).order_by('start_time')
    
    # Sessions en cours
    live_sessions = LiveSession.objects.filter(
        start_time__lte=now,
        end_time__gte=now,
        status='live'
    )
    
    # Sessions passées (avec enregistrements)
    past_sessions = LiveSession.objects.filter(
        end_time__lt=now,
        status='ended',
        recording_url__isnull=False
    ).exclude(recording_url='').order_by('-end_time')[:10]
    
    context = {
        'upcoming_sessions': upcoming_sessions,
        'live_sessions': live_sessions,
        'past_sessions': past_sessions,
    }
    
    return render(request, 'live_sessions/session_list.html', context)


def session_detail(request, session_id):
    """Détail d'une session live"""
    session = get_object_or_404(LiveSession, session_id=session_id)
    
    # Vérifier si l'utilisateur peut voir cette session
    if not session.is_public and request.user.is_anonymous:
        messages.error(request, "Vous devez être connecté pour voir cette session.")
        return redirect('accounts:login')
    
    # Vérifier l'inscription si nécessaire
    is_enrolled = False
    can_join = False
    join_message = ""
    
    if request.user.is_authenticated:
        is_enrolled = session.participants.filter(id=request.user.id).exists()
        can_join, join_message = session.can_join(request.user)
    
    # Questions publiques
    questions = session.questions.filter(is_public=True).order_by('-asked_at')[:10]
    
    context = {
        'session': session,
        'is_enrolled': is_enrolled,
        'can_join': can_join,
        'join_message': join_message,
        'questions': questions,
    }
    
    return render(request, 'live_sessions/session_detail.html', context)


@login_required
@require_http_methods(["POST"])
def join_session(request, session_id):
    """Rejoindre une session live"""
    session = get_object_or_404(LiveSession, session_id=session_id)
    
    can_join, message = session.can_join(request.user)
    
    if not can_join:
        return JsonResponse({'error': message}, status=400)
    
    # Ajouter l'utilisateur comme participant
    participant, created = SessionParticipant.objects.get_or_create(
        session=session,
        user=request.user,
        defaults={'is_present': True}
    )
    
    if not created:
        participant.is_present = True
        participant.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Vous avez rejoint la session avec succès!',
        'meeting_url': session.meeting_url
    })


@login_required
@require_http_methods(["POST"])
def leave_session(request, session_id):
    """Quitter une session live"""
    session = get_object_or_404(LiveSession, session_id=session_id)
    
    try:
        participant = SessionParticipant.objects.get(session=session, user=request.user)
        participant.is_present = False
        participant.left_at = timezone.now()
        participant.save()
        
        return JsonResponse({'success': True, 'message': 'Vous avez quitté la session.'})
    except SessionParticipant.DoesNotExist:
        return JsonResponse({'error': 'Vous n\'êtes pas dans cette session.'}, status=400)


@login_required
@require_http_methods(["POST"])
def ask_question(request, session_id):
    """Poser une question pendant une session"""
    session = get_object_or_404(LiveSession, session_id=session_id)
    
    # Vérifier que l'utilisateur participe à la session
    if not session.participants.filter(id=request.user.id).exists():
        return JsonResponse({'error': 'Vous devez participer à la session pour poser une question.'}, status=403)
    
    question_text = request.POST.get('question', '').strip()
    if not question_text:
        return JsonResponse({'error': 'Veuillez saisir une question.'}, status=400)
    
    question = SessionQuestion.objects.create(
        session=session,
        user=request.user,
        question=question_text
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Votre question a été envoyée.',
        'question_id': question.id
    })


@login_required
def my_sessions(request):
    """Mes sessions live"""
    now = timezone.now()
    
    # Sessions à venir auxquelles je participe
    upcoming = LiveSession.objects.filter(
        participants=request.user,
        start_time__gt=now
    ).order_by('start_time')
    
    # Sessions passées auxquelles j'ai participé
    past = LiveSession.objects.filter(
        participants=request.user,
        end_time__lt=now
    ).order_by('-end_time')
    
    # Pagination pour les sessions passées
    paginator = Paginator(past, 10)
    page_number = request.GET.get('page')
    past_page = paginator.get_page(page_number)
    
    context = {
        'upcoming_sessions': upcoming,
        'past_sessions': past_page,
    }
    
    return render(request, 'live_sessions/my_sessions.html', context)


def session_recording(request, session_id):
    """Voir l'enregistrement d'une session"""
    session = get_object_or_404(LiveSession, session_id=session_id, status='ended')
    
    if not session.recording_url:
        messages.error(request, "Aucun enregistrement disponible pour cette session.")
        return redirect('live_sessions:detail', session_id=session_id)
    
    # Vérifier l'accès à l'enregistrement
    if not session.is_public and request.user.is_anonymous:
        messages.error(request, "Vous devez être connecté pour voir cet enregistrement.")
        return redirect('accounts:login')
    
    context = {
        'session': session,
    }
    
    return render(request, 'live_sessions/recording.html', context)