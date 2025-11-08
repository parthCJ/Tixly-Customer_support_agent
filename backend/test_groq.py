"""
Quick test script to verify Groq API key works
Run this in HF Space to diagnose AI service issues
"""
import os
from groq import Groq

print("=" * 50)
print("🔍 Groq API Key Test")
print("=" * 50)

# Check if API key exists
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ GROQ_API_KEY not found in environment variables")
    print("Available env vars:", list(os.environ.keys()))
else:
    print(f"✅ GROQ_API_KEY found: {api_key[:10]}...{api_key[-4:]}")
    
    # Try to initialize client
    try:
        client = Groq(api_key=api_key)
        print("✅ Groq client initialized successfully")
        
        # Try a simple completion
        print("\n🧪 Testing API call...")
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say 'API works!'"}],
            max_tokens=10
        )
        print(f"✅ API Response: {completion.choices[0].message.content}")
        print("\n🎉 Everything works! AI service should be operational.")
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")
        print("Check if API key is valid at: https://console.groq.com/keys")

print("=" * 50)
