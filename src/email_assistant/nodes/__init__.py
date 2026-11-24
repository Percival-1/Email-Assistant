"""
Node components for the email assistant workflow.

Each node represents a discrete step in the email processing pipeline.
"""

from email_assistant.nodes.triage_node import triage_email
from email_assistant.nodes.draft_response_node import draft_response
from email_assistant.nodes.human_review_node import human_review
from email_assistant.nodes.send_response_node import send_response
from email_assistant.nodes.mark_read_node import mark_email_as_read
from email_assistant.nodes.memory_node import update_memory

__all__ = [
    "triage_email",
    "draft_response",
    "human_review",
    "send_response",
    "mark_email_as_read",
    "update_memory",
]
