from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('parametres/', views.notification_settings, name='settings'),
    path('marquer-lu/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('marquer-tout-lu/', views.mark_all_as_read, name='mark_all_as_read'),
    path('supprimer/<int:notification_id>/', views.delete_notification, name='delete'),
    path('api/non-lues/', views.get_unread_count, name='unread_count'),
]