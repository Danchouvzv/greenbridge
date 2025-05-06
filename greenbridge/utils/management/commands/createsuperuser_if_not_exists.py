"""
Management command to create a superuser if one doesn't exist.
Used in the Docker entrypoint to ensure an admin user is available.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    """
    Django command to create a superuser if one doesn't exist.
    """
    help = 'Creates a superuser if one does not exist'

    def handle(self, *args, **options):
        if User.objects.filter(is_superuser=True).count() == 0:
            username = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@greenbridge.com')
            password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')
            
            self.stdout.write(f'Creating superuser with email: {username}')
            
            admin = User.objects.create_superuser(
                email=username,
                password=password,
                first_name='Admin',
                last_name='User',
                role=User.ADMIN
            )
            
            admin.is_active = True
            admin.email_verified = True
            admin.save()
            
            self.stdout.write(self.style.SUCCESS('Superuser created successfully!'))
        else:
            self.stdout.write('Superuser already exists.') 