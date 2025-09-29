from django.urls import path
from . import views

app_name = 'live_sessions'

urlpatterns = [
    path('', views.session_list, name='list'),
    path('mes-sessions/', views.my_sessions, name='my_sessions'),
    path('<uuid:session_id>/', views.session_detail, name='detail'),
    path('<uuid:session_id>/rejoindre/', views.join_session, name='join'),
    path('<uuid:session_id>/quitter/', views.leave_session, name='leave'),
    path('<uuid:session_id>/question/', views.ask_question, name='ask_question'),
    path('<uuid:session_id>/enregistrement/', views.session_recording, name='recording'),
]