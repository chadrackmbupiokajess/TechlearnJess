"""
ASGI config for techlearnjess project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
from django.core.wsgi import get_wsgi_application

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techlearnjess.settings')

# Pour compatibilité avec Gunicorn, on utilise WSGI par défaut
django.setup()

# Application WSGI pour Gunicorn
wsgi_application = get_wsgi_application()

# Wrapper pour compatibilité
def application(environ, start_response):
    """
    Application hybride WSGI/ASGI
    Utilise WSGI pour la compatibilité avec Gunicorn
    """
    return wsgi_application(environ, start_response)

# Configuration ASGI complète (pour serveurs ASGI comme Uvicorn/Daphne)
def get_asgi_application_full():
    """Retourne l'application ASGI complète avec WebSockets"""
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack
    from django.core.asgi import get_asgi_application
    import chat.routing
    
    return ProtocolTypeRouter({
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                chat.routing.websocket_urlpatterns
            )
        ),
    })
