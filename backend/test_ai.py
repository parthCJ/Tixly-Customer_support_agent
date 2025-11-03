"""
Quick Test - AI Classification
Run this to verify AI is working correctly
"""
import sys
import os

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.ai_service import classify_ticket, generate_reply


def test_classification():
    """Test ticket classification"""
    print("\n" + "="*70)
    print("  🧪 Testing AI Ticket Classification")
    print("="*70 + "\n")
    
    # Test Case 1: Shipping Issue (HIGH priority)
    print("Test 1: Shipping Issue")
    print("-" * 70)
    result = classify_ticket(
        subject="URGENT: Order #2021 hasn't shipped",
        description="I placed order #2021 a week ago and paid $89.99 but tracking still shows processing. I need this by Friday!",
        metadata={"order_id": "2021"}
    )
    
    print(f"✓ Category: {result['category']}")
    print(f"✓ Priority: {result['priority']}")
    print(f"✓ Sentiment: {result['sentiment']}")
    print(f"✓ Confidence: {result['confidence']:.2%}")
    print(f"✓ Urgency Keywords: {result['urgency_keywords']}")
    print(f"✓ Extracted Info: {result['extracted_info']}")
    print(f"✓ Reasoning: {result['reasoning']}")
    
    # Test Case 2: Billing Issue (CRITICAL priority)
    print("\n\nTest 2: Billing Issue")
    print("-" * 70)
    result = classify_ticket(
        subject="Double charged for subscription",
        description="I was charged $49.99 TWICE on November 1st for my monthly subscription. This is unacceptable!",
        metadata={}
    )
    
    print(f"✓ Category: {result['category']}")
    print(f"✓ Priority: {result['priority']}")
    print(f"✓ Sentiment: {result['sentiment']}")
    print(f"✓ Confidence: {result['confidence']:.2%}")
    print(f"✓ Extracted Info: {result['extracted_info']}")
    
    # Test Case 3: General Question (LOW priority)
    print("\n\nTest 3: General Question")
    print("-" * 70)
    result = classify_ticket(
        subject="How do I change my password?",
        description="I want to update my account password but can't find the option.",
        metadata={}
    )
    
    print(f"✓ Category: {result['category']}")
    print(f"✓ Priority: {result['priority']}")
    print(f"✓ Sentiment: {result['sentiment']}")
    print(f"✓ Confidence: {result['confidence']:.2%}")
    
    print("\n" + "="*70)
    print("  ✅ Classification Tests Complete!")
    print("="*70 + "\n")


def test_reply_generation():
    """Test AI reply generation"""
    print("\n" + "="*70)
    print("  💬 Testing AI Reply Generation")
    print("="*70 + "\n")
    
    ticket_data = {
        "subject": "Order #2021 hasn't shipped",
        "description": "My order was placed a week ago but still shows processing.",
        "category": "SHIPPING",
        "priority": "HIGH"
    }
    
    print("Generating suggested reply...")
    reply = generate_reply(ticket_data)
    
    print("\n📧 AI Suggested Reply:")
    print("-" * 70)
    print(reply)
    print("-" * 70)
    
    print("\n" + "="*70)
    print("  ✅ Reply Generation Test Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    print("\n🚀 Starting AI Tests...\n")
    
    try:
        # Test classification
        test_classification()
        
        # Test reply generation
        test_reply_generation()
        
        print("\n🎉 All AI tests passed successfully!\n")
        print("Next step: Run the full server test with 'python test_tickets.py'\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        print("Make sure:")
        print("1. You have a .env file with GROQ_API_KEY set")
        print("2. Your Groq API key is valid")
        print("3. You have internet connection")
        print("4. pip install groq was run successfully\n")
        import traceback
        traceback.print_exc()
