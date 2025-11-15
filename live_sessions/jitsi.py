import jwt
from datetime import datetime, timedelta
from django.conf import settings

def generate_jitsi_jwt(user, room_name, is_moderator=False):
    """
    Génère un jeton JWT pour une réunion JaaS 8x8.
    """
    try:
        with open(settings.JAAS_PRIVATE_KEY_PATH, 'r') as key_file:
            private_key = key_file.read()
    except FileNotFoundError:
        raise Exception(f"Fichier de clé privée JaaS non trouvé à l'emplacement : {settings.JAAS_PRIVATE_KEY_PATH}")

    payload = {
        'context': {
            'user': {
                'id': str(user.id),
                'name': user.get_full_name() or user.username,
                'avatar': user.userprofile.get_avatar_url(),
                'email': user.email,
                'moderator': is_moderator,  # CORRECTION: Utiliser un vrai booléen
            },
            'features': {
                "livestreaming": is_moderator,
                "recording": is_moderator,
                "transcription": is_moderator,
                "outbound-call": False,
            }
        },
        'aud': 'jitsi',
        'iss': 'chat',
        'sub': settings.JAAS_APP_ID,
        'room': '*',  # CORRECTION: Utiliser le wildcard '*'
        'exp': datetime.utcnow() + timedelta(hours=3),
        'nbf': datetime.utcnow() - timedelta(minutes=5),
    }

    headers = {
        'kid': settings.JAAS_API_KEY
    }

    token = jwt.encode(
        payload,
        private_key,
        algorithm='RS256',
        headers=headers
    )
    return token
