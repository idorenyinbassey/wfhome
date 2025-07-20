"""
Verification script to check the admin user in the database.
"""

from app import create_app
from models import db, User


def verify_admin():
    """Verify the admin user exists and can login."""
    
    app = create_app()
    
    with app.app_context():
        # Find the admin user
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            print("Admin user found!")
            print(f"ID: {admin.id}")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Full Name: {admin.first_name} {admin.last_name}")
            print(f"Department: {admin.department}")
            print(f"Is Admin: {admin.is_admin}")
            print(f"Status: {admin.status}")
            print(f"Date Created: {admin.date_created}")
            
            # Test password
            if admin.check_password('Admin@2025!'):
                print("✅ Password verification: SUCCESS")
            else:
                print("❌ Password verification: FAILED")
            
            # Check total users
            total_users = User.query.count()
            print(f"\nTotal users in database: {total_users}")
            
        else:
            print("❌ Admin user not found!")


if __name__ == '__main__':
    verify_admin()
