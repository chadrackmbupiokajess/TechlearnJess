from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from .models import UserProfile, LoginHistory
from .forms import UserRegistrationForm, UserProfileForm, UserUpdateForm


def register(request):
    """Inscription d'un nouvel utilisateur"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé avec succès pour {username}! Vous pouvez maintenant vous connecter.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    """Connexion utilisateur"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Enregistrer l'historique de connexion
            LoginHistory.objects.create(
                user=user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                is_successful=True
            )
            
            messages.success(request, f'Bienvenue {user.get_full_name() or user.username}!')
            
            # Redirection vers la page demandée ou le dashboard
            next_page = request.GET.get('next', 'core:dashboard')
            return redirect(next_page)
        else:
            # Enregistrer la tentative échouée
            try:
                user_obj = User.objects.get(username=username)
                LoginHistory.objects.create(
                    user=user_obj,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    is_successful=False
                )
            except User.DoesNotExist:
                pass
            
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'accounts/login.html')


def user_logout(request):
    """Déconnexion utilisateur"""
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('core:home')


@login_required
def profile(request, username=None):
    """Affichage du profil utilisateur"""
    if username:
        user = get_object_or_404(User, username=username)
        is_own_profile = request.user == user
    else:
        user = request.user
        is_own_profile = True
    
    profile = get_object_or_404(UserProfile, user=user)
    
    # Statistiques du profil
    stats = {
        'total_courses': 0,
        'completed_courses': profile.total_courses_completed,
        'certificates': profile.total_certificates,
        'join_date': user.date_joined,
    }
    
    # Cours récents (si l'utilisateur consulte son propre profil)
    recent_courses = []
    if is_own_profile:
        try:
            from courses.models import Enrollment
            recent_courses = Enrollment.objects.filter(
                user=user
            ).select_related('course').order_by('-enrolled_at')[:5]
        except ImportError:
            pass
    
    context = {
        'profile_user': user,
        'profile': profile,
        'is_own_profile': is_own_profile,
        'stats': stats,
        'recent_courses': recent_courses,
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """Modification du profil utilisateur"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'accounts/edit_profile.html', context)


@login_required
def change_password(request):
    """Changement de mot de passe"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important pour maintenir la session
            messages.success(request, 'Votre mot de passe a été changé avec succès!')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def login_history(request):
    """Historique des connexions"""
    history = LoginHistory.objects.filter(user=request.user)[:20]
    return render(request, 'accounts/login_history.html', {'history': history})


@login_required
@require_http_methods(["POST"])
def delete_account(request):
    """Suppression du compte utilisateur"""
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        
        if user is not None:
            user.is_active = False
            user.save()
            logout(request)
            messages.success(request, 'Votre compte a été désactivé avec succès.')
            return redirect('core:home')
        else:
            messages.error(request, 'Mot de passe incorrect.')
    
    return redirect('accounts:profile')


def get_client_ip(request):
    """Récupérer l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip