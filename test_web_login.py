"""
Test the web login functionality using requests
"""

import requests
from requests.sessions import Session

BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/login"
DASHBOARD_URL = f"{BASE_URL}/dashboard"


def test_web_login():
    """Test the web login functionality"""
    
    # Create a session to maintain cookies
    session = Session()
    
    try:
        print("Testing web login...")
        
        # First get the login page to get CSRF token
        print("Getting login page...")
        login_page = session.get(LOGIN_URL)
        print(f"Login page status: {login_page.status_code}")
        
        # Login data
        login_data = {
            "login_identifier": "admin",
            "password": "Admin@2025!"
        }
        
        # Attempt login
        print("Attempting login...")
        response = session.post(LOGIN_URL, data=login_data, allow_redirects=False)
        
        print(f"Login response status: {response.status_code}")
        print(f"Login response headers: {dict(response.headers)}")
        
        if response.status_code == 302:  # Redirect indicates successful login
            redirect_location = response.headers.get('Location', '')
            print(f"✅ Login successful! Redirecting to: {redirect_location}")
            
            # Try to access dashboard
            dashboard_response = session.get(DASHBOARD_URL)
            print(f"Dashboard access status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("✅ Dashboard accessible after login!")
                if "Welcome, admin" in dashboard_response.text:
                    print("✅ User logged in correctly - welcome message found!")
                else:
                    print("⚠️ Dashboard loaded but welcome message not found")
            else:
                print("❌ Dashboard not accessible after login")
                
        else:
            print(f"❌ Login failed! Status: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure the Flask app is running.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == '__main__':
    test_web_login()
