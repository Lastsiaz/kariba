from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Sets admin06 role to admin'

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username='admin06')
            user_profile = UserProfile.objects.get(user=user)
            user_profile.role = 'admin'
            user_profile.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully set {user.username}\'s role to admin'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User admin06 does not exist'))
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR('User profile for admin06 does not exist')) 