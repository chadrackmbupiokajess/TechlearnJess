from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from django.http import HttpResponse
from django.template import loader
from datetime import timedelta

from .models import SiteSettings, Testimonial, FAQ
from courses.models import Course, Enrollment
from notifications.models import Notification

User = get_user_model()


def home(request):
    """Page d'accueil"""
    settings = SiteSettings.get_settings()
    
    # Derniers cours disponibles
    latest_courses = Course.objects.filter(
        is_published=True
    ).order_by('-created_at')[:6]
    
    # Témoignages mis en avant
    featured_testimonials = Testimonial.objects.filter(
        is_featured=True, 
        is_active=True
    )[:3]
    
    # Statistiques générales
    stats = {
        'total_courses': Course.objects.filter(is_published=True).count(),
        'total_students': User.objects.filter(is_active=True).count(),
        'total_enrollments': Enrollment.objects.count(),
    }
    
    context = {
        'settings': settings,
        'latest_courses': latest_courses,
        'testimonials': featured_testimonials,
        'stats': stats,
    }
    
    return render(request, 'core/home.html', context)


def about(request):
    """Page à propos"""
    settings = SiteSettings.get_settings()
    
    # Témoignages actifs
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    
    # FAQ générale
    faqs = FAQ.objects.filter(
        category='general',
        is_active=True
    )[:5]
    
    context = {
        'settings': settings,
        'testimonials': testimonials,
        'faqs': faqs,
    }
    
    return render(request, 'core/about.html', context)


