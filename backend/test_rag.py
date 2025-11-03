"""
Test RAG System - Knowledge Base Search
Tests the semantic search and retrieval functionality
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.kb_service import get_kb_service, search_knowledge_base
from data.sample_kb_articles import load_sample_articles, SAMPLE_ARTICLES


def test_kb_initialization():
    """Test KB service initialization"""
    print("\n" + "="*70)
    print("  🧪 Test 1: Knowledge Base Initialization")
    print("="*70 + "\n")
    
    kb = get_kb_service()
    stats = kb.get_stats()
    
    print(f"✓ KB initialized successfully")
    print(f"✓ Total articles: {stats['total_articles']}")
    print(f"✓ Categories: {list(stats['categories'].keys())}")
    
    if stats['total_articles'] == 0:
        print("\n⚠️  No articles found. Loading sample articles...")
        load_sample_articles()
        stats = kb.get_stats()
        print(f"✓ Loaded {stats['total_articles']} articles")
    
    return kb


def test_semantic_search():
    """Test semantic search functionality"""
    print("\n" + "="*70)
    print("  🔍 Test 2: Semantic Search")
    print("="*70 + "\n")
    
    test_queries = [
        {
            "subject": "Order hasn't arrived",
            "description": "I placed my order 10 days ago but still haven't received it. The tracking shows it was shipped but no updates.",
            "category": "shipping"
        },
        {
            "subject": "Want to return my purchase",
            "description": "The product doesn't fit well and I'd like to return it for a refund.",
            "category": "refund"
        },
        {
            "subject": "Charged twice",
            "description": "I see two charges of $49.99 on my credit card for the same order.",
            "category": "billing"
        },
        {
            "subject": "Cannot login to my account",
            "description": "I forgot my password and the reset email isn't coming through.",
            "category": "account"
        }
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query['subject']}")
        print("-" * 70)
        
        articles = search_knowledge_base(
            subject=query['subject'],
            description=query['description'],
            category=query.get('category'),
            n_results=3
        )
        
        if articles:
            print(f"Found {len(articles)} relevant articles:\n")
            for j, article in enumerate(articles, 1):
                print(f"   {j}. {article['title']}")
                print(f"      Relevance: {article['relevance_score']:.2%}")
                print(f"      Category: {article['category']}")
                print(f"      Preview: {article['content'][:100]}...")
                print()
        else:
            print("   ❌ No articles found")


def test_rag_integration():
    """Test RAG integration with AI reply generation"""
    print("\n" + "="*70)
    print("  💬 Test 3: RAG-Enhanced Reply Generation")
    print("="*70 + "\n")
    
    from services.ai_service import generate_reply
    
    ticket_data = {
        "subject": "Order hasn't shipped",
        "description": "My order #2021 was placed a week ago but the tracking still shows 'processing'. When will it ship?",
        "category": "shipping",
        "priority": "medium"
    }
    
    print("Ticket:")
    print(f"  Subject: {ticket_data['subject']}")
    print(f"  Description: {ticket_data['description']}")
    print()
    
    # Search KB first to show what articles are being used
    print("🔍 Searching knowledge base...")
    kb_articles = search_knowledge_base(
        subject=ticket_data['subject'],
        description=ticket_data['description'],
        category="shipping",
        n_results=2
    )
    
    if kb_articles:
        print(f"\n📚 Using {len(kb_articles)} relevant KB articles:")
        for article in kb_articles:
            print(f"   • {article['title']} ({article['relevance_score']:.2%} relevant)")
    
    print("\n🤖 Generating AI reply with KB context...")
    reply = generate_reply(ticket_data)
    
    print("\n📧 AI-Generated Reply:")
    print("-" * 70)
    print(reply)
    print("-" * 70)


def test_search_accuracy():
    """Test search accuracy with edge cases"""
    print("\n" + "="*70)
    print("  🎯 Test 4: Search Accuracy")
    print("="*70 + "\n")
    
    kb = get_kb_service()
    
    test_cases = [
        {
            "query": "international shipping customs delay",
            "expected_category": "shipping",
            "description": "Should find international shipping article"
        },
        {
            "query": "subscription cancel monthly payment",
            "expected_category": "billing",
            "description": "Should find subscription management article"
        },
        {
            "query": "damaged broken arrived defective",
            "expected_category": "product",
            "description": "Should find damaged product article"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"{i}. {test['description']}")
        print(f"   Query: '{test['query']}'")
        
        articles = kb.search(query=test['query'], n_results=1)
        
        if articles:
            top_article = articles[0]
            print(f"   ✓ Found: {top_article['title']}")
            print(f"   ✓ Category: {top_article['category']}")
            print(f"   ✓ Relevance: {top_article['relevance_score']:.2%}")
            
            if top_article['category'] == test['expected_category']:
                print(f"   ✅ Correct category!")
            else:
                print(f"   ⚠️  Expected {test['expected_category']}, got {top_article['category']}")
        else:
            print(f"   ❌ No articles found")
        print()


def run_all_tests():
    """Run all RAG tests"""
    print("\n" + "="*70)
    print("  🚀 RAG System Tests - Phase 3")
    print("="*70)
    
    try:
        # Test 1: Initialization
        kb = test_kb_initialization()
        
        # Test 2: Semantic search
        test_semantic_search()
        
        # Test 3: RAG integration
        test_rag_integration()
        
        # Test 4: Accuracy
        test_search_accuracy()
        
        print("\n" + "="*70)
        print("  ✅ All RAG Tests Complete!")
        print("="*70 + "\n")
        
        # Show final stats
        stats = kb.get_stats()
        print("📊 Final Knowledge Base Statistics:")
        print(f"   Total Articles: {stats['total_articles']}")
        print(f"   Categories: {dict(stats['categories'])}")
        print(f"   Storage: {stats['persist_directory']}")
        print()
        
    except Exception as e:
        print(f"\n❌ Test Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nMake sure to install dependencies:")
        print("  pip install chromadb sentence-transformers")


if __name__ == "__main__":
    run_all_tests()
