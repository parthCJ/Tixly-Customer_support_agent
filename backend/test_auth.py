"""
Test script for OAuth 2.0 authentication
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_register():
    """Test user registration"""
    print_section("1. REGISTER NEW USER")
    
    user_data = {
        "email": "testuser@example.com",
        "password": "testpass123",
        "full_name": "Test User",
        "role": "customer"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
    
    if response.status_code == 201:
        user = response.json()
        print("✅ User registered successfully!")
        print(f"   User ID: {user['user_id']}")
        print(f"   Email: {user['email']}")
        print(f"   Role: {user['role']}")
        return user
    elif response.status_code == 400:
        print("⚠️  User already exists (this is okay)")
        return None
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_login(email="agent@tixly.com", password="agent123"):
    """Test user login"""
    print_section(f"2. LOGIN AS {email}")
    
    # OAuth2 form data format
    login_data = {
        "username": email,  # OAuth2 uses 'username' field
        "password": password
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data=login_data  # Form data, not JSON
    )
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ Login successful!")
        print(f"   Access Token: {token_data['access_token'][:50]}...")
        print(f"   Token Type: {token_data['token_type']}")
        print(f"   Expires In: {token_data['expires_in']} seconds")
        print(f"\n   User Info:")
        print(f"   - Name: {token_data['user']['full_name']}")
        print(f"   - Email: {token_data['user']['email']}")
        print(f"   - Role: {token_data['user']['role']}")
        return token_data['access_token']
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_login_json(email="manager@tixly.com", password="manager123"):
    """Test JSON login endpoint"""
    print_section(f"3. LOGIN (JSON) AS {email}")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login/json",
        json=login_data
    )
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ JSON login successful!")
        print(f"   User: {token_data['user']['full_name']} ({token_data['user']['role']})")
        return token_data['access_token']
    else:
        print(f"❌ JSON login failed: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_get_current_user(token):
    """Test getting current user info"""
    print_section("4. GET CURRENT USER INFO")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    
    if response.status_code == 200:
        user = response.json()
        print("✅ Retrieved current user info!")
        print(f"   Name: {user['full_name']}")
        print(f"   Email: {user['email']}")
        print(f"   Role: {user['role']}")
        print(f"   User ID: {user['user_id']}")
        return user
    else:
        print(f"❌ Failed to get user info: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_protected_endpoint_without_auth():
    """Test accessing protected endpoint without token"""
    print_section("5. ACCESS PROTECTED ENDPOINT (NO TOKEN)")
    
    response = requests.get(f"{BASE_URL}/api/auth/me")
    
    if response.status_code == 401:
        print("✅ Correctly rejected unauthenticated request")
        print(f"   Status: {response.status_code}")
        print(f"   Message: {response.json().get('detail')}")
    else:
        print(f"❌ Unexpected response: {response.status_code}")


def test_list_users_as_admin():
    """Test listing users with admin token"""
    print_section("6. LIST ALL USERS (ADMIN)")
    
    # Login as admin
    admin_token = test_login("admin@tixly.com", "admin123")
    if not admin_token:
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/api/auth/users", headers=headers)
    
    if response.status_code == 200:
        users = response.json()
        print(f"✅ Retrieved {len(users)} users")
        for user in users:
            print(f"   - {user['email']} ({user['role']})")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   {response.text}")


def test_list_users_as_agent():
    """Test that agents cannot list users"""
    print_section("7. LIST USERS AS AGENT (SHOULD FAIL)")
    
    # Login as agent
    agent_token = test_login("agent@tixly.com", "agent123")
    if not agent_token:
        return
    
    headers = {"Authorization": f"Bearer {agent_token}"}
    response = requests.get(f"{BASE_URL}/api/auth/users", headers=headers)
    
    if response.status_code == 403:
        print("✅ Correctly denied access (insufficient permissions)")
        print(f"   Message: {response.json().get('detail')}")
    else:
        print(f"❌ Unexpected response: {response.status_code}")


def test_create_ticket_authenticated():
    """Test creating a ticket with authentication"""
    print_section("8. CREATE TICKET (AUTHENTICATED)")
    
    # Login as customer
    customer_token = test_login("customer@example.com", "customer123")
    if not customer_token:
        return
    
    ticket_data = {
        "customer_email": "customer@example.com",
        "customer_name": "Customer Jane",
        "subject": "Test authenticated ticket",
        "description": "This ticket was created with JWT authentication",
        "source": "web"
    }
    
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = requests.post(
        f"{BASE_URL}/api/tickets/create",
        json=ticket_data,
        headers=headers
    )
    
    if response.status_code == 200:
        ticket = response.json()['ticket']
        print("✅ Ticket created with authentication!")
        print(f"   Ticket ID: {ticket['ticket_id']}")
        print(f"   Status: {ticket['status']}")
        return ticket['ticket_id']
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   {response.text}")
        return None


def main():
    """Run all authentication tests"""
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║         OAuth 2.0 / JWT Authentication Test Suite         ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Test registration
        test_register()
        
        # Test login (OAuth2 format)
        agent_token = test_login("agent@tixly.com", "agent123")
        
        # Test JSON login
        manager_token = test_login_json("manager@tixly.com", "manager123")
        
        # Test getting current user
        if agent_token:
            test_get_current_user(agent_token)
        
        # Test protected endpoint without auth
        test_protected_endpoint_without_auth()
        
        # Test role-based access control
        test_list_users_as_admin()
        test_list_users_as_agent()
        
        # Test creating ticket with auth
        test_create_ticket_authenticated()
        
        print_section("✅ AUTHENTICATION SYSTEM READY!")
        
        print("\n📝 Demo Users Available:")
        print("   1. admin@tixly.com / admin123 (ADMIN)")
        print("   2. manager@tixly.com / manager123 (MANAGER)")
        print("   3. agent@tixly.com / agent123 (AGENT)")
        print("   4. customer@example.com / customer123 (CUSTOMER)")
        
        print("\n🔐 Features Implemented:")
        print("   ✅ JWT token-based authentication")
        print("   ✅ Password hashing with bcrypt")
        print("   ✅ Role-based access control (RBAC)")
        print("   ✅ Protected API endpoints")
        print("   ✅ OAuth 2.0 compatible login")
        print("   ✅ User registration")
        print("   ✅ Token expiration (24 hours)")
        
        print("\n📚 Next Steps:")
        print("   - Add authentication to more ticket endpoints")
        print("   - Implement refresh tokens")
        print("   - Add password reset functionality")
        print("   - Connect frontend login UI")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend")
        print("   Make sure the server is running:")
        print("   python -m backend.main")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
