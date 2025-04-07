from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Fixes users with marketer email but researcher role'

    def handle(self, *args, **options):
        # Find users with marketer email but researcher role
        users = User.objects.filter(email__icontains='marketer')
        fixed_count = 0
        
        for user in users:
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.role == 'researcher':
                    profile.role = 'marketer'
                    profile.department = 'Marketing'
                    profile.save()
                    fixed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Fixed user {user.username} (email: {user.email}) - Changed role from researcher to marketer')
                    )
            except UserProfile.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'User {user.username} (email: {user.email}) has no profile')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Fixed {fixed_count} users with marketer email but researcher role')
        ) 