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
from users.forms import AdminUserRegistrationForm

def test_user_creation():
    """Test creating a user to ensure no unique constraint errors"""
    print("Testing user creation...")
    
    # Test data
    test_data = {
        'username': 'testuser123',
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password1': 'A1b2c3d4e5f6',
        'password2': 'A1b2c3d4e5f6',
        'role': 'analyst',
        'department': 'Data Analytics'
    }
    
    try:
        # Check if user already exists
        if User.objects.filter(username=test_data['username']).exists():
            print(f"User {test_data['username']} already exists, skipping test.")
            return True
            
        # Create form and validate
        form = AdminUserRegistrationForm(test_data)
        if form.is_valid():
            print("Form is valid, creating user...")
            user = form.save()
            print(f"User created successfully: {user.username}")
            
            # Verify UserProfile was created correctly
            profile = user.userprofile
            print(f"UserProfile created: role={profile.role}, department={profile.department}")
            
            # Clean up - delete the test user
            user.delete()
            print("Test user deleted successfully.")
            
            return True
        else:
            print("Form validation failed:")
            for field, errors in form.errors.items():
                print(f"  {field}: {errors}")
            return False
            
    except Exception as e:
        print(f"Error during user creation: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_user_creation()
    if success:
        print("✅ User creation test passed!")
    else:
        print("❌ User creation test failed!") 