from django.utils import timezone
import pytz

class TimezoneMiddleware:
    """
    Middleware qui active le fuseau horaire de l'utilisateur pour chaque requête.
    Utilise la nouvelle syntaxe de middleware de Django.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Utilise un bloc try/finally pour garantir que le fuseau horaire est toujours désactivé
        try:
            if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
                user_tz_str = str(request.user.userprofile.timezone)
                if user_tz_str:
                    # Active le fuseau horaire de l'utilisateur
                    timezone.activate(pytz.timezone(user_tz_str))
                else:
                    # Si aucun fuseau n'est défini, désactive pour utiliser celui par défaut
                    timezone.deactivate()
            else:
                # Pour les utilisateurs anonymes, utilise le fuseau par défaut
                timezone.deactivate()
            
            response = self.get_response(request)
        
        except pytz.UnknownTimeZoneError:
            # Si le fuseau horaire de la BDD est invalide, on utilise celui par défaut
            timezone.deactivate()
            response = self.get_response(request)

        finally:
            # Désactive le fuseau horaire après que la réponse a été traitée
            timezone.deactivate()
            
        return response


class UpdateLastActivityMiddleware:
    """
    Middleware pour mettre à jour le champ `last_activity` de l'utilisateur.
    Utilise la nouvelle syntaxe de middleware de Django.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Ce code s'exécute après la vue.
        # Le fuseau horaire de l'utilisateur est toujours actif ici grâce au TimezoneMiddleware.
        if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
            request.user.userprofile.last_activity = timezone.now()
            request.user.userprofile.save(update_fields=['last_activity'])
            
        return response
