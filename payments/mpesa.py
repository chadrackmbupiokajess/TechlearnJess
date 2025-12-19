import requests
from django.conf import settings
from django.urls import reverse
import base64
import datetime
import json # Pour gérer les réponses JSON

# URL de base de l'API M-PESA (Sandbox)
MPESA_API_BASE_URL = "https://uat.openapi.m-pesa.com"
MPESA_MARKET = "vodacomRC" # Pour la RDC

def get_mpesa_api_token():
    """
    Obtient un token d'authentification (session ID) auprès de l'API M-PESA.
    """
    print("DEMANDE DE TOKEN M-PESA (UTILISATION DIRECTE DE LA CLÉ API)")
    return settings.MPESA_API_KEY # Votre clé API du bac à sable

def initiate_payment(payment, request):
    """
    Initie une transaction de paiement avec l'API M-PESA (STK Push).
    """
    token = get_mpesa_api_token()
    if not token:
        return None # Ou gérer l'erreur

    # Construire l'URL de callback que M-PESA appellera
    # Cette URL doit être accessible publiquement par M-PESA
    callback_url = request.build_absolute_uri(
        reverse('payments:mpesa_callback')
    )

    # Les données à envoyer à l'API M-PESA pour initier le paiement
    # Ces champs sont basés sur votre exemple et la documentation M-PESA C2B Single Stage
    payload = {
        "input_Amount": str(int(payment.amount)), # M-PESA attend souvent des entiers ou des chaînes
        "input_Country": "RDC", # Ou le code pays approprié
        "input_Currency": payment.currency, # USD ou CDF
        "input_CustomerMSISDN": payment.phone_number, # Utilise le numéro de test fourni
        "input_ServiceProviderCode": settings.MPESA_SERVICE_PROVIDER_CODE, # Le code 000000 de l'exemple
        "input_ThirdPartyConversationID": str(payment.payment_id), # ID unique pour la conversation
        "input_TransactionReference": str(payment.payment_id), # Référence de transaction
        "input_PurchasedItemsDesc": f"Paiement cours {payment.course.title}",
        "input_ShortCode": settings.MPESA_SHORT_CODE, # Votre numéro de marchand
        "input_CallbackUrl": callback_url, # L'URL où M-PESA enverra la notification
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "*",
    }

    # URL de l'API M-PESA pour initier un paiement (STK Push)
    api_url = f"{MPESA_API_BASE_URL}/sandbox/ipg/v2/{MPESA_MARKET}/c2bPayment/singleStage/"

    print(f"INITIATION DU PAIEMENT M-PESA AVEC LES DONNÉES : {payload}")
    print(f"URL API : {api_url}")
    print(f"HEADERS : {headers}")

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status() # Lève une exception pour les codes d'erreur HTTP (4xx ou 5xx)
        data = response.json()
        print(f"RÉPONSE API M-PESA : {json.dumps(data, indent=2)}")

        if data.get('output_ResponseCode') == '0' or data.get('output_ResponseDesc') == 'Request processed successfully':
            return reverse('payments:mpesa_pending', args=[payment.payment_id])
        else:
            print(f"Erreur M-PESA lors de l'initiation: {data.get('output_ResponseDesc', 'Erreur inconnue')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion à l'API M-PESA: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Erreur de décodage JSON de la réponse M-PESA: {response.text}")
        return None

def handle_callback(request):
    """
    Gère la notification de callback envoyée par M-PESA.
    """
    try:
        data = json.loads(request.body)
        print(f"CALLBACK M-PESA REÇU : {json.dumps(data, indent=2)}")

        transaction_id = data.get('input_ThirdPartyConversationID')
        response_code = data.get('output_ResponseCode')
        response_desc = data.get('output_ResponseDesc')

        from .models import Payment
        if transaction_id:
            try:
                payment = Payment.objects.get(payment_id=transaction_id)
                if response_code == '0':
                    payment.mark_as_completed()
                    print(f"Paiement {transaction_id} marqué comme COMPLETED.")
                else:
                    payment.mark_as_failed(reason=f"Statut M-PESA Callback : {response_desc} (Code: {response_code})")
                    print(f"Paiement {transaction_id} marqué comme FAILED.")
            except Payment.DoesNotExist:
                print(f"Paiement {transaction_id} non trouvé pour le callback M-PESA.")
        else:
            print("ID de transaction manquant dans le callback M-PESA.")

        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'C2B Payment received successfully'})
    except json.JSONDecodeError:
        print(f"Erreur de décodage JSON du callback M-PESA: {request.body}")
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Erreur inattendue lors du traitement du callback M-PESA: {e}")
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Internal Error'}, status=500)
