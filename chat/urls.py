from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.liste_salons, name='liste_salons'),
    path('salon/<int:salon_id>/', views.salon_chat, name='salon_chat'),
    path('salon/create/', views.creer_salon, name='creer_salon'),
    path('salon/<int:salon_id>/send_message/', views.envoyer_message, name='envoyer_message'), # Nouvelle URL pour envoyer un message
    path('api/messages/<int:salon_id>/', views.messages_api, name='messages_api'),
]