"""
Management command to create a default admin user.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates a default admin user if one does not exist'

    def handle(self, *args, **options):
        email = 'admin@lms.com'
        password = 'admin7564'
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin user "{email}" already exists.')
            )
            return
        
        User.objects.create_superuser(
            email=email,
            password=password,
            first_name='Admin',
            last_name='User'
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created admin user: {email}')
        )
