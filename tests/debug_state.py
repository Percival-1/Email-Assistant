"""Quick debug script to check thread state."""

import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
from langgraph_sdk import get_client
import time

client = get_client(url="http://localhost:2024")
assistant_id = "email_assistant"

# Create thread
thread = client.threads.create()
print(f"Thread: {thread['thread_id']}")

# Start run
input_data = {
    "email_input": {
        "email_id": "test-123",
        "from_email": "john@example.com",
        "subject": "Meeting Request",
        "body": "Can we schedule a meeting at 2pm tomorrow to discuss the project?",
        "to_email": "assistant@example.com",
    }
}

run = client.runs.create(thread["thread_id"], assistant_id, input=input_data)
print(f"Run: {run['run_id']}")

# Wait and monitor
print("\nWaiting 15 seconds...")
time.sleep(15)

run_status = client.runs.get(thread["thread_id"], run["run_id"])
print(f"\nRun Status: {run_status['status']}")

# Get the state to see what happened
state = client.threads.get_state(thread["thread_id"])
print(f"\nState info:")
print(f"  Next tasks: {state.get('next', [])}")
print(f"  Tasks: {state.get('tasks', [])}")

values = state["values"]
print(f"\nState values:")
print(f"  classification_decision: {values.get('classification_decision', 'NOT SET')}")
print(f"  draft_response: {values.get('draft_response', 'NOT SET')}")
print(f"  human_approved: {values.get('human_approved', 'NOT SET')}")
print(f"  send_status: {values.get('send_status', 'NOT SET')}")

# Check history
print(f"\nGetting state history...")
history = list(client.threads.get_history(thread["thread_id"], limit=10))
print(f"Total checkpoints: {len(history)}")
for i, checkpoint in enumerate(history):
    print(f"\n  Checkpoint {i+1}:")
    print(f"    Next: {checkpoint.get('next', [])}")
    print(f"    Tasks: {len(checkpoint.get('tasks', []))} tasks")
