from pathlib import Path
import os
from decouple import config
from datetime import date

# ------------------------------
# BASE DIR
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------
# SECURITY
# ------------------------------
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'techlearnjess.pythonanywhere.com',
    '192.168.1.193',
    '.ngrok-free.app'
]

# ------------------------------
# APPLICATIONS
# ------------------------------
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',

    # Third party apps
    'crispy_forms',
    'crispy_tailwind',
    'ckeditor',
    'ckeditor_uploader',
    'corsheaders',
    'django_countries',
    'paypal.standard.ipn',

    # Local apps
    'core',
    'accounts',
    'courses',
    'forum',
    'chat',
    'certificates',
    'notifications',
    'payments',
    'live_sessions',
]

# ------------------------------
# SITE ID
# ------------------------------
SITE_ID = 1

# ------------------------------
# MIDDLEWARE
# ------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.UpdateLastActivityMiddleware',
    'accounts.middleware.TimezoneMiddleware',
]

# ------------------------------
# CORS
# ------------------------------
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3003",
    "http://127.0.0.1:8000",
    "http://192.168.1.193:8000",
    "https://techlearnjess.pythonanywhere.com",
]

# ------------------------------
# URLS
# ------------------------------
ROOT_URLCONF = 'techlearnjess.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_settings',
                'notifications.context_processors.unread_notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'techlearnjess.wsgi.application'

# ------------------------------
# DATABASE
# ------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ------------------------------
# AUTH PASSWORD VALIDATORS
# ------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# ------------------------------
# INTERNATIONALIZATION
# ------------------------------
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Kinshasa'
USE_I18N = True
USE_TZ = True

# ------------------------------
# STATIC FILES
# ------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ------------------------------
# MEDIA FILES
# ------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# ------------------------------
# DEFAULT PRIMARY KEY
# ------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------------------------
# PAYMENT GATEWAYS
# ------------------------------
# PayPal
PAYPAL_TEST = config('PAYPAL_TEST', default=True, cast=bool)
PAYPAL_RECEIVER_EMAIL = config('PAYPAL_RECEIVER_EMAIL')

# Orange Money (placeholders)
ORANGE_MONEY_MERCHANT_KEY = config('ORANGE_MONEY_MERCHANT_KEY', default='YOUR_ORANGE_MONEY_KEY')

# M-PESA (placeholders)
MPESA_SHORT_CODE = config('MPESA_SHORT_CODE', default='YOUR_MPESA_SHORT_CODE')
MPESA_API_KEY = config('MPESA_API_KEY', default='YOUR_MPESA_API_KEY') # C'est la clé API du bac à sable
MPESA_PUBLIC_KEY = config('MPESA_PUBLIC_KEY', default='YOUR_MPESA_PUBLIC_KEY') # La longue clé publique
MPESA_SERVICE_PROVIDER_CODE = config('MPESA_SERVICE_PROVIDER_CODE', default='YOUR_MPESA_SERVICE_PROVIDER_CODE') # Le 000000 de l'exemple

# ------------------------------
# COMPANY INFO & LEGAL
# ------------------------------
COMPANY_NAME = 'Jessna TechLearn'
COMPANY_EMAIL = 'jessnatechlearn@gmail.com'
COMPANY_PHONE = '+243 891 433 419'
COMPANY_ADDRESS = 'Matadi, Kongo Central, RDC'
COMPANY_WEBSITE = 'https://techlearnjess.pythonanywhere.com'

LEGAL_REPRESENTATIVE = 'Chadrack Mbu Jess'
LEGAL_TITLE = 'Fondateur & Directeur Général'
REGISTRATION_NUMBER = 'En cours'
TAX_NUMBER = 'En cours'

HOST_NAME = 'PythonAnywhere'
HOST_ADDRESS = '525 Brannan Street, Suite 300, San Francisco, CA 94107, USA'
HOST_WEBSITE = 'https://pythonanywhere.com'

TERMS_VERSION = '1.0.2'
TERMS_DATE = date(2025, 11, 9)
PRIVACY_POLICY_VERSION = '1.0.2'
PRIVACY_POLICY_DATE = date(2025, 11, 9)
DATA_CONTROLLER = 'Chadrack Mbu Jess'
DATA_PROTECTION_EMAIL = 'jessnatechlearn@gmail.com'
GOVERNING_LAW = 'République Démocratique du Congo'

# ------------------------------
# CRISPY FORMS
# ------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# ------------------------------
# CKEDITOR
# ------------------------------
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 500,
        'width': '100%',
        'enterMode': 2,
        'shiftEnterMode': 1,
        'extraPlugins': ','.join(['floatingspace', 'stylescombo']),
        'stylesSet': [
            {'name': 'Titre de Section', 'element': 'h2', 'attributes': {'class': 'text-2xl font-semibold text-gray-900 mb-4'}},
            { 'name': 'Boîte Bleue', 'element': 'div', 'attributes': {'class': 'info-box'} },
            { 'name': 'Boîte Verte', 'element': 'div', 'attributes': {'class': 'success-box'} },
            { 'name': 'Boîte Jaune', 'element': 'div', 'attributes': {'class': 'warning-box'} },
            { 'name': 'Boîte Rouge', 'element': 'div', 'attributes': {'class': 'error-box'} },
            { 'name': 'Boîte Violette', 'element': 'div', 'attributes': {'class': 'purple-box'} },
            { 'name': 'Boîte Rose', 'element': 'div', 'attributes': {'class': 'pink-box'} },
            { 'name': 'Boîte Grise', 'element': 'div', 'attributes': {'class': 'gray-box'} },
            { 'name': 'Boîte Cyan', 'element': 'div', 'attributes': {'class': 'cyan-box'} },
        ]
    },
}

# ------------------------------
# LOGIN URLS
# ------------------------------
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'core:dashboard'
LOGOUT_REDIRECT_URL = 'core:home'

# ------------------------------
# EMAIL
# ------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ------------------------------
# JITSI (JaaS 8x8)
# ------------------------------
JAAS_APP_ID = config('JAAS_APP_ID', default='vpaas-magic-cookie-d45a7fec84d4476396cc3ddc915840cf')
JAAS_API_KEY = config('JAAS_API_KEY', default='vpaas-magic-cookie-d45a7fec84d4476396cc3ddc915840cf/a31886-SAMPLE_APP')
JAAS_DOMAIN = config('JAAS_DOMAIN', default='8x8.vc')
JAAS_PRIVATE_KEY_PATH = config('JAAS_PRIVATE_KEY_PATH', default=os.path.join(BASE_DIR, 'jaas_private_key.pk'))

# ------------------------------
# SECURITY
# ------------------------------
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
