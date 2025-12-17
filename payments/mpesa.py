import requests
from django.conf import settings
from django.urls import reverse
import base64
import datetime

def get_mpesa_api_token():
    """
    Fonction pour obtenir un token d'authentification auprès de l'API M-PESA.
    (À remplir avec la logique de l'API M-PESA)
    """
    # Cette fonction devra probablement faire une requête POST à une URL de token
    # avec votre Consumer Key et Consumer Secret.
    print("DEMANDE DE TOKEN M-PESA (SIMULATION)")
    return "FAKE_MPESA_TOKEN_67890"

def initiate_payment(payment, request):
    """
    Initie une transaction de paiement avec l'API M-PESA (STK Push).
    (À remplir avec la logique de l'API M-PESA)
    """
    token = get_mpesa_api_token()
    
    # Construire l'URL de callback que M-PESA appellera
    callback_url = request.build_absolute_uri(
        reverse('payments:mpesa_callback')
    )

    # Les données à envoyer à l'API M-PESA pour initier le paiement
    # Ces champs sont des exemples, ils devront être ajustés selon la doc M-PESA
    payload = {
        "BusinessShortCode": settings.MPESA_SHORT_CODE,
        "Password": "GENERATED_PASSWORD_FROM_PASSKEY_AND_TIMESTAMP", # Ceci est complexe, à générer
        "Timestamp": datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(payment.amount), # M-PESA attend souvent des entiers
        "PartyA": payment.phone_number,
        "PartyB": settings.MPESA_SHORT_CODE,
        "PhoneNumber": payment.phone_number,
        "CallBackURL": callback_url,
        "AccountReference": str(payment.payment_id),
        "TransactionDesc": f"Paiement cours {payment.course.title}"
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # URL de l'API M-PESA pour initier un paiement (STK Push)
    # (cette URL devra être trouvée dans la documentation)
    api_url = "https://api.mpesa.com/stkpush/v1/processrequest" # URL D'EXEMPLE

    print(f"INITIATION DU PAIEMENT M-PESA (SIMULATION) AVEC LES DONNÉES : {payload}")

    # Dans la vraie implémentation, nous ferions une requête POST
    # response = requests.post(api_url, json=payload, headers=headers)
    # if response.status_code == 200:
    #     data = response.json()
    #     # M-PESA ne redirige pas, il envoie un push. On redirige vers une page d'attente.
    #     return reverse('payments:mpesa_pending', args=[payment.payment_id])
    # else:
    #     return None

    # Pour l'instant, nous simulons une redirection vers une page d'attente
    return reverse('payments:mpesa_pending', args=[payment.payment_id])

def handle_callback(request):
    """
    Gère la notification de callback envoyée par M-PESA.
    (À remplir avec la logique de l'API M-PESA)
    """
    data = request.json()
    print(f"CALLBACK M-PESA REÇU (SIMULATION) : {data}")

    # Ici, nous devrions :
    # 1. Vérifier l'authenticité de la requête (avec une signature, par exemple).
    # 2. Récupérer les informations de la transaction (AccountReference, ResultCode).
    # 3. Mettre à jour notre base de données.
    
    # Exemple de récupération d'infos (à ajuster selon la doc M-PESA)
    # result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
    # merchant_request_id = data.get('Body', {}).get('stkCallback', {}).get('MerchantRequestID')
    # checkout_request_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
    # account_reference = data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [])[0].get('Value')

    # from .models import Payment
    # try:
    #     payment = Payment.objects.get(payment_id=account_reference)
    #     if result_code == 0: # 0 signifie succès
    #         payment.mark_as_completed()
    #     else:
    #         payment.mark_as_failed(reason=f"Statut M-PESA : {result_code}")
    # except Payment.DoesNotExist:
    #     pass

    # Répondre à M-PESA pour confirmer la réception
    # return JsonResponse({'ResultCode': 0, 'ResultDesc': 'C2B Payment received successfully'})
    pass
