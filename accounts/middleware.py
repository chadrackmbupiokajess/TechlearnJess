from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

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
                # Mettre à jour `last_activity` seulement si plus de 60 secondes se sont écoulées
                # pour éviter des écritures en base de données à chaque requête.
                if (timezone.now() - request.user.userprofile.last_activity).seconds > 60:
                    request.user.userprofile.last_activity = timezone.now()
                    request.user.userprofile.save(update_fields=['last_activity'])
        
        # Continuer le traitement de la requête
        return None
