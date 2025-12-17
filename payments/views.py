from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from decimal import Decimal
import uuid
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm

from .models import Payment, PaymentMethod, Invoice, Refund
from courses.models import Course
from core.models import SiteSettings

@login_required
def checkout(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    
    if course.is_free:
        messages.info(request, "Ce cours est gratuit.")
        return redirect('courses:enroll', slug=course_slug)
    
    from courses.models import Enrollment
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, "Vous êtes déjà inscrit à ce cours.")
        return redirect('courses:detail', slug=course_slug)
    
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    context = {
        'course': course,
        'payment_methods': payment_methods,
    }
    
    return render(request, 'payments/checkout.html', context)


@login_required
@require_http_methods(["POST"])
def create_payment(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    
    if course.is_free:
        return JsonResponse({'error': 'Ce cours est gratuit'}, status=400)
    
    payment_method_id = request.POST.get('payment_method')
    
    try:
        payment_method = PaymentMethod.objects.get(id=payment_method_id, is_active=True)
    except PaymentMethod.DoesNotExist:
        return JsonResponse({'error': 'Méthode de paiement invalide'}, status=400)
    
    payment = Payment.objects.create(
        user=request.user,
        course=course,
        payment_method=payment_method,
        amount=course.price,
        currency='USD',
        status='pending'
    )

    if payment_method.payment_type == 'paypal':
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('payments:process_paypal', kwargs={'payment_id': payment.payment_id})
        })
    else:
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('payments:pending', kwargs={'payment_id': payment.payment_id})
        })


@login_required
def process_paypal(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user)
    host = request.get_host()

    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": f'{payment.amount:.2f}',
        "item_name": payment.course.title,
        "invoice": str(payment.payment_id),
        "currency_code": "USD",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return_url": request.build_absolute_uri(reverse('payments:payment_success', args=[payment.payment_id])),
        "cancel_return": request.build_absolute_uri(reverse('payments:payment_cancelled', args=[payment.payment_id])),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {'form': form, 'payment': payment}
    return render(request, 'payments/process_paypal.html', context)


@login_required
def payment_pending(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user)
    
    if payment.status == 'completed':
        messages.success(request, "Votre paiement pour ce cours a déjà été confirmé.")
        return redirect('courses:learn', slug=payment.course.slug)
        
    messages.info(request, "Votre demande de paiement a été enregistrée. Veuillez suivre les instructions pour la finaliser.")
    
    context = {
        'payment': payment,
    }
    
    return render(request, 'payments/pending.html', context)


@login_required
def payment_success(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user)
    # La logique de complétion est maintenant dans le signal de save du modèle Payment
    messages.success(request, "Votre paiement a été effectué avec succès.")
    return render(request, 'payments/success.html', {'payment': payment})

@login_required
def payment_cancelled(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user)
    payment.status = 'cancelled'
    payment.save()
    messages.error(request, "Votre paiement a été annulé.")
    return render(request, 'payments/cancelled.html', {'payment': payment})


@login_required
def payment_history(request):
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'payments': payments,
    }
    return render(request, 'payments/history.html', context)


@login_required
def payment_detail(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user)
    context = {
        'payment': payment,
    }
    return render(request, 'payments/detail.html', context)


@login_required
def view_invoice(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user, status='completed')
    
    try:
        invoice = payment.invoice
    except Invoice.DoesNotExist:
        from datetime import datetime, timedelta
        invoice = Invoice.objects.create(
            payment=payment,
            due_date=datetime.now() + timedelta(days=30)
        )
    
    settings = SiteSettings.get_settings()

    context = {
        'invoice': invoice,
        'settings': settings,
    }
    
    return render(request, 'payments/invoice.html', context)


@login_required
@require_http_methods(["POST"])
def request_refund(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user, status='completed')
    
    reason = request.POST.get('reason', '')
    if not reason:
        messages.error(request, "Veuillez indiquer la raison du remboursement.")
        return redirect('payments:detail', payment_id=payment_id)
    
    if Refund.objects.filter(payment=payment).exists():
        messages.warning(request, "Une demande de remboursement existe déjà pour ce paiement.")
        return redirect('payments:detail', payment_id=payment_id)
    
    Refund.objects.create(
        payment=payment,
        amount=payment.total_amount,
        reason=reason
    )
    
    messages.success(request, "Votre demande de remboursement a été soumise.")
    return redirect('payments:detail', payment_id=payment_id)
