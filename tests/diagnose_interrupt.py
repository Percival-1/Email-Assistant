"""
Diagnostic script to test interrupt and email sending.

Run this to see exactly where the workflow is failing.
"""

import asyncio
from langgraph_sdk import get_client


async def diagnose_workflow():
    """Test the complete workflow with diagnostics."""
    
    print("=" * 60)
    print("  Interrupt & Email Send Diagnostic")
    print("=" * 60)
    
    # Connect to server
    print("\n[1/6] Connecting to LangGraph server...")
    client = get_client(url="http://localhost:2024")
    
    try:
        await client.threads.search()
        print("   ✅ Connected successfully")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print("\n   Solution: Run 'langgraph dev' in another terminal")
        return
    
    # Create test input
    print("\n[2/6] Creating test email input...")
    test_email = {
        "email_input": {
            "id": "test-msg-12345",
            "thread_id": "test-thread-12345",
            "from_email": "sender@example.com",
            "to_email": "your@email.com",  # Change this to your email
            "subject": "Test Meeting Request",
            "page_content": "Hi, can we schedule a meeting this Sunday at 2 PM?",
            "send_time": "2026-11-24T10:00:00",
        }
    }
    
    print(f"   ✅ Test email created")
    print(f"      From: {test_email['email_input']['from_email']}")
    print(f"      Subject: {test_email['email_input']['subject']}")
    
    # Create thread
    print("\n[3/6] Creating thread...")
    thread = await client.threads.create()
    thread_id = thread["thread_id"]
    print(f"   ✅ Thread created: {thread_id}")
    
    # Start run
    print("\n[4/6] Starting workflow run...")
    run = await client.runs.create(
        thread_id=thread_id,
        assistant_id="email_assistant",
        input=test_email,
    )
    run_id = run["run_id"]
    print(f"   ✅ Run started: {run_id}")
    
    # Wait and check status
    print("\n[5/6] Monitoring run status...")
    max_checks = 30
    check_count = 0
    
    while check_count < max_checks:
        await asyncio.sleep(2)
        check_count += 1
        
        try:
            run_status = await client.runs.get(thread_id=thread_id, run_id=run_id)
            status = run_status.get("status", "unknown")
            
            print(f"   [{check_count}] Status: {status}")
            
            if status == "interrupted":
                print("\n   ✅ INTERRUPT DETECTED!")
                print("   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print("   This means:")
                print("   1. ✅ Triage classified as 'respond'")
                print("   2. ✅ should_review() routed to human_review")
                print("   3. ✅ interrupt() was called successfully")
                print("   4. ✅ Email should appear in Agent Inbox!")
                print("   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                
                # Get state to see what's being interrupted
                state = await client.threads.get_state(thread_id=thread_id)
                print(f"\n   Current Node: {state.get('values', {}).get('__langgraph_state__', {}).get('next', 'unknown')}")
                
                # Check if draft exists
                draft = state.get("values", {}).get("draft_response", "")
                if draft:
                    print(f"   Draft length: {len(draft)} characters")
                    print(f"   Draft preview: {draft[:100]}...")
                else:
                    print("   ⚠️  No draft found in state")
                
                print("\n   Next steps:")
                print("   1. Go to: https://dev.agentinbox.ai")
                print("   2. Click 'Interrupted' tab")
                print(f"   3. Find thread: {thread_id}")
                print("   4. Click 'Approve'")
                print(f"   5. Run: python check_email_sent.py {thread_id}")
                
                return
            
            elif status == "success":
                print("\n   ⚠️  RUN COMPLETED WITHOUT INTERRUPT")
                print("   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print("   Possible reasons:")
                print("   1. ❌ Triage classified as 'ignore' or 'notify'")
                print("   2. ❌ should_review() didn't route to human_review")
                print("   3. ❌ Classification not set correctly")
                print("   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                
                # Get final state
                state = await client.threads.get_state(thread_id=thread_id)
                values = state.get("values", {})
                
                print(f"\n   Classification: {values.get('classification_decision', 'NOT SET')}")
                print(f"   Triage: {values.get('triage_result', {}).get('classification', 'NOT SET')}")
                
                if values.get('classification_decision') not in ['respond', 'urgent']:
                    print("\n   🔧 FIX: Email classified as non-respond")
                    print("      Solution: Check triage_node.py classification logic")
                
                return
            
            elif status == "error":
                print("\n   ❌ RUN FAILED WITH ERROR")
                error = run_status.get("error", "Unknown error")
                print(f"   Error: {error}")
                return
        
        except Exception as e:
            print(f"   ⚠️  Error checking status: {e}")
    
    print("\n   ⏱️  Timeout waiting for run to complete")
    print("   The run may still be processing...")


async def check_sent_email(thread_id: str):
    """Check if email was sent after approval."""
    print("=" * 60)
    print("  Checking Email Send Status")
    print("=" * 60)
    
    client = get_client(url="http://localhost:2024")
    
    print(f"\n[1/2] Getting thread state: {thread_id}")
    state = await client.threads.get_state(thread_id=thread_id)
    
    values = state.get("values", {})
    
    print(f"\n[2/2] Email Send Status:")
    print(f"   human_approved: {values.get('human_approved', 'NOT SET')}")
    print(f"   send_status: {values.get('send_status', 'NOT SET')}")
    print(f"   send_result: {values.get('send_result', 'NOT SET')}")
    
    if values.get('send_status') == 'sent':
        print("\n   ✅ EMAIL SENT SUCCESSFULLY!")
        print("   Check Gmail Sent folder")
    elif values.get('send_status') == 'rejected':
        print("\n   ⚠️  Email was rejected by human reviewer")
    elif values.get('send_status') == 'failed':
        error = values.get('send_error', 'Unknown')
        print(f"\n   ❌ Email send failed: {error}")
    else:
        print("\n   ⏳ Email not sent yet (or status not set)")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        # Check mode: python diagnose_interrupt.py check <thread_id>
        if len(sys.argv) < 3:
            print("Usage: python diagnose_interrupt.py check <thread_id>")
            sys.exit(1)
        
        thread_id = sys.argv[2]
        asyncio.run(check_sent_email(thread_id))
    else:
        # Normal mode: test interrupt
        asyncio.run(diagnose_workflow())
