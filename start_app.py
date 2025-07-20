"""
Test the Flask application with the new admin user.
This script starts the development server.
"""

from app import create_app

if __name__ == '__main__':
    app = create_app()
    
    print("="*60)
    print("WFHOME APPLICATION STARTING")
    print("="*60)
    print("Admin credentials:")
    print("Username: admin")
    print("Email: admin@wfhome.com") 
    print("Password: Admin@2025!")
    print("="*60)
    print("Application will be available at: http://127.0.0.1:5000")
    print("Admin panel will be available at: http://127.0.0.1:5000/admin")
    print("="*60)
    
    app.run(debug=True, host='127.0.0.1', port=5000)
