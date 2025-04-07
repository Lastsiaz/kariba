from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Lists all users and their roles'

    def handle(self, *args, **options):
        self.stdout.write('Users and their roles:')
        for user in User.objects.all():
            try:
                profile = UserProfile.objects.get(user=user)
                self.stdout.write(
                    f'{user.username}: {user.email} - Role: {profile.role}, Department: {profile.department}'
                )
            except UserProfile.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'{user.username}: {user.email} - No profile')
                ) 