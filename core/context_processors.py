from .models import SiteSettings

def site_settings(request):
    """
    Rend les paramètres du site disponibles dans tous les templates.
    """
    return {'settings': SiteSettings.get_settings()}
