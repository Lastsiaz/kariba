from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Updates a user\'s role to researcher'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to update')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            user_profile = UserProfile.objects.get(user=user)
            user_profile.role = 'researcher'
            user_profile.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {username}\'s role to researcher'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist'))
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User profile for {username} does not exist')) 