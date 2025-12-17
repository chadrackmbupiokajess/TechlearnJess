from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('historique/', views.payment_history, name='history'),
    path('cours/<slug:course_slug>/paiement/', views.checkout, name='checkout'),
    path('cours/<slug:course_slug>/creer-paiement/', views.create_payment, name='create_payment'),
    
    # URLs pour les paiements manuels (espèces, etc.)
    path('<uuid:payment_id>/en-attente/', views.payment_pending, name='pending'),
    
    # URLs pour PayPal
    path('<uuid:payment_id>/paypal/', views.process_paypal, name='process_paypal'),
    
    # URLs pour Orange Money
    path('<uuid:payment_id>/orange-money/', views.orange_money_pending, name='orange_money_pending'),
    path('callback/orange-money/', views.orange_money_callback, name='orange_money_callback'),

    # URLs pour M-PESA
    path('<uuid:payment_id>/mpesa/', views.mpesa_pending, name='mpesa_pending'),
    path('callback/mpesa/', views.mpesa_callback, name='mpesa_callback'),

    # URLs de retour génériques
    path('<uuid:payment_id>/succes/', views.payment_success, name='payment_success'),
    path('<uuid:payment_id>/annule/', views.payment_cancelled, name='payment_cancelled'),
    
    # URLs de gestion
    path('<uuid:payment_id>/', views.payment_detail, name='detail'),
    path('<uuid:payment_id>/facture/', views.view_invoice, name='view_invoice'),
    path('<uuid:payment_id>/remboursement/', views.request_refund, name='request_refund'),
]
