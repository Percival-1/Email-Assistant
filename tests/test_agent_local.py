"""
Test your email assistant via local API (no UI needed)
"""

import requests
import json
import time

API_URL = "http://127.0.0.1:2024"

print("=" * 60)
print("  Testing Email Assistant Locally")
print("=" * 60)

# 1. Create a thread
print("\n1. Creating thread...")
response = requests.post(f"{API_URL}/threads")
thread = response.json()
thread_id = thread["thread_id"]
print(f"✓ Thread created: {thread_id}")

# 2. Test email
test_email = """
From: john@example.com
Subject: Meeting Request
Body: Can we schedule a meeting next Tuesday at 2pm to discuss the project?
"""

print(f"\n2. Processing email...")
print(f"   Email: {test_email[:50]}...")

# 3. Start the run
run_response = requests.post(
    f"{API_URL}/threads/{thread_id}/runs",
    json={
        "assistant_id": "email_assistant",
        "input": {"email_input": test_email}
    }
)
run = run_response.json()
run_id = run["run_id"]
print(f"✓ Run started: {run_id}")

# 4. Poll for completion or interrupt
print("\n3. Waiting for agent response...")
max_attempts = 30
for i in range(max_attempts):
    time.sleep(2)
    
    state_response = requests.get(f"{API_URL}/threads/{thread_id}/state")
    state = state_response.json()
    
    # Check if there's an interrupt (HITL)
    if state.get("next"):
        print("\n🛑 INTERRUPT - Human review needed!")
        print(f"   State: {json.dumps(state['values'], indent=2)[:200]}...")
        
        # Auto-approve for demo
        print("\n4. Auto-approving (you can modify this)...")
        requests.post(
            f"{API_URL}/threads/{thread_id}/runs/{run_id}",
            json={
                "command": {
                    "resume": {"approved": True}
                }
            }
        )
        continue
    
    # Check run status
    run_status = requests.get(f"{API_URL}/threads/{thread_id}/runs/{run_id}")
    status_data = run_status.json()
    
    if status_data["status"] == "success":
        print("✓ Agent completed!")
        break
    elif status_data["status"] == "error":
        print(f"✗ Error: {status_data.get('error')}")
        break
    else:
        print(f"   Status: {status_data['status']}...")

# 5. Get final state
print("\n5. Final state:")
final_state = requests.get(f"{API_URL}/threads/{thread_id}/state").json()
print(json.dumps(final_state["values"], indent=2)[:500])

print("\n" + "=" * 60)
print("✅ Test complete!")
print("=" * 60)
print(f"\nView in browser:")
print(f"http://127.0.0.1:2024/threads/{thread_id}")
