from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from django.http import HttpResponse
from django.template import loader
from datetime import datetime
from django.conf import settings

from .models import SiteSettings, Testimonial, FAQ, GalleryImage
from courses.models import Course, Enrollment
from notifications.models import Notification

User = get_user_model()


def handler500(request):
    """Gestionnaire d'erreur 500 personnalisé."""
    return render(request, '500.html', status=500)


def home(request):
    """Page d'accueil"""
    settings = SiteSettings.get_settings()
    
    latest_courses = Course.objects.filter(
        is_published=True
    ).order_by('-created_at')[:6]
    
    featured_testimonials = Testimonial.objects.filter(
        is_featured=True, 
        is_active=True
    )[:3]
    
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
    
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    
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
    settings = SiteSettings.get_settings()
    user = request.user
    
    current_enrollments = Enrollment.objects.filter(
        user=user,
        is_completed=False
    ).select_related('course')[:5]
    
    completed_enrollments = Enrollment.objects.filter(
        user=user,
        is_completed=True
    ).select_related('course')[:3]
    
    recent_notifications = Notification.objects.filter(
        user=user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    upcoming_sessions = []
    try:
        from live_sessions.models import LiveSession
        upcoming_sessions = LiveSession.objects.filter(
            participants=user,
            start_time__gte=timezone.now()
        ).order_by('start_time')[:3]
    except ImportError:
        pass
    
    user_stats = {
        'total_enrollments': Enrollment.objects.filter(user=user).count(),
        'completed_courses': Enrollment.objects.filter(user=user, is_completed=True).count(),
        'certificates_earned': 0,
        'forum_posts': 0,
    }
    
    if user_stats['total_enrollments'] > 0:
        user_stats['completion_rate'] = round(
            (user_stats['completed_courses'] / user_stats['total_enrollments']) * 100, 1
        )
    else:
        user_stats['completion_rate'] = 0
    
    context = {
        'settings': settings,
        'current_enrollments': current_enrollments,
        'completed_enrollments': completed_enrollments,
        'recent_notifications': recent_notifications,
        'upcoming_sessions': upcoming_sessions,
        'user_stats': user_stats,
    }
    
    return render(request, 'core/dashboard.html', context)

#privacy
def privacy_policy(request):
    """Page de politique de confidentialité"""
    return render(request, 'core/privacy_policy.html')


def faq_list(request):
    """Liste des FAQ"""
    settings = SiteSettings.get_settings()
    category = request.GET.get('category', 'all')
    
    faqs = FAQ.objects.filter(is_active=True)
    
    if category != 'all':
        faqs = faqs.filter(category=category)
    
    faq_categories = {}
    for faq in faqs:
        if faq.category not in faq_categories:
            faq_categories[faq.category] = []
        faq_categories[faq.category].append(faq)
    
    context = {
        'settings': settings,
        'faq_categories': faq_categories,
        'current_category': category,
        'categories': FAQ._meta.get_field('category').choices,
    }
    
    return render(request, 'core/faq.html', context)


def privacy_policy(request):
    """Page Politique de confidentialité"""
    settings = SiteSettings.get_settings()
    return render(request, 'core/privacy_policy.html', {'settings': settings})


def terms_of_service(request):
    """Page Conditions d'utilisation"""
    settings = SiteSettings.get_settings()
    return render(request, 'core/terms_of_service.html', {'settings': settings})


def legal_notice(request):
    """Page Mentions légales"""
    settings = SiteSettings.get_settings()
    return render(request, 'core/legal_notice.html', {'settings': settings})


def gallery(request):
    """Page galerie d'images"""
    settings = SiteSettings.get_settings()
    images = GalleryImage.objects.all()
    context = {
        'settings': settings,
        'images': images
    }
    return render(request, 'core/gallery.html', context)


def sitemap_xml(request):
    """Génération du sitemap XML pour le SEO"""
    domain = "https://techlearnjess.pythonanywhere.com"
    
    courses = Course.objects.filter(is_published=True)
    
    forum_topics = []
    try:
        from forum.models import Topic
        forum_topics = Topic.objects.filter(is_active=True)[:50]
    except ImportError:
        pass
    
    gallery_images = GalleryImage.objects.all()
    
    settings = SiteSettings.get_settings()
    
    context = {
        'domain': domain,
        'last_modified': settings.updated_at,
        'courses': courses,
        'forum_topics': forum_topics,
        'gallery_images': gallery_images,
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
        "Sitemap: https://techlearnjess.pythonanywhere.com/sitemap.xml",
        "",
        "# Pages importantes pour le SEO",
        "Allow: /",
        "Allow: /about/",
        "Allow: /courses/",
        "Allow: /forum/",
        "Allow: /live-sessions/",
        "Allow: /faq/",
        "Allow: /galerie/",
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

def ads_txt(request):
    """Serves the ads.txt file."""
    content = "google.com, pub-5640124347001712, DIRECT, f08c47fec0942fa0"
    return HttpResponse(content, content_type='text/plain')

def time_test_view(request):
    """Vue de test pour diagnostiquer les problèmes de temps."""
    user_timezone = request.session.get('django_timezone', 'N/A')
    
    context = {
        'datetime_now': datetime.now(),
        'timezone_now': timezone.now(),
        'user_timezone': user_timezone,
        'paypal_receiver_email': settings.PAYPAL_RECEIVER_EMAIL,
    }
    return render(request, 'core/time_test.html', context)
