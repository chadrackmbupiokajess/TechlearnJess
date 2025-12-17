import requests
from django.conf import settings
from django.urls import reverse

def get_orange_money_api_token():
    """
    Fonction pour obtenir un token d'authentification auprès de l'API Orange Money.
    (À remplir avec la logique de l'API d'Orange)
    """
    print("DEMANDE DE TOKEN ORANGE MONEY (SIMULATION)")
    return "FAKE_TOKEN_12345"

def initiate_payment(payment, request):
    """
    Initie une transaction de paiement avec l'API Orange Money.
    (À remplir avec la logique de l'API d'Orange)
    """
    token = get_orange_money_api_token()
    
    callback_url = request.build_absolute_uri(
        reverse('payments:orange_money_callback')
    )

    payload = {
        "merchant_key": settings.ORANGE_MONEY_MERCHANT_KEY,
        "currency": payment.currency,
        "order_id": str(payment.payment_id),
        "amount": payment.amount,
        "customer_msisdn": payment.phone_number, # Ajout du numéro de téléphone
        "return_url": request.build_absolute_uri(reverse('payments:payment_success', args=[payment.payment_id])),
        "cancel_url": request.build_absolute_uri(reverse('payments:payment_cancelled', args=[payment.payment_id])),
        "notif_url": callback_url,
        "lang": "fr",
        "reference": "TechLearnJess Course Payment"
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    api_url = "https://api.orange.com/orange-money-webpay/v1/webpayment" # URL D'EXEMPLE

    print(f"INITIATION DU PAIEMENT ORANGE MONEY (SIMULATION) AVEC LES DONNÉES : {payload}")

    # Pour l'instant, nous simulons une redirection vers une page d'attente
    return reverse('payments:orange_money_pending', args=[payment.payment_id])

def handle_callback(request):
    """
    Gère la notification de callback envoyée par Orange Money.
    (À remplir avec la logique de l'API d'Orange)
    """
    data = request.json()
    print(f"CALLBACK ORANGE MONEY REÇU (SIMULATION) : {data}")
    
    order_id = data.get('order_id')
    status = data.get('status')

    # from .models import Payment
    # try:
    #     payment = Payment.objects.get(payment_id=order_id)
    #     if status == 'SUCCESS':
    #         payment.mark_as_completed()
    #     else:
    #         payment.mark_as_failed(reason=f"Statut Orange Money : {status}")
    # except Payment.DoesNotExist:
    #     pass

    pass
