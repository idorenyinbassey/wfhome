"""
Database User Management Script
This script deletes all existing users and creates a new admin user.
Use with caution as this will permanently delete all user data!
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Task
from datetime import datetime

def delete_all_users_and_create_admin():
    """Delete all users from database and create a new admin user."""
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            print("Starting user database cleanup...")
            
            # First, delete all tasks (to avoid foreign key constraints)
            tasks_count = Task.query.count()
            if tasks_count > 0:
                print(f"Deleting {tasks_count} tasks...")
                Task.query.delete()
                db.session.commit()
                print(f"✓ Deleted {tasks_count} tasks")
            
            # Delete all users
            users_count = User.query.count()
            if users_count > 0:
                print(f"Deleting {users_count} users...")
                User.query.delete()
                db.session.commit()
                print(f"✓ Deleted {users_count} users")
            else:
                print("No users found to delete")
            
            # Create new admin user
            print("\nCreating new admin user...")
            
            admin_user = User(
                username='admin',
                email='admin@wfhome.com',
                first_name='System',
                last_name='Administrator',
                department='IT',
                is_admin=True,
                status='active',
                date_created=datetime.utcnow()
            )
            
            # Set a strong default password (should be changed after first login)
            admin_password = 'Admin@123!'
            admin_user.set_password(admin_password)
            
            # Add to database
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"✓ Created new admin user:")
            print(f"   Username: {admin_user.username}")
            print(f"   Email: {admin_user.email}")
            print(f"   Password: {admin_password}")
            print(f"   Admin privileges: {admin_user.is_admin}")
            print(f"\n⚠️  IMPORTANT: Please change the admin password after first login!")
            
        except Exception as e:
            print(f"❌ Error occurred: {str(e)}")
            db.session.rollback()
            return False
    
    return True

def create_sample_users():
    """Optional: Create some sample users for testing."""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("\nCreating sample users for testing...")
            
            # Sample users data
            sample_users = [
                {
                    'username': 'john_doe',
                    'email': 'john.doe@wfhome.com',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'department': 'Marketing',
                    'password': 'Password123!'
                },
                {
                    'username': 'jane_smith',
                    'email': 'jane.smith@wfhome.com',
                    'first_name': 'Jane',
                    'last_name': 'Smith',
                    'department': 'HR',
                    'password': 'Password123!'
                },
                {
                    'username': 'manager_user',
                    'email': 'manager@wfhome.com',
                    'first_name': 'Mike',
                    'last_name': 'Manager',
                    'department': 'Operations',
                    'password': 'Manager123!',
                    'is_admin': False  # Regular user but could be made manager
                }
            ]
            
            for user_data in sample_users:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    department=user_data['department'],
                    is_admin=user_data.get('is_admin', False),
                    status='active',
                    date_created=datetime.utcnow()
                )
                
                user.set_password(user_data['password'])
                db.session.add(user)
            
            db.session.commit()
            
            print(f"✓ Created {len(sample_users)} sample users")
            for user_data in sample_users:
                print(f"   - {user_data['username']} ({user_data['email']})")
            
        except Exception as e:
            print(f"❌ Error creating sample users: {str(e)}")
            db.session.rollback()
            return False
    
    return True

def verify_admin_user():
    """Verify that the admin user was created successfully."""
    
    app = create_app()
    
    with app.app_context():
        try:
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print(f"\n✅ Admin user verification successful:")
                print(f"   ID: {admin.id}")
                print(f"   Username: {admin.username}")
                print(f"   Email: {admin.email}")
                print(f"   Full Name: {admin.first_name} {admin.last_name}")
                print(f"   Department: {admin.department}")
                print(f"   Is Admin: {admin.is_admin}")
                print(f"   Status: {admin.status}")
                print(f"   Created: {admin.date_created}")
                
                # Test password
                if admin.check_password('Admin@123!'):
                    print(f"   ✓ Password verification successful")
                else:
                    print(f"   ❌ Password verification failed")
                
                return True
            else:
                print("❌ Admin user not found!")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying admin user: {str(e)}")
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("WFHOME DATABASE USER MANAGEMENT")
    print("=" * 60)
    print("⚠️  WARNING: This will delete ALL existing users and tasks!")
    print("⚠️  Make sure you have a backup if needed.")
    print("=" * 60)
    
    # Ask for confirmation
    confirmation = input("\nDo you want to proceed? Type 'YES' to confirm: ")
    
    if confirmation.upper() == 'YES':
        print("\n" + "=" * 60)
        
        # Delete users and create admin
        if delete_all_users_and_create_admin():
            print("\n" + "-" * 60)
            
            # Verify admin creation
            verify_admin_user()
            
            # Ask if user wants sample users
            create_samples = input("\nDo you want to create sample users for testing? (y/n): ")
            if create_samples.lower() in ['y', 'yes']:
                create_sample_users()
            
            print("\n" + "=" * 60)
            print("✅ DATABASE MANAGEMENT COMPLETED SUCCESSFULLY!")
            print("✅ You can now login with the admin credentials shown above.")
            print("⚠️  Remember to change the admin password after first login!")
            print("=" * 60)
        else:
            print("\n❌ Database management failed!")
    else:
        print("\n❌ Operation cancelled by user.")
        print("No changes were made to the database.")
