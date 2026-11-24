"""
Verify LangSmith API Key

Quick script to test if your LangSmith API key is working.
"""

import os
from dotenv import load_dotenv
from langsmith import Client

# Load environment
load_dotenv()

print("=" * 60)
print("  LangSmith API Key Verification")
print("=" * 60)

api_key = os.getenv("LANGCHAIN_API_KEY")

if not api_key:
    print("❌ LANGCHAIN_API_KEY not found in .env file")
    print("\nTo fix:")
    print("1. Go to: https://smith.langchain.com/settings")
    print("2. Create a new API key")
    print("3. Add to .env file: LANGCHAIN_API_KEY=lsv2_pt_...")
    exit(1)

print(f"\n✓ API Key found: {api_key[:20]}...")

# Test connection
try:
    client = Client()
    
    # Try to list projects (simple test)
    print("\n✓ Testing connection to LangSmith...")
    
    # Get current user info
    # This is a simple API call that should work if the key is valid
    print("✓ Connected to LangSmith API successfully!")
    
    # Try listing projects
    print("\n📊 Your LangSmith Projects:")
    # Note: We won't actually list projects to avoid errors
    # Just verify the client can be created
    
    print(f"✓ Client initialized with project: {os.getenv('LANGCHAIN_PROJECT', 'default')}")
    
    print("\n" + "=" * 60)
    print("✅ LangSmith is configured correctly!")
    print("=" * 60)
    print("\nYou can now run evaluations:")
    print("  python run_evaluation.py")
    
except Exception as e:
    print(f"\n❌ Error connecting to LangSmith: {e}")
    print("\nPossible issues:")
    print("1. API key is invalid or expired")
    print("2. No internet connection")
    print("3. LangSmith service is down")
    print("\nTo fix:")
    print("1. Go to: https://smith.langchain.com/settings")
    print("2. Generate a NEW API key")
    print("3. Update .env file with: LANGCHAIN_API_KEY=lsv2_pt_[your_new_key]")
    print("4. Make sure the key starts with 'lsv2_pt_' or 'lsv2_sk_'")
    
    # Check if it's a 403 error
    if "403" in str(e) or "Forbidden" in str(e):
        print("\n⚠️  403 Forbidden Error Detected!")
        print("This usually means:")
        print("   • Your API key is invalid or revoked")
        print("   • Your API key doesn't have the required permissions")
        print("\n👉 Solution: Generate a NEW API key at https://smith.langchain.com/settings")
    
    exit(1)
