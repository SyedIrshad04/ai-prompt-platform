import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-production-abc123xyz')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        'CSRF_TRUSTED_ORIGINS',
        'https://*.railway.app,https://*.render.com'
    ).split(',')
    if origin.strip()
]

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'corsheaders',
    'apps.prompts',
    'apps.tags',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# DATABASE_URL takes precedence (Railway, Render, Heroku style)
# Falls back to individual DB_* vars for local Docker usage
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    import urllib.parse as _urlparse
    _u = _urlparse.urlparse(DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql',
            'NAME':     _u.path.lstrip('/'),
            'USER':     _u.username,
            'PASSWORD': _u.password,
            'HOST':     _u.hostname,
            'PORT':     str(_u.port or 5432),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql',
            'NAME':     os.getenv('DB_NAME', 'promptdb'),
            'USER':     os.getenv('DB_USER', 'promptuser'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'promptpass'),
            'HOST':     os.getenv('DB_HOST', 'db'),
            'PORT':     os.getenv('DB_PORT', '5432'),
        }
    }

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True   # Tighten via CORS_ALLOWED_ORIGINS in production
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:4200,http://localhost:80').split(',')
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']
CORS_ALLOW_HEADERS = ['accept', 'authorization', 'content-type', 'origin', 'x-requested-with']

JWT_SECRET = os.getenv('JWT_SECRET', SECRET_KEY)
JWT_EXPIRY_HOURS = int(os.getenv('JWT_EXPIRY_HOURS', '24'))

import logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
