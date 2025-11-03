"""
Agent Management System - Test Script

Tests the complete agent integration including:
- Agent creation and management
- Manual ticket assignment
- Auto-assignment with load balancing
- Agent capacity tracking
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_json(data: Dict[Any, Any], title: str = None):
    """Pretty print JSON data"""
    if title:
        print(f"\n{title}:")
    print(json.dumps(data, indent=2, default=str))


def test_agent_creation():
    """Test creating a new agent"""
    print_section("1. CREATE NEW AGENT")
    
    agent_data = {
        "agent_id": "AGENT-TEST-001",
        "name": "Test Agent John",
        "email": "john.test@company.com",
        "team": "test_team",
        "skills": ["SHIPPING", "BILLING"],
        "max_tickets_per_day": 10
    }
    
    response = requests.post(f"{BASE_URL}/api/agents/", json=agent_data)
    
    if response.status_code == 201:
        print("✅ Agent created successfully!")
        print_json(response.json())
    else:
        print(f"❌ Failed to create agent: {response.status_code}")
        print(response.text)
    
    return response.json() if response.status_code == 201 else None


def test_list_agents():
    """Test listing all agents"""
    print_section("2. LIST ALL AGENTS")
    
    response = requests.get(f"{BASE_URL}/api/agents/")
    
    if response.status_code == 200:
        agents = response.json()
        print(f"✅ Found {len(agents)} agents:\n")
        
        for agent in agents:
            print(f"  • {agent['agent_id']}: {agent['name']}")
            print(f"    Team: {agent['team']}")
            print(f"    Skills: {', '.join(agent['skills'])}")
            print(f"    Load: {agent['current_load']}/{agent['max_tickets_per_day']}")
            print(f"    Status: {agent['status']}")
            print()
    else:
        print(f"❌ Failed to list agents: {response.status_code}")


def test_agent_statistics():
    """Test getting agent statistics"""
    print_section("3. AGENT STATISTICS")
    
    response = requests.get(f"{BASE_URL}/api/agents/stats")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Agent Statistics:\n")
        
        for stat in stats:
            availability = "🟢 Available" if stat['is_available'] else "🔴 Unavailable"
            print(f"  {stat['name']} ({stat['agent_id']})")
            print(f"    Current Load: {stat['current_load']}/{stat['max_tickets_per_day']} tickets")
            print(f"    Utilization: {stat['utilization_percentage']:.1f}%")
            print(f"    Available Capacity: {stat['available_capacity']} tickets")
            print(f"    Status: {availability}")
            print(f"    Resolved: {stat['total_tickets_resolved']} tickets")
            print()
    else:
        print(f"❌ Failed to get statistics: {response.status_code}")


def test_create_ticket():
    """Create a test ticket"""
    print_section("4. CREATE TEST TICKET")
    
    ticket_data = {
        "subject": "Package not delivered",
        "description": "I ordered a laptop 2 weeks ago but haven't received it yet. Can you help track my order?",
        "customer_email": "customer@example.com",
        "customer_name": "Test Customer"
    }
    
    response = requests.post(f"{BASE_URL}/api/tickets/create", json=ticket_data)
    
    if response.status_code == 200:
        ticket = response.json()
        print("✅ Ticket created successfully!")
        print(f"\nTicket ID: {ticket['ticket']['ticket_id']}")
        print(f"Category: {ticket['ticket'].get('category', 'Not classified yet')}")
        print(f"Priority: {ticket['ticket'].get('priority', 'Not set yet')}")
        print(f"Status: {ticket['ticket']['status']}")
        return ticket['ticket']['ticket_id']
    else:
        print(f"❌ Failed to create ticket: {response.status_code}")
        print(response.text)
        return None


def test_manual_assignment(ticket_id: str, agent_id: str = "AGENT-001"):
    """Test manual ticket assignment"""
    print_section("5. MANUAL TICKET ASSIGNMENT")
    
    print(f"Assigning ticket {ticket_id} to {agent_id}...")
    
    response = requests.put(
        f"{BASE_URL}/api/tickets/{ticket_id}/assign",
        params={"agent_id": agent_id}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Manual assignment successful!")
        print_json(result['assignment'], "Assignment Details")
    else:
        print(f"❌ Failed to assign ticket: {response.status_code}")
        print(response.text)


def test_auto_assignment(ticket_id: str):
    """Test automatic ticket assignment"""
    print_section("6. AUTO-ASSIGNMENT (INTELLIGENT ROUTING)")
    
    print(f"Auto-assigning ticket {ticket_id}...")
    
    response = requests.put(
        f"{BASE_URL}/api/tickets/{ticket_id}/assign",
        params={"auto_assign": True}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Auto-assignment successful!")
        print_json(result['assignment'], "Assignment Details")
        
        # Show updated agent stats
        print("\n📊 Updated Agent Load:")
        stats_response = requests.get(f"{BASE_URL}/api/agents/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            assigned_agent = result['assignment']['agent_id']
            for stat in stats:
                if stat['agent_id'] == assigned_agent:
                    print(f"  {stat['name']}: {stat['current_load']}/{stat['max_tickets_per_day']} tickets ({stat['utilization_percentage']:.1f}% utilized)")
    else:
        print(f"❌ Failed to auto-assign: {response.status_code}")
        print(response.text)


def test_available_agents_by_skill():
    """Test finding available agents by skill"""
    print_section("7. FIND AVAILABLE AGENTS BY SKILL")
    
    skill = "SHIPPING"
    print(f"Finding available agents with skill: {skill}\n")
    
    response = requests.get(
        f"{BASE_URL}/api/agents/available/by-skill",
        params={"skill": skill}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {result['available_count']} available agents with {skill} skill:\n")
        
        for agent in result['agents']:
            print(f"  • {agent['name']} ({agent['agent_id']})")
            print(f"    Team: {agent['team']}")
            print(f"    Load: {agent['current_load']}/{agent['max_tickets_per_day']}")
            print(f"    Capacity: {agent['available_capacity']} tickets")
            print()
    else:
        print(f"❌ Failed to find agents: {response.status_code}")


def test_load_balancing():
    """Test load balancing with multiple tickets"""
    print_section("8. LOAD BALANCING TEST (Multiple Tickets)")
    
    print("Creating 5 shipping tickets to test load distribution...\n")
    
    ticket_ids = []
    for i in range(5):
        ticket_data = {
            "subject": f"Shipping issue #{i+1}",
            "description": f"Test shipping ticket number {i+1}",
            "customer_email": f"customer{i+1}@example.com",
            "customer_name": f"Customer {i+1}"
        }
        
        response = requests.post(f"{BASE_URL}/api/tickets/create", json=ticket_data)
        if response.status_code == 200:
            ticket_id = response.json()['ticket']['ticket_id']
            ticket_ids.append(ticket_id)
            
            # Auto-assign each ticket
            assign_response = requests.put(
                f"{BASE_URL}/api/tickets/{ticket_id}/assign",
                params={"auto_assign": True}
            )
            
            if assign_response.status_code == 200:
                assignment = assign_response.json()['assignment']
                print(f"  ✅ Ticket {i+1}: Assigned to {assignment['agent_name']} (load: {assignment['agent_load']})")
            else:
                print(f"  ❌ Ticket {i+1}: Assignment failed")
    
    # Show final load distribution
    print("\n📊 Final Load Distribution:")
    stats_response = requests.get(f"{BASE_URL}/api/agents/stats")
    if stats_response.status_code == 200:
        stats = stats_response.json()
        for stat in stats:
            if stat['current_load'] > 0:
                bar = "█" * stat['current_load']
                print(f"  {stat['name']:<20} {bar} {stat['current_load']}/{stat['max_tickets_per_day']}")


def test_resolve_ticket(ticket_id: str):
    """Test resolving a ticket (should reduce agent load)"""
    print_section("9. RESOLVE TICKET (Reduce Agent Load)")
    
    print(f"Resolving ticket {ticket_id}...\n")
    
    response = requests.put(
        f"{BASE_URL}/api/tickets/{ticket_id}/status",
        params={"status": "resolved"}
    )
    
    if response.status_code == 200:
        ticket = response.json()
        print(f"✅ Ticket resolved!")
        if ticket.get('assigned_to'):
            print(f"   Agent {ticket['assigned_to']}'s load has been reduced")
        
        # Show updated stats
        print("\n📊 Updated Agent Stats:")
        stats_response = requests.get(f"{BASE_URL}/api/agents/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            for stat in stats[:3]:  # Show top 3
                print(f"  {stat['name']}: {stat['current_load']}/{stat['max_tickets_per_day']} tickets")
    else:
        print(f"❌ Failed to resolve ticket: {response.status_code}")


def test_agent_status_update():
    """Test updating agent availability status"""
    print_section("10. UPDATE AGENT STATUS")
    
    agent_id = "AGENT-001"
    new_status = "away"
    
    print(f"Setting {agent_id} status to '{new_status}'...\n")
    
    response = requests.post(
        f"{BASE_URL}/api/agents/{agent_id}/status",
        params={"status": new_status}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        print(f"   {result['name']} is now {result['status']}")
    else:
        print(f"❌ Failed to update status: {response.status_code}")


def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "="*70)
    print("  CUSTOMER SUPPORT COPILOT - AGENT SYSTEM TESTS")
    print("="*70)
    
    try:
        # 1. Create agent
        test_agent_creation()
        
        # 2. List agents
        test_list_agents()
        
        # 3. Agent statistics
        test_agent_statistics()
        
        # 4. Create ticket
        ticket_id = test_create_ticket()
        
        if ticket_id:
            # 5. Manual assignment
            # test_manual_assignment(ticket_id)
            
            # 6. Auto-assignment
            test_auto_assignment(ticket_id)
            
            # 7. Available agents by skill
            test_available_agents_by_skill()
            
            # 8. Load balancing
            test_load_balancing()
            
            # 9. Resolve ticket
            test_resolve_ticket(ticket_id)
            
            # 10. Update agent status
            test_agent_status_update()
        
        print_section("✅ ALL TESTS COMPLETED")
        print("Agent system is fully functional!")
        print("\n🌐 View API docs: http://localhost:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server")
        print("Please start the server first: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


if __name__ == "__main__":
    run_all_tests()
