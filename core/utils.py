"""
Utilitaires pour la gestion des médias et uploads
"""
import os
import uuid
from pathlib import Path
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import hashlib


def get_upload_path(instance, filename, folder='images'):
    """
    Génère un chemin d'upload unique pour les fichiers
    Similaire au système WhatsApp - stockage local organisé
    """
    # Obtenir l'extension du fichier
    ext = filename.split('.')[-1].lower()
    
    # Générer un nom unique
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # Créer le chemin basé sur la date et le type
    from datetime import datetime
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    day = now.strftime('%d')
    
    return f"{folder}/{year}/{month}/{day}/{unique_filename}"


def save_uploaded_file(uploaded_file, folder='images', compress=True):
    """
    Sauvegarde un fichier uploadé localement
    Retourne le chemin relatif du fichier sauvegardé
    """
    try:
        # Générer le chemin d'upload
        file_path = get_upload_path(None, uploaded_file.name, folder)
        full_path = settings.MEDIA_ROOT / file_path
        
        # Créer les dossiers si nécessaire
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder le fichier
        if compress and folder == 'images' and uploaded_file.content_type.startswith('image/'):
            # Compresser l'image
            compressed_file = compress_image(uploaded_file)
            with open(full_path, 'wb') as f:
                f.write(compressed_file.read())
        else:
            # Sauvegarder tel quel
            with open(full_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
        
        return file_path
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")
        return None


def compress_image(image_file, quality=85, max_size=(1920, 1080)):
    """
    Compresse une image pour optimiser l'espace de stockage
    """
    try:
        # Ouvrir l'image
        img = Image.open(image_file)
        
        # Convertir en RGB si nécessaire
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Redimensionner si trop grande
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Sauvegarder dans un buffer
        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        buffer.seek(0)
        
        return ContentFile(buffer.read())
    except Exception as e:
        print(f"Erreur lors de la compression: {e}")
        return image_file


def get_file_hash(file_path):
    """
    Calcule le hash MD5 d'un fichier pour éviter les doublons
    """
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None


def create_media_directories():
    """
    Crée la structure de dossiers pour les médias
    """
    media_dirs = [
        'images/avatars',
        'images/courses',
        'images/certificates', 
        'images/forum',
        'images/chat',
        'videos/courses',
        'videos/live_sessions',
        'documents/courses',
        'documents/certificates',
        'documents/uploads',
    ]
    
    for dir_path in media_dirs:
        full_path = settings.MEDIA_ROOT / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        
        # Créer un fichier .gitkeep pour garder le dossier dans git
        gitkeep_file = full_path / '.gitkeep'
        if not gitkeep_file.exists():
            gitkeep_file.touch()


def get_media_url(file_path):
    """
    Retourne l'URL complète d'un fichier média
    """
    if file_path:
        return f"{settings.MEDIA_URL}{file_path}"
    return None


def delete_media_file(file_path):
    """
    Supprime un fichier média du stockage local
    """
    try:
        full_path = settings.MEDIA_ROOT / file_path
        if full_path.exists():
            full_path.unlink()
            return True
    except Exception as e:
        print(f"Erreur lors de la suppression: {e}")
    return False


def get_file_size_mb(file_path):
    """
    Retourne la taille d'un fichier en MB
    """
    try:
        full_path = settings.MEDIA_ROOT / file_path
        if full_path.exists():
            size_bytes = full_path.stat().st_size
            return round(size_bytes / (1024 * 1024), 2)
    except:
        pass
    return 0


# Limites de taille par type de fichier (en MB)
FILE_SIZE_LIMITS = {
    'image': 10,  # 10 MB max pour les images
    'video': 100,  # 100 MB max pour les vidéos
    'document': 25,  # 25 MB max pour les documents
}

# Extensions autorisées
ALLOWED_EXTENSIONS = {
    'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    'video': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'],
    'document': ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt'],
}


def validate_file(uploaded_file, file_type='image'):
    """
    Valide un fichier uploadé (taille, extension, etc.)
    """
    errors = []
    
    # Vérifier l'extension
    ext = uploaded_file.name.split('.')[-1].lower()
    if ext not in ALLOWED_EXTENSIONS.get(file_type, []):
        errors.append(f"Extension {ext} non autorisée pour {file_type}")
    
    # Vérifier la taille
    size_mb = uploaded_file.size / (1024 * 1024)
    max_size = FILE_SIZE_LIMITS.get(file_type, 10)
    if size_mb > max_size:
        errors.append(f"Fichier trop volumineux ({size_mb:.1f}MB). Maximum: {max_size}MB")
    
    return errors