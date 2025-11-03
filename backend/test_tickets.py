# Test script to create sample tickets
import requests
import time

# Base URL
BASE_URL = "http://localhost:8000"

# Sample tickets covering different scenarios
sample_tickets = [
    {
        "customer_email": "john.doe@example.com",
        "customer_name": "John Doe",
        "subject": "Order #2021 hasn't shipped yet",
        "description": "My order #2021 was placed a week ago but the tracking still shows 'processing'. Can you check what's going on?",
        "order_id": "2021",
        "source": "web"
    },
    {
        "customer_email": "jane.smith@example.com",
        "customer_name": "Jane Smith",
        "subject": "Double charged for subscription",
        "description": "I was charged $49.99 twice on November 1st for my monthly subscription. I should only be charged once.",
        "source": "email"
    },
    {
        "customer_email": "bob.wilson@example.com",
        "customer_name": "Bob Wilson",
        "subject": "Cannot login to my account",
        "description": "After resetting my password, I still can't login. The system says 'invalid credentials' but I'm sure my password is correct.",
        "source": "chat"
    },
    {
        "customer_email": "alice.johnson@example.com",
        "customer_name": "Alice Johnson",
        "subject": "Product arrived damaged",
        "description": "Order #3456 arrived today but the item is damaged. The box was dented and the product inside is cracked. I'd like a replacement or refund.",
        "order_id": "3456",
        "source": "web"
    },
    {
        "customer_email": "mike.brown@example.com",
        "customer_name": "Mike Brown",
        "subject": "How do I cancel my subscription?",
        "description": "I want to cancel my premium subscription but can't find the option in my account settings.",
        "source": "web"
    }
]


def test_ticket_creation():
    """Test creating multiple tickets"""
    print("🎯 Testing Ticket Creation Workflow\n")
    print("="*60)
    
    created_tickets = []
    
    for i, ticket_data in enumerate(sample_tickets, 1):
        print(f"\n📝 Creating Ticket {i}/{len(sample_tickets)}")
        print(f"   Subject: {ticket_data['subject']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/tickets/create",
                json=ticket_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                ticket = result['ticket']
                
                print(f"   ✅ Created: {ticket['ticket_id']}")
                print(f"   Customer: {ticket['customer_email']}")
                print(f"   Status: {ticket['status']}")
                print(f"   Priority: {ticket['priority']}")
                
                created_tickets.append(ticket['ticket_id'])
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Cannot connect to server!")
            print("   Make sure the server is running: python backend/main.py")
            return
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        time.sleep(0.5)  # Small delay between requests
    
    print("\n" + "="*60)
    print(f"\n✨ Created {len(created_tickets)} tickets successfully!\n")
    
    # List all tickets
    print("📋 Retrieving all tickets...")
    try:
        response = requests.get(f"{BASE_URL}/api/tickets/")
        if response.status_code == 200:
            tickets = response.json()
            print(f"   Found {len(tickets)} total tickets\n")
            
            for ticket in tickets[:3]:  # Show first 3
                print(f"   • {ticket['ticket_id']}: {ticket['subject']}")
    except Exception as e:
        print(f"   ❌ Error listing tickets: {str(e)}")


def test_single_ticket():
    """Test creating and retrieving a single ticket"""
    print("\n🔍 Testing Single Ticket Flow\n")
    print("="*60)
    
    ticket_data = {
        "customer_email": "test@example.com",
        "customer_name": "Test User",
        "subject": "Test ticket",
        "description": "This is a test ticket to verify the system works",
        "source": "test"
    }
    
    print("\n1️⃣ Creating ticket...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/tickets/create",
            json=ticket_data
        )
        
        if response.status_code == 200:
            result = response.json()
            ticket_id = result['ticket']['ticket_id']
            print(f"   ✅ Created: {ticket_id}\n")
            
            # Retrieve the ticket
            print(f"2️⃣ Retrieving ticket {ticket_id}...")
            response = requests.get(f"{BASE_URL}/api/tickets/{ticket_id}")
            
            if response.status_code == 200:
                ticket = response.json()
                print("   ✅ Retrieved successfully!")
                print(f"   Subject: {ticket['subject']}")
                print(f"   Status: {ticket['status']}")
                print(f"   Created: {ticket['created_at']}")
            else:
                print(f"   ❌ Error: {response.status_code}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")


def check_server_health():
    """Check if server is running"""
    print("🏥 Checking server health...\n")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Server is healthy!\n")
            return True
        else:
            print("   ⚠️  Server responded but might have issues\n")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to server!")
        print("   Please start the server: python backend/main.py\n")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}\n")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  Customer Support Copilot - Ticket Creation Tests")
    print("="*60 + "\n")
    
    # Check server
    if not check_server_health():
        print("Please start the server first!")
        exit(1)
    
    # Run tests
    test_ticket_creation()
    
    # Test single flow
    test_single_ticket()
    
    print("\n" + "="*60)
    print("  🎉 All tests completed!")
    print("  View API docs: http://localhost:8000/docs")
    print("="*60 + "\n")
