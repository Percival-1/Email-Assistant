"""
Quick test of email assistant (Windows-friendly)
"""

from email_assistant.email_assistant import email_assistant

print("=" * 60)
print("  Email Assistant - Quick Test")
print("=" * 60)

# Test email
test_email = """
From: alice@company.com
Subject: Weekly Team Meeting
Body: Hi team, can we schedule our weekly sync for Thursday at 3pm? Please confirm if this time works for everyone.
"""

print("\n📧 Test Email:")
print(test_email)

print("\n⏳ Processing with agent...")
print("-" * 60)

# Run the agent
result = email_assistant.invoke({"email_input": test_email})

print("\n📊 Results:")
print("-" * 60)

# Show classification
if "classification_decision" in result:
    print(f"✓ Classification: {result['classification_decision']}")

# Show triage result
if "triage_result" in result:
    triage = result['triage_result']
    print(f"✓ Triage: {triage}")

# Show messages
if "messages" in result and result["messages"]:
    print(f"\n💬 Agent Response:")
    last_msg = result["messages"][-1]
    if hasattr(last_msg, 'content'):
        print(last_msg.content[:300] + "...")

print("\n" + "=" * 60)
print("✅ Test complete!")
print("=" * 60)

print("\n🌐 For more testing, open:")
print("   http://127.0.0.1:2024/docs")
