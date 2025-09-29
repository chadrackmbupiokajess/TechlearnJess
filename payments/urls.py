from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('historique/', views.payment_history, name='history'),
    path('cours/<slug:course_slug>/paiement/', views.checkout, name='checkout'),
    path('cours/<slug:course_slug>/creer-paiement/', views.create_payment, name='create_payment'),
    path('<uuid:payment_id>/traiter/', views.process_payment, name='process'),
    path('<uuid:payment_id>/succes/', views.payment_success, name='success'),
    path('<uuid:payment_id>/', views.payment_detail, name='detail'),
    path('<uuid:payment_id>/facture/', views.download_invoice, name='download_invoice'),
    path('<uuid:payment_id>/remboursement/', views.request_refund, name='request_refund'),
]