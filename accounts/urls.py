from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('inscription/', views.register, name='register'),
    path('connexion/', views.user_login, name='login'),
    path('deconnexion/', views.user_logout, name='logout'),
    path('profil/', views.profile, name='profile'),
    path('profil/<str:username>/', views.profile, name='user_profile'),
    path('modifier-profil/', views.edit_profile, name='edit_profile'),
    path('changer-mot-de-passe/', views.change_password, name='change_password'),
    path('historique-connexions/', views.login_history, name='login_history'),
    path('supprimer-compte/', views.delete_account, name='delete_account'),
]