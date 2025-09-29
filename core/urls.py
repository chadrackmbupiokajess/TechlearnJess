from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('a-propos/', views.about, name='about'),
    path('tableau-de-bord/', views.dashboard, name='dashboard'),
    path('faq/', views.faq_list, name='faq'),
    
    # Pages légales
    path('politique-confidentialite/', views.privacy_policy, name='privacy_policy'),
    path('conditions-utilisation/', views.terms_of_service, name='terms_of_service'),
    path('mentions-legales/', views.legal_notice, name='legal_notice'),
    
    # SEO
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
]