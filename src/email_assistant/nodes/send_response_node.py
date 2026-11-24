"""
Send Response Node - Sends the approved email response.

This node executes the actual sending of the email through Gmail API.
"""

import logging
from email_assistant.schemas import State
from email_assistant.tools.gmail.gmail_tools import send_email

logger = logging.getLogger(__name__)


def send_response(state: State, store) -> dict:
    """
    Send the approved email response via Gmail API.

    Args:
        state: Current workflow state with draft_response and email_input
        store: LangGraph store for memory access

    Returns:
        Updated state with send_status
    """
    draft = state.get("draft_response", "")
    email_input = state.get("email_input", {})

    # Check if human review happened and was rejected
    if not state.get("human_approved", True):
        logger.info("Email response rejected by human reviewer, not sending")
        return {
            "send_status": "rejected",
            "send_result": "Human reviewer rejected the draft response",
        }

    # Extract email details from email_input
    # Email input structure: {id, thread_id, from_email, to_email, subject, page_content, send_time}
    message_id = email_input.get("id", "")
    sender_email = email_input.get("to_email", "")  # Our email (the assistant's email)

    if not message_id:
        logger.error("No message ID found in email_input")
        return {
            "send_status": "failed",
            "send_error": "Missing message ID - cannot reply",
        }

    if not sender_email:
        logger.error("No sender email found in email_input")
        return {
            "send_status": "failed",
            "send_error": "Missing sender email address",
        }

    try:
        # Send email via Gmail API
        # send_email expects: (email_id, response_text, email_address, addn_recipients)
        logger.info(f"Sending email reply to message ID: {message_id}")
        logger.info(f"From: {sender_email}")
        logger.info(f"Draft length: {len(draft)} characters")

        success = send_email(
            email_id=message_id,
            response_text=draft,
            email_address=sender_email,
            addn_receipients=None,
        )

        if success:
            logger.info("✅ Email sent successfully via Gmail API")
            return {
                "send_status": "sent",
                "send_result": "Email sent successfully",
            }
        else:
            logger.error("❌ Email send failed")
            return {
                "send_status": "failed",
                "send_error": "send_email returned False",
            }

    except Exception as e:
        logger.error(f"❌ Exception while sending email: {str(e)}")
        import traceback

        traceback.print_exc()
        return {
            "send_status": "failed",
            "send_error": str(e),
        }
