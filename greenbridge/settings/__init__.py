"""
Settings initialization module for GreenBridge project.
"""
import os

# Default to development settings
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')

if not settings_module or settings_module == 'greenbridge.settings':
    from .development import *  # noqa 