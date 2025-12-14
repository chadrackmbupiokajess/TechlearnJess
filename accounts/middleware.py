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
            # Mettre à jour le champ last_activity du profil utilisateur
            # On utilise update_fields pour être plus efficace et éviter de déclencher
            # d'autres signaux de sauvegarde inutilement.
            if hasattr(request.user, 'userprofile'):
                request.user.userprofile.last_activity = timezone.now()
                request.user.userprofile.save(update_fields=['last_activity'])
        
        # Continuer le traitement de la requête
        return None
