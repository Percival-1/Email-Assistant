"""
Triage Workflow - Classifies and routes incoming emails.

This workflow:
1. Analyzes the email content
2. Classifies priority and category
3. Routes to appropriate next step
"""

from langgraph.graph import StateGraph, START, END
from email_assistant.schemas import State
from email_assistant.nodes import triage_email


def route_after_triage(state: State) -> str:
    """
    Route email after triage classification.
    
    Returns:
        Next step: 'response_workflow', 'archive', or 'escalate'
    """
    triage_result = state.get("triage_result", {})
    classification = triage_result.get("classification", "").lower()
    
    # Simple routing logic
    if "spam" in classification or "unsubscribe" in classification:
        return "archive"
    elif "urgent" in classification or "escalate" in classification:
        return "escalate"
    else:
        return "response_workflow"


def build_triage_workflow():
    """
    Build the email triage workflow.
    
    Flow:
        START → triage_email → [route decision] → END
    """
    workflow = StateGraph(State)
    
    # Add triage node
    workflow.add_node("triage_email", triage_email)
    
    # Add edges
    workflow.add_edge(START, "triage_email")
    
    # Note: The routing is handled by the main workflow
    # This sub-workflow just performs triage
    workflow.add_edge("triage_email", END)
    
    return workflow.compile()
