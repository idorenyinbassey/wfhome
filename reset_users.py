"""
Simple script to delete all users and create a new admin user.
Run this script from the project root directory.
"""

from app import create_app
from models import db, User, Task
from datetime import datetime


def reset_database_users():
    """Reset all users and create new admin."""
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        print("Starting database user reset...")
        
        try:
            # Delete all tasks first (foreign key constraints)
            print("Deleting all tasks...")
            Task.query.delete()
            
            # Delete all users
            print("Deleting all users...")
            User.query.delete()
            
            # Create new admin user
            print("Creating new admin user...")
            admin = User(
                username='admin',
                email='admin@wfhome.com',
                first_name='System',
                last_name='Administrator',
                department='IT',
                is_admin=True,
                status='active'
            )
            
            # Set password
            admin.set_password('Admin@2025!')
            
            # Save to database
            db.session.add(admin)
            db.session.commit()
            
            print("\n" + "="*50)
            print("SUCCESS! New admin user created:")
            print("="*50)
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print("Password: Admin@2025!")
            print("Admin: Yes")
            print("="*50)
            print("IMPORTANT: Change password after first login!")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            db.session.rollback()


if __name__ == '__main__':
    reset_database_users()
