"""Test response_workflow directly without server."""
from src.email_assistant.workflows.response_workflow import build_response_workflow
from src.email_assistant.schemas import State

# Build workflow
print("Building response_workflow...")
workflow = build_response_workflow()
print("✅ Workflow built")

# Test input
test_state = {
    "email_input": {
        "from_email": "test@example.com",
        "subject": "Test",
        "body": "Can we meet at 2pm tomorrow?",
        "to_email": "me@example.com"
    },
    "classification_decision": "respond",
    "triage_result": {
        "classification": "respond"
    }
}

print("\nInvoking workflow...")
try:
    result = workflow.invoke(test_state)
    print(f"✅ Result:")
    print(f"  Draft: {result.get('draft_response', 'NONE')[:100]}")
    print(f"  Human approved: {result.get('human_approved', 'NONE')}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
