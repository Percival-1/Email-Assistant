"""
Email Assistant - Main entry point.

A structured, modular email assistant with:
- Nodes: Discrete processing steps (triage, draft, review, send, etc.)
- Workflows: Logical groupings of nodes (triage_workflow, response_workflow)
- Main Workflow: Top-level orchestration

Architecture:
    nodes/          - Individual processing steps
    workflows/      - Composed workflows
    storage/        - PostgreSQL + Redis backends
    tools/          - Gmail, Calendar, etc.
"""

from dotenv import load_dotenv
from email_assistant.workflows import build_main_workflow

# Load environment variables
load_dotenv(".env")

# Build the complete email assistant
email_assistant = build_main_workflow()

# Export for LangGraph
__all__ = ["email_assistant"]


if __name__ == "__main__":
    # Test the workflow structure
    print("Email Assistant Workflow Structure:")
    print("=" * 50)
    print("\nNodes in workflow:")
    for node in email_assistant.get_graph().nodes:
        print(f"  - {node}")
    
    print("\nEdges in workflow:")
    for edge in email_assistant.get_graph().edges:
        print(f"  - {edge}")
