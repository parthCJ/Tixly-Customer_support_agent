"""
Quick script to submit test tickets from test_tickets_data.json
Perfect for testing and showcasing without manual form entry
"""
import requests
import json
import time
import sys
from typing import Optional

API_URL = "http://localhost:8000"

def submit_ticket(ticket_data: dict, delay: float = 2.0) -> Optional[dict]:
    """Submit a single ticket to the API"""
    try:
        response = requests.post(
            f"{API_URL}/api/tickets/create/",
            json=ticket_data,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        ticket_id = result.get('ticket', {}).get('ticket_id', 'Unknown')
        print(f"✅ Submitted: {ticket_data['subject'][:50]}... (ID: {ticket_id})")
        time.sleep(delay)  # Delay between submissions
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed: {ticket_data['subject'][:50]}... - {str(e)}")
        return None

def load_test_tickets(filename: str = "test_tickets_data.json") -> list:
    """Load tickets from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Invalid JSON in {filename}")
        sys.exit(1)

def main():
    """Main execution"""
    print("🎯 Test Ticket Submission Script")
    print("=" * 60)
    
    # Check if backend is running
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        print(f"Backend is running at {API_URL}\n")
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to backend at {API_URL}")
        print("   Make sure the backend is running first!")
        sys.exit(1)
    
    # Load tickets
    tickets = load_test_tickets()
    print(f"📋 Loaded {len(tickets)} test tickets\n")
    
    # Ask how many to submit
    print("How many tickets do you want to submit?")
    print(f"  1) Submit 5 tickets (quick demo)")
    print(f"  2) Submit 10 tickets")
    print(f"  3) Submit all {len(tickets)} tickets")
    print(f"  4) Custom number")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    count_map = {
        '1': 5,
        '2': 10,
        '3': len(tickets),
    }
    
    if choice in count_map:
        num_to_submit = count_map[choice]
    elif choice == '4':
        try:
            num_to_submit = int(input("Enter number of tickets: ").strip())
            num_to_submit = min(num_to_submit, len(tickets))
        except ValueError:
            print("Invalid number, defaulting to 5")
            num_to_submit = 5
    else:
        print("Invalid choice, defaulting to 5")
        num_to_submit = 5
    
    print(f"\n🚀 Submitting {num_to_submit} tickets...\n")
    
    # Submit tickets
    successful = 0
    failed = 0
    
    for i, ticket in enumerate(tickets[:num_to_submit], 1):
        print(f"[{i}/{num_to_submit}] ", end="")
        result = submit_ticket(ticket)
        if result:
            successful += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {num_to_submit}")
    print("=" * 60)
    print(f"\n💡View tickets at: http://localhost:3000/agent/tickets")

if __name__ == "__main__":
    main()
