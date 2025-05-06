"""
WSGI config for GreenBridge project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set the settings module based on environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenbridge.settings.production')

# Get the WSGI application
application = get_wsgi_application() 