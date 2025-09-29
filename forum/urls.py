from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.forum_index, name='index'),
    path('<slug:slug>/', views.category_detail, name='category_detail'),
    path('<slug:category_slug>/nouveau/', views.create_topic, name='create_topic'),
    path('<slug:category_slug>/<slug:slug>/', views.topic_detail, name='topic_detail'),
    path('<slug:category_slug>/<slug:topic_slug>/repondre/', views.create_post, name='create_post'),
]