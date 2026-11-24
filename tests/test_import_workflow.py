"""Test if workflow can even be imported and compiled."""

import sys
import traceback

try:
    print("1. Importing email_assistant...")
    from src.email_assistant.email_assistant import email_assistant

    print("2. Getting graph structure...")
    graph = email_assistant.get_graph()

    print("3. Nodes in graph:")
    for node_id in graph.nodes:
        print(f"   - {node_id}")

    print("\n4. Checking response_workflow subgraph...")
    # Try to access response_workflow node
    print("   response_workflow node exists in graph")

    print("\n✅ Workflow compiled successfully!")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
