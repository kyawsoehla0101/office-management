from pathlib import Path
import os
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", get_random_secret_key())

DEBUG = False

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    "set.apps.SetConfig",
    'base',
    'accounts',
    'het',
    'training',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    "accounts.middleware.OfficeDeviceMiddleware",
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'accounts.middleware.DynamicSessionTimeoutMiddleware',
    # Device restriction middleware

]

ROOT_URLCONF = 'office.urls'
AUTH_USER_MODEL = "accounts.CustomUser"

LOGIN_URL = "login"
LOGOUT_REDIRECT_URL = "login"
LOGIN_REDIRECT_URL = "post_login_redirect"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'office.wsgi.application'

AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailOrUsernameBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Yangon'
USE_I18N = True
USE_TZ = True

# Static still served by WhiteNoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

