from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Checks user roles'

    def handle(self, *args, **options):
        # Get all users
        users = User.objects.all()
        
        for user in users:
            try:
                user_profile = UserProfile.objects.get(user=user)
                self.stdout.write(self.style.SUCCESS(f'User: {user.username}, Current Role: {user_profile.role}'))
            except UserProfile.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'No profile found for user: {user.username}')) 