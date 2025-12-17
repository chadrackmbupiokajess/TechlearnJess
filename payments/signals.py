from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from .models import Payment

@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # Le paiement a été effectué
        try:
            payment = Payment.objects.get(payment_id=ipn_obj.invoice)
        except Payment.DoesNotExist:
            return

        if payment.status == 'completed':
            return

        if payment.amount == ipn_obj.mc_gross:
            payment.mark_as_completed()
        else:
            # Le montant ne correspond pas
            payment.mark_as_failed(reason=f"Montant incorrect. Attendu: {payment.amount}, Reçu: {ipn_obj.mc_gross}")

    elif ipn_obj.payment_status in [ST_PP_FAILED, ST_PP_DENIED, ST_PP_EXPIRED]:
        try:
            payment = Payment.objects.get(payment_id=ipn_obj.invoice)
            payment.mark_as_failed(reason=f"Statut PayPal: {ipn_obj.payment_status}")
        except Payment.DoesNotExist:
            return
