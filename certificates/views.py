from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Certificate


@login_required
def my_certificates(request):
    """Mes certificats"""
    certificates = Certificate.objects.filter(user=request.user, is_valid=True)
    
    context = {
        'certificates': certificates,
    }
    
    return render(request, 'certificates/my_certificates.html', context)


def certificate_detail(request, certificate_id):
    """Détail d'un certificat (vérification publique)"""
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id, is_valid=True)
    
    context = {
        'certificate': certificate,
        'is_verification': True,
    }
    
    return render(request, 'certificates/certificate_detail.html', context)


@login_required
def download_certificate(request, certificate_id):
    """Télécharger un certificat PDF"""
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id, is_valid=True)
    
    # Vérifier que l'utilisateur peut télécharger ce certificat
    if certificate.user != request.user and not request.user.is_staff:
        raise PermissionDenied("Vous n'avez pas l'autorisation de télécharger ce certificat.")
    
    if not certificate.pdf_file:
        messages.error(request, "Le fichier PDF n'est pas disponible.")
        return redirect('certificates:my_certificates')
    
    try:
        with open(certificate.pdf_file.path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="certificat_{certificate.certificate_id}.pdf"'
            return response
    except FileNotFoundError:
        messages.error(request, "Le fichier PDF n'a pas été trouvé.")
        return redirect('certificates:my_certificates')


def verify_certificate(request):
    """Page de vérification de certificat"""
    certificate = None
    error_message = None
    
    if request.method == 'POST':
        certificate_id = request.POST.get('certificate_id', '').strip()
        
        if certificate_id:
            try:
                certificate = Certificate.objects.get(certificate_id=certificate_id, is_valid=True)
            except Certificate.DoesNotExist:
                error_message = "Certificat non trouvé ou invalide."
        else:
            error_message = "Veuillez saisir un ID de certificat."
    
    context = {
        'certificate': certificate,
        'error_message': error_message,
    }
    
    return render(request, 'certificates/verify.html', context)