@login_required
def dashboard(request):
    """Tableau de bord utilisateur"""
    user = request.user
    
    # Cours en cours
    current_enrollments = Enrollment.objects.filter(
        user=user,
        is_completed=False
    ).select_related('course')[:5]
    
    # Cours terminés
    completed_enrollments = Enrollment.objects.filter(
        user=user,
        is_completed=True
    ).select_related('course')[:3]
    
    # Notifications récentes non lues
    recent_notifications = Notification.objects.filter(
        user=user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    # Sessions live à venir (si l'app existe)
    upcoming_sessions = []
    try:
        from live_sessions.models import LiveSession
        upcoming_sessions = LiveSession.objects.filter(
            participants=user,
            start_time__gte=timezone.now()
        ).order_by('start_time')[:3]
    except ImportError:
        pass
    
    # Statistiques personnelles
    user_stats = {
        'total_enrollments': Enrollment.objects.filter(user=user).count(),
        'completed_courses': Enrollment.objects.filter(user=user, is_completed=True).count(),
        'certificates_earned': 0,  # À implémenter avec l'app certificates
        'forum_posts': 0,  # À implémenter avec l'app forum
    }
    
    # Calcul du taux de complétion
    if user_stats['total_enrollments'] > 0:
        user_stats['completion_rate'] = round(
            (user_stats['completed_courses'] / user_stats['total_enrollments']) * 100, 1
        )
    else:
        user_stats['completion_rate'] = 0
    
    context = {
        'current_enrollments': current_enrollments,
        'completed_enrollments': completed_enrollments,
        'recent_notifications': recent_notifications,
        'upcoming_sessions': upcoming_sessions,
        'user_stats': user_stats,
    }
    
    return render(request, 'core/dashboard.html', context)


def faq_list(request):
    """Liste des FAQ"""
    category = request.GET.get('category', 'all')
    
    faqs = FAQ.objects.filter(is_active=True)
    
    if category != 'all':
        faqs = faqs.filter(category=category)
    
    # Grouper par catégorie
    faq_categories = {}
    for faq in faqs:
        if faq.category not in faq_categories:
            faq_categories[faq.category] = []
        faq_categories[faq.category].append(faq)
    
    context = {
        'faq_categories': faq_categories,
        'current_category': category,
        'categories': FAQ._meta.get_field('category').choices,
    }
    
    return render(request, 'core/faq.html', context)


def privacy_policy(request):
    """Page Politique de confidentialité"""
    from decouple import config
    
    context = {
        'company_name': config('COMPANY_NAME'),
        'company_address': config('COMPANY_ADDRESS'),
        'company_email': config('COMPANY_EMAIL'),
        'company_phone': config('COMPANY_PHONE'),
        'data_protection_email': config('DATA_PROTECTION_EMAIL'),
        'privacy_policy_version': config('PRIVACY_POLICY_VERSION'),
        'privacy_policy_date': config('PRIVACY_POLICY_DATE'),
        'data_controller': config('DATA_CONTROLLER'),
    }
    
    return render(request, 'core/privacy_policy.html', context)


def terms_of_service(request):
    """Page Conditions d'utilisation"""
    from decouple import config
    
    context = {
        'company_name': config('COMPANY_NAME'),
        'company_address': config('COMPANY_ADDRESS'),
        'company_email': config('COMPANY_EMAIL'),
        'company_phone': config('COMPANY_PHONE'),
        'company_website': config('COMPANY_WEBSITE'),
        'terms_version': config('TERMS_VERSION'),
        'terms_date': config('TERMS_DATE'),
        'governing_law': config('GOVERNING_LAW'),
    }
    
    return render(request, 'core/terms_of_service.html', context)


def legal_notice(request):
    """Page Mentions légales"""
    from decouple import config
    
    context = {
        'company_name': config('COMPANY_NAME'),
        'company_address': config('COMPANY_ADDRESS'),
        'company_email': config('COMPANY_EMAIL'),
        'company_phone': config('COMPANY_PHONE'),
        'company_website': config('COMPANY_WEBSITE'),
        'legal_representative': config('LEGAL_REPRESENTATIVE'),
        'legal_title': config('LEGAL_TITLE'),
        'registration_number': config('REGISTRATION_NUMBER'),
        'tax_number': config('TAX_NUMBER'),
    }
    
    return render(request, 'core/legal_notice.html', context)


def sitemap_xml(request):
    """Génération du sitemap XML pour le SEO"""
    from django.contrib.sites.models import Site
    
    try:
        current_site = Site.objects.get_current()
        domain = f"https://{current_site.domain}"
    except:
        domain = "https://techlearnjess.onrender.com"
    
    # Récupérer tous les cours publiés
    courses = Course.objects.filter(is_published=True)
    
    # Récupérer les topics du forum (si disponible)
    forum_topics = []
    try:
        from forum.models import Topic
        forum_topics = Topic.objects.filter(is_active=True)[:50]  # Limiter à 50
    except ImportError:
        pass
    
    context = {
        'domain': domain,
        'current_date': timezone.now(),
        'courses': courses,
        'forum_topics': forum_topics,
    }
    
    template = loader.get_template('sitemap.xml')
    xml_content = template.render(context, request)
    
    return HttpResponse(xml_content, content_type='application/xml')


def robots_txt(request):
    """Génération du fichier robots.txt"""
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "# Sitemap",
        "Sitemap: https://techlearnjess.onrender.com/sitemap.xml",
        "",
        "# Pages importantes pour le SEO",
        "Allow: /",
        "Allow: /about/",
        "Allow: /courses/",
        "Allow: /forum/",
        "Allow: /live-sessions/",
        "Allow: /faq/",
        "",
        "# Bloquer les pages administratives",
        "Disallow: /admin/",
        "Disallow: /accounts/logout/",
        "Disallow: /api/",
        "",
        "# Bloquer les fichiers temporaires",
        "Disallow: /*.tmp$",
        "Disallow: /*.log$",
        "",
        "# Informations sur le fondateur Chadrack Mbu Jess",
        "# Site créé par Chadrack Mbu Jess (Chadrackmbujess)",
        "# Contact: chadrackmbujess@gmail.com",
        "# Portfolio: https://chadrackmbu.pythonanywhere.com/",
    ]
    
    return HttpResponse("\n".join(lines), content_type="text/plain")