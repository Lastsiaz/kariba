import os
import django
from pymongo import MongoClient
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentiment_analysis_system.settings')
django.setup()

def view_users():
    # Get MongoDB connection settings from Django settings
    client = MongoClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    
    # Get the users collection
    users_collection = db['users']
    
    print("\nUser Records in MongoDB:")
    print("-" * 50)
    
    # Find all users
    users = users_collection.find()
    
    for user in users:
        print(f"\nUsername/Email: {user.get('username', 'N/A')}")
        print(f"First Name: {user.get('first_name', 'N/A')}")
        print(f"Last Name: {user.get('last_name', 'N/A')}")
        print(f"Role: {user.get('role', 'N/A')}")
        print(f"Is Active: {user.get('is_active', False)}")
        print(f"Date Joined: {user.get('date_joined', 'N/A')}")
        print("-" * 30)

if __name__ == '__main__':
    view_users() 