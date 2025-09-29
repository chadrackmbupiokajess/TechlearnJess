#!/usr/bin/env python
"""
Script de gestion des médias pour TechLearnJess
Initialise la structure de dossiers et gère les fichiers médias
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techlearnjess.settings')
django.setup()

from django.conf import settings
from core.utils import create_media_directories


def init_media_structure():
    """Initialise la structure de dossiers pour les médias"""
    print("🚀 Initialisation de la structure des médias...")
    
    # Créer le dossier media principal
    settings.MEDIA_ROOT.mkdir(exist_ok=True)
    print(f"✅ Dossier principal créé: {settings.MEDIA_ROOT}")
    
    # Créer tous les sous-dossiers
    create_media_directories()
    print("✅ Structure de dossiers créée:")
    
    # Lister la structure créée
    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
        level = root.replace(str(settings.MEDIA_ROOT), '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}📁 {os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if file != '.gitkeep':
                print(f"{subindent}📄 {file}")


def create_gitignore():
    """Crée un .gitignore pour les médias"""
    gitignore_content = """# Ignorer tous les fichiers médias sauf la structure
*
!.gitkeep
!*/
"""
    
    gitignore_path = settings.MEDIA_ROOT / '.gitignore'
    with open(gitignore_path, 'w') as f:
        f.write(gitignore_content)
    print(f"✅ .gitignore créé: {gitignore_path}")


def show_media_info():
    """Affiche les informations sur le stockage des médias"""
    print("\n📊 Configuration du stockage des médias:")
    print(f"📁 Dossier racine: {settings.MEDIA_ROOT}")
    print(f"🌐 URL de base: {settings.MEDIA_URL}")
    print(f"🔧 Mode DEBUG: {settings.DEBUG}")
    
    print("\n📋 Types de fichiers supportés:")
    from core.utils import ALLOWED_EXTENSIONS, FILE_SIZE_LIMITS
    
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        size_limit = FILE_SIZE_LIMITS.get(file_type, 'N/A')
        print(f"  {file_type.upper()}: {', '.join(extensions)} (max: {size_limit}MB)")


def clean_empty_dirs():
    """Nettoie les dossiers vides"""
    print("\n🧹 Nettoyage des dossiers vides...")
    cleaned = 0
    
    for root, dirs, files in os.walk(settings.MEDIA_ROOT, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                # Ne supprimer que si vide (sauf .gitkeep)
                contents = list(dir_path.iterdir())
                if not contents or (len(contents) == 1 and contents[0].name == '.gitkeep'):
                    continue  # Garder les dossiers avec .gitkeep
                elif not any(item.is_file() for item in contents):
                    dir_path.rmdir()
                    cleaned += 1
                    print(f"  🗑️ Supprimé: {dir_path}")
            except OSError:
                pass
    
    print(f"✅ {cleaned} dossiers vides supprimés")


def main():
    """Fonction principale"""
    if len(sys.argv) < 2:
        print("Usage: python manage_media.py [init|info|clean]")
        print("  init  - Initialise la structure des dossiers")
        print("  info  - Affiche les informations de configuration")
        print("  clean - Nettoie les dossiers vides")
        return
    
    command = sys.argv[1]
    
    if command == 'init':
        init_media_structure()
        create_gitignore()
        show_media_info()
        print("\n🎉 Structure des médias initialisée avec succès!")
        print("💡 Les fichiers seront maintenant stockés localement et persistants.")
        
    elif command == 'info':
        show_media_info()
        
    elif command == 'clean':
        clean_empty_dirs()
        
    else:
        print(f"❌ Commande inconnue: {command}")


if __name__ == '__main__':
    main()