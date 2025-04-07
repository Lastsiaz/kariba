from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Updates a user\'s role and department'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user to update')
        parser.add_argument('role', type=str, help='New role (admin, analyst, marketer, researcher, general_user)')

    def handle(self, *args, **options):
        username = options['username']
        role = options['role']
        
        # Validate role
        valid_roles = ['admin', 'analyst', 'marketer', 'researcher', 'general_user']
        if role not in valid_roles:
            self.stdout.write(
                self.style.ERROR(f'Invalid role. Must be one of: {", ".join(valid_roles)}')
            )
            return
        
        try:
            user = User.objects.get(username=username)
            profile = UserProfile.objects.get(user=user)
            
            # Update role
            profile.role = role
            
            # Set department based on role
            if role == 'admin':
                profile.department = 'Administration'
            elif role == 'analyst':
                profile.department = 'Data Analytics'
            elif role == 'marketer':
                profile.department = 'Marketing'
            elif role == 'researcher':
                profile.department = 'Research'
            else:
                profile.department = 'General'
            
            profile.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {username}\'s role to {role} and department to {profile.department}')
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User {username} does not exist')
            )
        except UserProfile.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User {username} has no profile')
            ) 