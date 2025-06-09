#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/c%3A/Users/Last%20Siakanya/Desktop/kariba')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kariba.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

def check_user_roles():
    """Check all users and their roles"""
    print("=== User Role Check ===")
    print("Username | Role | Department | Is Admin | Is Analyst | Is Marketer | Is Researcher")
    print("-" * 80)
    
    users = User.objects.all()
    for user in users:
        try:
            profile = user.userprofile
            print(f"{user.username:15} | {profile.role:10} | {profile.department:15} | {profile.is_admin:8} | {profile.is_analyst:9} | {profile.is_marketer:10} | {profile.is_researcher:11}")
        except UserProfile.DoesNotExist:
            print(f"{user.username:15} | NO PROFILE | {'N/A':15} | {'N/A':8} | {'N/A':9} | {'N/A':10} | {'N/A':11}")
    
    print("\n=== Role Summary ===")
    profiles = UserProfile.objects.all()
    role_counts = {}
    for profile in profiles:
        role_counts[profile.role] = role_counts.get(profile.role, 0) + 1
    
    for role, count in role_counts.items():
        print(f"{role}: {count} users")

if __name__ == "__main__":
    check_user_roles() 