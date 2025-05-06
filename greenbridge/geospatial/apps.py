"""
Django app configuration for the Geospatial app.
"""
from django.apps import AppConfig


class GeospatialConfig(AppConfig):
    """Configuration for the geospatial app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'greenbridge.geospatial'
    verbose_name = 'Geospatial Services' 