"""
Development settings for GreenBridge project.
"""
import os
from pathlib import Path

from .base import *  # noqa

# Development mode
DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-development-key-change-in-production')
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.contrib.gis.db.backends.postgis'),
        'NAME': os.environ.get('DB_NAME', 'greenbridge'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 0,
    }
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'greenbridge-dev-cache',
    }
}

# Development-specific apps
INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
]

# Add debug toolbar middleware
MIDDLEWARE.insert(
    MIDDLEWARE.index('django.middleware.common.CommonMiddleware') + 1,
    'debug_toolbar.middleware.DebugToolbarMiddleware'
)

# Debug toolbar settings
INTERNAL_IPS = ['127.0.0.1', '::1']
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
}

# Email Backend in development - output to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable throttling in development
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': None,
    'user': None,
    'uploads': None,
}

# Make celery execute tasks synchronously in development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Set to True if using runserver_plus with HTTPS
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Django Extensions settings
SHELL_PLUS = "ipython"
SHELL_PLUS_PRINT_SQL = True
SHELL_PLUS_IMPORTS = [
    'from django.core.cache import cache',
    'from django.conf import settings',
    'from django.contrib.auth.models import Group, Permission',
    'from django.contrib.contenttypes.models import ContentType',
    'from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When',
    'from django.utils import timezone',
    'from greenbridge.accounts.models import User, Organization',
]

# Notebook settings
NOTEBOOK_ARGUMENTS = [
    '--ip', '0.0.0.0',
    '--port', '8888',
    '--allow-root',
    '--no-browser',
]

# Disable Content Security Policy in development
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'")

# Disable security checks in development
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False

# Add media root to static files dirs for easier testing
STATICFILES_DIRS += [
    os.path.join(BASE_DIR, 'media'),
]

# Debug logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',  # Change to 'DEBUG' to see SQL queries
            'propagate': False,
        },
        'greenbridge': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
} 