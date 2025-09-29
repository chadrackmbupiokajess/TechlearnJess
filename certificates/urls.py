from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('', views.my_certificates, name='my_certificates'),
    path('verifier/', views.verify_certificate, name='verify'),
    path('<uuid:certificate_id>/', views.certificate_detail, name='detail'),
    path('<uuid:certificate_id>/telecharger/', views.download_certificate, name='download'),
]