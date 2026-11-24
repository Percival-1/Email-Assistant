"""
Main Workflow - Orchestrates the complete email assistant.

This is the top-level workflow that coordinates:
1. Triage workflow - Email classification
2. Response workflow - Draft, review, send
3. Cleanup - Mark as read, update stats
"""

from langgraph.graph import StateGraph, START, END
from email_assistant.schemas import State, StateInput
from email_assistant.nodes import mark_email_as_read
from email_assistant.workflows.triage_workflow import build_triage_workflow
from email_assistant.workflows.response_workflow import build_response_workflow


def should_process_email(state: State) -> str:
    """
    Determine if email should be processed or archived.

    Returns:
        Next node: 'response_workflow' or 'mark_as_read'
    """
    triage_result = state.get("triage_result", {})
    classification = triage_result.get("classification", "").lower()

    # Skip processing for spam or low-priority
    if "spam" in classification or "ignore" in classification:
        return "mark_as_read"

    return "response_workflow"


def build_main_workflow():
    """
    Build the complete email assistant workflow.

    Flow:
        START → triage_workflow → [should_process?] → response_workflow → mark_as_read → END
                                                     ↘ mark_as_read → END
    """
    # Build sub-workflows
    triage_workflow = build_triage_workflow()
    response_workflow = build_response_workflow()

    # Build main workflow
    workflow = StateGraph(State, input=StateInput)

    # Add sub-workflows as nodes
    workflow.add_node("triage_workflow", triage_workflow)
    workflow.add_node("response_workflow", response_workflow)
    workflow.add_node("mark_as_read", mark_email_as_read)

    # Connect the flow
    workflow.add_edge(START, "triage_workflow")
    workflow.add_conditional_edges(
        "triage_workflow",
        should_process_email,
        {
            "response_workflow": "response_workflow",
            "mark_as_read": "mark_as_read",
        },
    )
    workflow.add_edge("response_workflow", "mark_as_read")
    workflow.add_edge("mark_as_read", END)

    return workflow.compile()
