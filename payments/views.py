from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from decimal import Decimal
import uuid

from .models import Payment, PaymentMethod, Invoice
from courses.models import Course
from core.models import SiteSettings

@login_required
def checkout(request, course_slug):
    """Page de paiement pour un cours"""
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
    """Créer un nouveau paiement"""
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    
    if course.is_free:
        return JsonResponse({'error': 'Ce cours est gratuit'}, status=400)
    
    payment_method_id = request.POST.get('payment_method')
    phone_number = request.POST.get('phone_number', '')
    
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
        phone_number=phone_number,
        status='pending'
    )
    
    return JsonResponse({
        'success': True,
        'payment_id': str(payment.payment_id),
        'redirect_url': reverse('payments:pending', kwargs={'payment_id': payment.payment_id})
    })


@login_required
def payment_pending(request, payment_id):
    """Affiche les instructions pour un paiement en attente."""
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
    """Page de succès du paiement"""
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user, status='completed')
    
    context = {
        'payment': payment,
    }
    
    return render(request, 'payments/success.html', context)


@login_required
def payment_history(request):
    """Historique des paiements"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'payments': payments,
    }
    
    return render(request, 'payments/history.html', context)


@login_required
def payment_detail(request, payment_id):
    """Détail d'un paiement"""
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user)
    
    context = {
        'payment': payment,
    }
    
    return render(request, 'payments/detail.html', context)


@login_required
def view_invoice(request, payment_id):
    """Afficher la facture HTML"""
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
    """Demander un remboursement"""
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user, status='completed')
    
    reason = request.POST.get('reason', '')
    if not reason:
        messages.error(request, "Veuillez indiquer la raison du remboursement.")
        return redirect('payments:detail', payment_id=payment_id)
    
    from .models import Refund
    if Refund.objects.filter(payment=payment).exists():
        messages.warning(request, "Une demande de remboursement existe déjà pour ce paiement.")
        return redirect('payments:detail', payment_id=payment_id)
    
    refund = Refund.objects.create(
        payment=payment,
        amount=payment.total_amount,
        reason=reason
    )
    
    messages.success(request, "Votre demande de remboursement a été soumise.")
    return redirect('payments:detail', payment_id=payment_id)
