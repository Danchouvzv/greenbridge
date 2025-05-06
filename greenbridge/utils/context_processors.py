"""
Context processors for the GreenBridge application.
These processors add context variables to all template renders.
"""
from django.conf import settings


def settings_context(request):
    """
    Adds useful settings to the template context.
    """
    return {
        'DEBUG': settings.DEBUG,
        'SITE_NAME': 'GreenBridge',
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
    } 