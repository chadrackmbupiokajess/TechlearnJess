from .models import SiteSettings

class SiteSettingsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.settings = SiteSettings.get_settings()
        response = self.get_response(request)
        return response
