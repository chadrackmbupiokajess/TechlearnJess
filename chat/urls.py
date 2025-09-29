from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.liste_salons, name='liste_salons'),
    path('salon/<int:salon_id>/', views.salon_chat, name='salon_chat'),
    path('api/messages/<int:salon_id>/', views.messages_api, name='messages_api'),
]