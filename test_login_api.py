"""
Test the API login functionality
"""

import requests
import json

# API endpoint
BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"

def test_login():
    """Test the login API endpoint"""
    
    # Admin credentials we created
    login_data = {
        "username": "admin",
        "password": "Admin@2025!"
    }
    
    try:
        print("Testing login API...")
        print(f"URL: {LOGIN_URL}")
        print(f"Data: {login_data}")
        
        # Make the request
        response = requests.post(LOGIN_URL, json=login_data)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Login successful!")
            print(f"Token: {data.get('token', 'No token')}")
            print(f"User: {data.get('user', 'No user info')}")
        else:
            print(f"\n❌ Login failed!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure the Flask app is running.")
        print("Run: python run.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    test_login()
