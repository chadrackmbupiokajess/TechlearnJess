from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import ForumCategory, ForumTopic, ForumPost


def forum_index(request):
    """Page d'accueil du forum"""
    categories = ForumCategory.objects.filter(est_actif=True)
    
    # Derniers sujets
    derniers_sujets = ForumTopic.objects.select_related('categorie', 'auteur').order_by('-derniere_activite')[:5]
    
    context = {
        'categories': categories,
        'derniers_sujets': derniers_sujets,
    }
    
    return render(request, 'forum/index.html', context)


def category_detail(request, slug):
    """Détail d'une catégorie"""
    categorie = get_object_or_404(ForumCategory, slug=slug, est_actif=True)
    sujets = ForumTopic.objects.filter(categorie=categorie).select_related('auteur')
    
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
        'categorie': categorie,
        'page_obj': page_obj,
        'search': search,
    }
    
    return render(request, 'forum/category_detail.html', context)


def topic_detail(request, category_slug, slug):
    """Détail d'un sujet"""
    categorie = get_object_or_404(ForumCategory, slug=category_slug, est_actif=True)
    sujet = get_object_or_404(ForumTopic, categorie=categorie, slug=slug)
    
    # Incrémenter les vues
    sujet.incrementer_vues()
    
    # Réponses
    reponses = sujet.reponses.select_related('auteur').order_by('cree_le')
    
    # Pagination
    paginator = Paginator(reponses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'categorie': categorie,
        'sujet': sujet,
        'page_obj': page_obj,
    }
    
    return render(request, 'forum/topic_detail.html', context)


@login_required
def create_topic(request, category_slug):
    """Créer un nouveau sujet"""
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
        'categorie': categorie,
    }
    
    return render(request, 'forum/create_topic.html', context)


@login_required
def create_post(request, category_slug, topic_slug):
    """Créer une réponse"""
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
            return redirect('forum:topic_detail', category_slug=category_slug, slug=topic_slug)
        else:
            messages.error(request, 'Veuillez saisir un contenu.')
    
    return redirect('forum:topic_detail', category_slug=category_slug, slug=topic_slug)