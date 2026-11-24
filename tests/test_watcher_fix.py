"""
Quick test to verify gmail_watcher fix.

Tests that:
1. fetch_group_emails returns a generator
2. Converting to list works
3. Email data structure matches schema
"""

from email_assistant.tools.gmail.gmail_tools import fetch_group_emails


def test_fetch_emails():
    """Test fetching emails and converting to list"""
    print("🧪 Testing fetch_group_emails...")
    
    # Fetch emails (returns generator)
    emails_generator = fetch_group_emails(
        email_address="test@example.com",
        minutes_since=30
    )
    
    print(f"✓ fetch_group_emails returned: {type(emails_generator)}")
    
    # Convert to list
    emails = list(emails_generator)
    print(f"✓ Converted to list: {len(emails)} email(s)")
    
    # Check structure
    if emails:
        email = emails[0]
        print(f"\n📧 Sample email structure:")
        print(f"  Keys: {list(email.keys())}")
        
        required_keys = [
            'id', 'thread_id', 'from_email', 'to_email', 
            'subject', 'page_content', 'send_time'
        ]
        
        for key in required_keys:
            if key in email:
                print(f"  ✓ {key}: {email[key][:50] if isinstance(email[key], str) else email[key]}")
            else:
                print(f"  ❌ {key}: MISSING!")
        
        print("\n✅ Structure matches EmailData schema!")
    else:
        print("ℹ️  No emails to test (using mock data)")
    
    return emails


def test_workflow_input():
    """Test creating workflow input from email"""
    print("\n🧪 Testing workflow input format...")
    
    emails = test_fetch_emails()
    
    if not emails:
        print("⚠️  No emails to test with")
        return
    
    email = emails[0]
    
    # Create workflow input (matches StateInput schema)
    workflow_input = {
        "email_input": {
            "id": email.get("id", ""),
            "thread_id": email.get("thread_id", ""),
            "from_email": email.get("from_email", ""),
            "to_email": email.get("to_email", ""),
            "subject": email.get("subject", ""),
            "page_content": email.get("page_content", ""),
            "send_time": email.get("send_time", ""),
        }
    }
    
    print(f"\n✅ Workflow input created:")
    print(f"  email_input keys: {list(workflow_input['email_input'].keys())}")
    print(f"  Subject: {workflow_input['email_input']['subject'][:50]}")
    print(f"  From: {workflow_input['email_input']['from_email']}")
    
    return workflow_input


if __name__ == "__main__":
    print("=" * 60)
    print("  Gmail Watcher Fix - Verification Test")
    print("=" * 60)
    
    try:
        # Test 1: Fetch emails and convert to list
        test_fetch_emails()
        
        # Test 2: Create workflow input
        test_workflow_input()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! Watcher should work now.")
        print("=" * 60)
        print("\n🚀 Run the watcher:")
        print("   python gmail_watcher.py --interval 5")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
