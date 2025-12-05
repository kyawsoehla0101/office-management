from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = [
    "office-management-cj00.onrender.com",
    "office.arakkha.tech"
]

CSRF_TRUSTED_ORIGINS = [
    "https://office-management-cj00.onrender.com",
    "https://office.arakkha.tech",
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get("DB_NAME", "defaultdb"),
        'USER': os.environ.get("DB_USER", "doadmin"),
        'PASSWORD': os.environ.get("DB_PASSWORD"),
        'HOST': os.environ.get("DB_HOST"),
        'PORT': os.environ.get("DB_PORT", "25060"),
        'OPTIONS': {
            'ssl_mode': 'REQUIRED',
        },
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': os.environ.get("DB_NAME", "defaultdb"),
#         'USER': os.environ.get("DB_USER", "avnadmin"),
#         'PASSWORD': os.environ.get("DB_PASSWORD"),
#         'HOST': os.environ.get("DB_HOST"),
#         'PORT': os.environ.get("DB_PORT", "25741"),
#         'OPTIONS': {
#             'ssl_mode': 'REQUIRED',
#         },
#     }
# }

STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"