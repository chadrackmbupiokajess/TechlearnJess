from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, F
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.http import JsonResponse # Importation pour les réponses JSON

from core.models import SiteSettings
from .models import ForumCategory, ForumTopic, ForumPost

def forum_index(request):
    """Page d'accueil du forum"""
    settings = SiteSettings.get_settings()
    categories = ForumCategory.objects.filter(est_actif=True)
    
    # Derniers sujets
    derniers_sujets = ForumTopic.objects.select_related('categorie', 'auteur', 'auteur__userprofile').order_by('-derniere_activite')[:5]
    
    # Statistiques du forum
    stats = {
        'total_topics': ForumTopic.objects.count(),
        'total_posts': ForumPost.objects.count(),
        'active_members': User.objects.filter(userprofile__last_activity__gte=timezone.now() - timedelta(days=30)).count(),
        'resolved_topics': ForumTopic.objects.filter(est_resolu=True).count(),
    }
    
    # Membres en ligne (dernières 5 minutes)
    online_members = User.objects.filter(userprofile__last_activity__gte=timezone.now() - timedelta(minutes=5)).select_related('userprofile')[:5]

    # Top contributeurs (sujets + réponses)
    top_contributors = User.objects.annotate(
        topic_count=Count('forumtopic', distinct=True),
        post_count=Count('forumpost', distinct=True)
    ).annotate(
        total_contributions=F('topic_count') + F('post_count')
    ).filter(
        total_contributions__gt=0
    ).order_by(
        '-total_contributions'
    )[:3]

    context = {
        'settings': settings,
        'categories': categories,
        'derniers_sujets': derniers_sujets,
        'stats': stats,
        'online_members': online_members,
        'top_contributors': top_contributors,
    }
    
    return render(request, 'forum/index.html', context)


@login_required
def select_category_for_topic(request):
    """Page pour choisir une catégorie avant de créer un sujet."""
    settings = SiteSettings.get_settings()
    categories = ForumCategory.objects.filter(est_actif=True)
    context = {
        'settings': settings,
        'categories': categories,
    }
    return render(request, 'forum/select_category.html', context)


def category_detail(request, slug):
    """Détail d'une catégorie"""
    settings = SiteSettings.get_settings()
    categorie = get_object_or_404(ForumCategory, slug=slug, est_actif=True)
    sujets = ForumTopic.objects.filter(categorie=categorie).select_related('auteur', 'auteur__userprofile')
    
    # Recherche
    search = request.GET.get('search')
    if search:
        sujets = sujets.filter(
            Q(titre__icontains=search) | Q(contenu__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(sujets, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'settings': settings,
        'categorie': categorie,
        'page_obj': page_obj,
        'search': search,
    }

    # Si la requête est AJAX, on renvoie seulement la partie des sujets
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'forum/includes/topic_list.html', context)
    
    return render(request, 'forum/category_detail.html', context)


def topic_detail(request, category_slug, slug):
    """Détail d'un sujet"""
    settings = SiteSettings.get_settings()
    categorie = get_object_or_404(ForumCategory, slug=category_slug, est_actif=True)
    sujet = get_object_or_404(ForumTopic, categorie=categorie, slug=slug)
    
    # Incrémenter les vues
    sujet.incrementer_vues()
    
    # Réponses
    reponses = sujet.reponses.select_related('auteur', 'auteur__userprofile').order_by('cree_le')
    
    # Pagination
    paginator = Paginator(reponses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'settings': settings,
        'categorie': categorie,
        'sujet': sujet,
        'page_obj': page_obj,
    }
    
    return render(request, 'forum/topic_detail.html', context)


@login_required
def create_topic(request, category_slug):
    """Créer un nouveau sujet"""
    settings = SiteSettings.get_settings()
    categorie = get_object_or_404(ForumCategory, slug=category_slug, est_actif=True)
    
    if request.method == 'POST':
        titre = request.POST.get('titre')
        contenu = request.POST.get('contenu')
        
        if titre and contenu:
            sujet = ForumTopic.objects.create(
                titre=titre,
                categorie=categorie,
                auteur=request.user,
                contenu=contenu
            )
            messages.success(request, 'Sujet créé avec succès!')
            return redirect('forum:topic_detail', category_slug=category_slug, slug=sujet.slug)
        else:
            messages.error(request, 'Veuillez remplir tous les champs.')
    
    context = {
        'settings': settings,
        'categorie': categorie,
    }
    
    return render(request, 'forum/create_topic.html', context)


@login_required
def create_post(request, category_slug, topic_slug):
    """Créer une réponse"""
    settings = SiteSettings.get_settings()
    categorie = get_object_or_404(ForumCategory, slug=category_slug, est_actif=True)
    sujet = get_object_or_404(ForumTopic, categorie=categorie, slug=topic_slug)
    
    if sujet.est_ferme:
        messages.error(request, 'Ce sujet est fermé.')
        return redirect('forum:topic_detail', category_slug=category_slug, slug=topic_slug)
    
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        
        if contenu:
            ForumPost.objects.create(
                sujet=sujet,
                auteur=request.user,
                contenu=contenu
            )
            messages.success(request, 'Réponse ajoutée avec succès!')
            return redirect('forum:topic_detail', category_slug=category_slug, slug=sujet.slug)
        else:
            messages.error(request, 'Veuillez saisir un contenu.')
    
    context = {
        'settings': settings,
        'categorie': categorie,
        'sujet': sujet,
    }
    
    return redirect('forum:topic_detail', category_slug=category_slug, slug=topic_slug)