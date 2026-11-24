"""
Response Workflow - Handles drafting and sending email responses.

This workflow:
1. Drafts a response using LLM + tools
2. Sends for human review if needed
3. Sends the approved response
4. Updates memory with the interaction
"""

from langgraph.graph import StateGraph, START, END
from email_assistant.schemas import State
from email_assistant.nodes import (
    draft_response,
    human_review,
    send_response,
    update_memory,
)


def should_review(state: State) -> str:
    """
    Determine if human review is needed.

    For Agent Inbox integration, we ALWAYS review respond/urgent emails.

    Returns:
        Next node: 'human_review' or 'send_response'
    """
    classification = state.get("classification_decision", "").lower()

    # Always review respond and urgent classifications (for HITL)
    if classification in ["respond", "urgent"]:
        return "human_review"

    # Skip review for ignore/notify
    return "send_response"


def build_response_workflow():
    """
    Build the response handling workflow.

    Flow:
        START → draft_response → [review?] → human_review → send_response → update_memory → END

    Note: human_review node will create an interrupt for HITL approval.
    """
    workflow = StateGraph(State)

    # Add nodes
    workflow.add_node("draft_response", draft_response)
    workflow.add_node("human_review", human_review)
    workflow.add_node("send_response", send_response)
    workflow.add_node("update_memory", update_memory)

    # Add edges
    workflow.add_edge(START, "draft_response")
    workflow.add_conditional_edges(
        "draft_response",
        should_review,
        {
            "human_review": "human_review",
            "send_response": "send_response",
        },
    )
    workflow.add_edge("human_review", "send_response")
    workflow.add_edge("send_response", "update_memory")
    workflow.add_edge("update_memory", END)

    # Compile subgraph (dynamic interrupts handled in human_review node)
    return workflow.compile()
