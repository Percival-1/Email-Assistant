"""
Mark Read Node - Marks the email as read in Gmail.

Simple cleanup node to mark processed emails as read.
"""

from email_assistant.schemas import State
from email_assistant.tools.gmail.gmail_tools import mark_as_read


def parse_gmail(email_input: dict) -> tuple[str, str, str, str, str]:
    """Parse Gmail email input."""
    return (
        email_input.get("from", ""),
        email_input.get("to", ""),
        email_input.get("subject", ""),
        email_input.get("body", ""),
        email_input.get("id", ""),
    )


def mark_email_as_read(state: State, store) -> dict:
    """
    Mark the processed email as read.

    Args:
        state: Current workflow state with email_input
        store: LangGraph store for memory access

    Returns:
        Empty dict (state unchanged)
    """
    email_input = state.get("email_input", "")

    # Parse email to get ID
    _, _, _, _, email_id = parse_gmail(email_input)

    if email_id and not email_id.startswith("mock-"):
        try:
            mark_as_read(email_id)
        except Exception as e:
            # Log but don't fail - marking as read is optional
            print(f"⚠️  Could not mark email as read: {e}")
            # Continue processing - this is not critical

    return {}
