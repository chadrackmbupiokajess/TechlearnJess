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
    '192.168.27.241',
    'techlearnjess.pythonanywhere.com',

]

# ------------------------------
# APPLICATIONS
# ------------------------------
INSTALLED_APPS = [
    # Django apps
    'django.contrib.sites', # Moved up as per allauth recommendation
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third party apps
    'crispy_forms',
    'crispy_tailwind',
    'ckeditor',
    'ckeditor_uploader',
    'corsheaders',
    'django_countries',
    'paypal.standard.ipn',

    # Allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

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
# AUTHENTICATION BACKENDS
# ------------------------------
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

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
    'allauth.account.middleware.AccountMiddleware', # Added for allauth
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
                # `allauth` context processors are NOT needed here.
                # They are automatically added by allauth's middleware.
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
# ALLAUTH SETTINGS
# ------------------------------
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none' # Changed from 'mandatory' to 'none'
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_USERNAME_REQUIRED = False # Set to True if you want users to have a username
# SOCIALACCOUNT_LOGIN_BY_CODE = True # Removed as it might interfere with auto-signup
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none' # Added to skip email verification for social accounts
SOCIALACCOUNT_AUTO_SIGNUP = True # Added to automatically sign up social accounts
ACCOUNT_SIGNUP_REDIRECT_URL = 'core:dashboard' # Added for explicit signup redirection
# SOCIALACCOUNT_ADAPTER = 'accounts.adapters.MySocialAccountAdapter' # Removed custom adapter

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID'),
            'secret': config('GOOGLE_CLIENT_SECRET'),
            'key': '' # leave empty
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# ------------------------------
# LOGIN URLS
# ------------------------------
LOGIN_URL = 'accounts:login' # You might want to change this to 'account_login' from allauth
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

# ------------------------------
# IMPORTANT: ALLAUTH SITE CONFIGURATION
# ------------------------------
# For allauth to work correctly, especially with social logins,
# you MUST ensure that your Django Site configuration in the admin panel
# (http://127.0.0.1:8000/admin/sites/site/) is correctly set.
# The 'Domain name' and 'Display name' should match your application's domain.
# For local development, this is typically '127.0.0.1:8000' or 'localhost:8000'.
# If this is incorrect, allauth will often return 'Unauthorized' errors.
