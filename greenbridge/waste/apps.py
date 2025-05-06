"""
Django app configuration for the Waste Management app.
"""
from django.apps import AppConfig


class WasteConfig(AppConfig):
    """Configuration for the waste management app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'greenbridge.waste'
    verbose_name = 'Waste Management'