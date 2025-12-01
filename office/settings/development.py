from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000", "https://office-management-cj00.onrender.com", "https://office.arakkha.tech"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_ROOT = BASE_DIR / "media"
STATIC_ROOT = BASE_DIR / "staticfiles"
