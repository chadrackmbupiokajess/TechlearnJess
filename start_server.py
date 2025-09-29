#!/usr/bin/env python
"""
Script de démarrage pour serveur ASGI sur Render
Utilise Uvicorn avec l'application ASGI complète
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techlearnjess.settings')

def main():
    """Fonction principale de démarrage"""
    try:
        django.setup()
        
        # Lancer Uvicorn avec l'application ASGI complète
        import uvicorn
        from techlearnjess.asgi import get_asgi_application_full
        
        port = int(os.environ.get('PORT', '10000'))
        
        print(f"🚀 Démarrage du serveur ASGI avec WebSockets sur le port {port}")
        
        # Utiliser l'application ASGI complète
        app = get_asgi_application_full()
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur de démarrage: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()