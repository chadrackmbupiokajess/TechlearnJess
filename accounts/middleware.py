from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from datetime import timedelta

class UpdateLastActivityMiddleware(MiddlewareMixin):
    """
    Middleware pour mettre à jour le champ `last_activity` de l'utilisateur
    à chaque requête.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        # S'assurer que l'utilisateur est authentifié
        if request.user.is_authenticated:
            # Mettre à jour le champ last_activity du profil utilisateur à chaque requête
            if hasattr(request.user, 'userprofile'):
                request.user.userprofile.last_activity = timezone.now()
                request.user.userprofile.save(update_fields=['last_activity'])
        
        # Continuer le traitement de la requête
        return None

    def process_response(self, request, response):
        # Si la réponse est une redirection vers la page de déconnexion,
        # mettez à jour le last_activity de l'utilisateur.
        if (
            hasattr(request, 'user') and
            request.user.is_authenticated and
            response.status_code == 302 and
            response.url == reverse('accounts:logout') # Assurez-vous que c'est le bon nom d'URL
        ):
            if hasattr(request.user, 'userprofile'):
                # Mettre à jour le last_activity à une date antérieure pour le marquer comme déconnecté
                request.user.userprofile.last_activity = timezone.now() - timedelta(minutes=6)
                request.user.userprofile.save(update_fields=['last_activity'])
        
        return response
