from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Fixes user departments based on their roles'

    def handle(self, *args, **options):
        # Get all user profiles
        profiles = UserProfile.objects.all()
        
        # Counter for updated profiles
        updated_count = 0
        
        # Ensure all users have the correct department based on their role
        for profile in profiles:
            original_department = profile.department
            if profile.role == 'admin' and profile.department != 'Administration':
                profile.department = 'Administration'
                profile.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'Updated {profile.user.username} department from {original_department} to Administration'))
            elif profile.role == 'analyst' and profile.department != 'Data Analytics':
                profile.department = 'Data Analytics'
                profile.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'Updated {profile.user.username} department from {original_department} to Data Analytics'))
            elif profile.role == 'marketer' and profile.department != 'Marketing':
                profile.department = 'Marketing'
                profile.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'Updated {profile.user.username} department from {original_department} to Marketing'))
            elif profile.role == 'researcher' and profile.department != 'Research':
                profile.department = 'Research'
                profile.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'Updated {profile.user.username} department from {original_department} to Research'))
            elif profile.role == 'general_user' and profile.department != 'General':
                profile.department = 'General'
                profile.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'Updated {profile.user.username} department from {original_department} to General'))
        
        # Count users by role
        total_users = User.objects.count()
        total_analysts = UserProfile.objects.filter(role='analyst').count()
        total_marketers = UserProfile.objects.filter(role='marketer').count()
        total_researchers = UserProfile.objects.filter(role='researcher').count()
        
        self.stdout.write(self.style.SUCCESS(f'Updated {updated_count} user profiles'))
        self.stdout.write(self.style.SUCCESS(f'Total users: {total_users}'))
        self.stdout.write(self.style.SUCCESS(f'Total analysts: {total_analysts}'))
        self.stdout.write(self.style.SUCCESS(f'Total marketers: {total_marketers}'))
        self.stdout.write(self.style.SUCCESS(f'Total researchers: {total_researchers}')) 