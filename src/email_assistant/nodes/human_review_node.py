"""
Human Review Node - Pauses workflow for human approval via Agent Inbox.

This node creates an interrupt compatible with Agent Inbox where a human can:
- Accept the draft response as-is
- Edit the draft before sending
- Respond with modifications
- Ignore/reject the email

Agent Inbox Schema: https://github.com/langchain-ai/agent-inbox
"""

import logging
from langgraph.types import interrupt
from email_assistant.schemas import State

logger = logging.getLogger(__name__)


def human_review(state: State, store) -> dict:
    """
    Interrupt workflow for human review using Agent Inbox format.

    Agent Inbox requires:
    - action_request: {action: str, args: dict}
    - config: {allow_ignore, allow_respond, allow_edit, allow_accept}
    - description: Optional markdown description

    Returns HumanResponse:
    - type: "accept" | "ignore" | "response" | "edit"
    - args: None | str | ActionRequest

    Args:
        state: Current workflow state with draft_response
        store: LangGraph store for memory access

    Returns:
        Dict with human_approved flag and feedback
    """
    draft = state.get("draft_response", "")
    email_input = state.get("email_input", {})
    triage_result = state.get("triage_result", {})

    logger.info("=" * 60)
    logger.info("🔔 INTERRUPT: Pausing for human review (Agent Inbox)")
    logger.info(f"   Draft length: {len(draft)} characters")
    logger.info(f"   Classification: {triage_result.get('classification', 'unknown')}")
    logger.info(f"   From: {email_input.get('from_email', 'unknown')}")
    logger.info("=" * 60)

    # Build Agent Inbox compatible interrupt format
    original_from = email_input.get("from_email", "Unknown")
    original_subject = email_input.get("subject", "No subject")
    original_body = email_input.get("body", "")[:300]

    description = f"""## Email Response Review

**Original Email:**
- **From:** {original_from}
- **Subject:** {original_subject}
- **Body:** {original_body}{'...' if len(email_input.get('body', '')) > 300 else ''}

**Classification:** {triage_result.get('classification', 'unknown')}

**Draft Response:**
```
{draft}
```

### Actions:
- **Accept**: Send the draft as-is
- **Edit**: Modify the draft before sending
- **Response**: Provide different text to send
- **Ignore**: Don't send this email
"""

    # Create Agent Inbox interrupt
    interrupt_request = {
        "action_request": {
            "action": "send_email",  # Action name shown in Agent Inbox
            "args": {
                "to": email_input.get("from_email", ""),
                "subject": f"Re: {email_input.get('subject', '')}",
                "body": draft,
                "original_email_id": email_input.get("email_id", ""),
            },
        },
        "config": {
            "allow_ignore": True,  # Can reject/ignore
            "allow_respond": True,  # Can provide custom response
            "allow_edit": True,  # Can edit the draft
            "allow_accept": True,  # Can accept as-is
        },
        "description": description,
    }

    logger.info("   Sending interrupt to Agent Inbox...")

    # Call interrupt - Agent Inbox returns a list with single HumanResponse
    responses = interrupt(interrupt_request)

    # Extract first response (Agent Inbox always returns a list)
    human_response = responses[0] if isinstance(responses, list) else responses

    # When resumed, process human response
    logger.info("=" * 60)
    logger.info("✅ RESUMED: Processing Agent Inbox response")
    logger.info(f"   Response type: {human_response.get('type', 'unknown')}")
    logger.info("=" * 60)

    # Process based on response type
    response_type = human_response.get("type", "accept")
    response_args = human_response.get("args")

    if response_type == "accept":
        # Accepted as-is
        logger.info("   → ACCEPTED as-is")
        approved = True
        modified_draft = draft
        feedback_notes = "Accepted without changes"

    elif response_type == "edit":
        # Edited the draft
        logger.info("   → EDITED")
        approved = True
        # response_args is an ActionRequest with updated args
        if isinstance(response_args, dict):
            modified_draft = response_args.get("args", {}).get("body", draft)
        else:
            modified_draft = str(response_args) if response_args else draft
        feedback_notes = "Draft edited by human"
        logger.info(f"   New draft length: {len(modified_draft)} chars")

    elif response_type == "response":
        # Provided custom response text
        logger.info("   → CUSTOM RESPONSE provided")
        approved = True
        modified_draft = str(response_args) if response_args else draft
        feedback_notes = "Custom response provided"
        logger.info(f"   Response length: {len(modified_draft)} chars")

    elif response_type == "ignore":
        # Rejected/ignored
        logger.info("   → IGNORED/REJECTED")
        approved = False
        modified_draft = draft
        feedback_notes = "Email rejected by human"
    else:
        # Unknown type - default to accept
        logger.warning(
            f"   → Unknown response type: {response_type}, defaulting to ACCEPT"
        )
        approved = True
        modified_draft = draft
        feedback_notes = f"Unknown response type: {response_type}"

    logger.info(f"   Final status: {'✅ APPROVED' if approved else '❌ REJECTED'}")

    return {
        "human_approved": approved,
        "draft_response": modified_draft,
        "human_feedback": feedback_notes,
    }
