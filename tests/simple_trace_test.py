"""
Simple LangSmith Trace Test

This creates a simple trace to verify LangSmith is working.
No datasets required.
"""

import os
from dotenv import load_dotenv
from langsmith import traceable
from langchain_openai import ChatOpenAI

# Load environment
load_dotenv()

print("=" * 60)
print("  Simple LangSmith Trace Test")
print("=" * 60)

# Check environment
if not os.getenv("LANGCHAIN_API_KEY"):
    print("❌ LANGCHAIN_API_KEY not found")
    exit(1)

if not os.getenv("OPENAI_API_KEY"):
    print("❌ OPENAI_API_KEY not found")
    exit(1)

print("✓ API keys found")
print(f"✓ Project: {os.getenv('LANGCHAIN_PROJECT', 'default')}")

# Simple traced function
@traceable(name="email_triage_test")
def triage_email(email_text: str) -> dict:
    """Test function with tracing."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    response = llm.invoke(
        f"Classify this email as: 'meeting', 'question', 'action', or 'fyi'.\n\nEmail: {email_text}\n\nRespond with just the category."
    )
    
    return {
        "email": email_text,
        "category": response.content.strip().lower()
    }

# Test it
print("\n📧 Testing email triage with LangSmith tracing...")

test_email = "Can we schedule a meeting for next Tuesday at 2pm?"

try:
    result = triage_email(test_email)
    
    print(f"✓ Email classified as: {result['category']}")
    print("\n" + "=" * 60)
    print("✅ Success! LangSmith trace created!")
    print("=" * 60)
    print(f"\n👉 View trace at: https://smith.langchain.com/o/*/projects/{os.getenv('LANGCHAIN_PROJECT', 'default')}")
    print("\nYou should see:")
    print("  • Trace name: email_triage_test")
    print("  • Input: Email text")
    print("  • Output: Classification category")
    print("  • LLM calls to OpenAI")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nCheck:")
    print("1. OPENAI_API_KEY is valid")
    print("2. LANGCHAIN_API_KEY is valid")
    print("3. Internet connection")
    exit(1)
