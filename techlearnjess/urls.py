from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from core.views import sitemap_xml, robots_txt

admin.site.site_header = "Administration Jessna TechLearn"
admin.site.site_title = "Portail d'administration Jessna TechLearn"
admin.site.index_title = "Bienvenue sur le portail d'administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # SEO files
    path('sitemap.xml', sitemap_xml, name='sitemap_xml'),
    path('robots.txt', robots_txt, name='robots_txt'),

    path('', include('core.urls')),
    path('comptes/', include('accounts.urls')),
    path('cours/', include('courses.urls')),
    path('forum/', include('forum.urls')),
    path('chat/', include('chat.urls')),
    path('certificats/', include('certificates.urls')),
    path('notifications/', include('notifications.urls')),
    path('paiements/', include('payments.urls')),
    path('sessions-live/', include('live_sessions.urls')),
    
    # Google Search Console verification
    path('googleff7e45855a024362.html', TemplateView.as_view(template_name='googleff7e45855a024362.html', content_type='text/html')),
    
    # AdSense ads.txt
    path('ads.txt', TemplateView.as_view(template_name='ads.txt', content_type='text/plain')),
]

# Servir les fichiers médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
