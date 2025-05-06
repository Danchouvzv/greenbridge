"""
Django app configuration for the Accounts app.
"""
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuration for the accounts app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'greenbridge.accounts'
    verbose_name = 'User Accounts'

    def ready(self):
        """Initialize app when ready."""
        try:
            import greenbridge.accounts.signals  # noqa
        except ImportError:
            pass 