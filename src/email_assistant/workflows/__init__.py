"""
Workflow components for the email assistant.

Each workflow represents a logical grouping of nodes for specific tasks.
"""

from email_assistant.workflows.triage_workflow import build_triage_workflow
from email_assistant.workflows.response_workflow import build_response_workflow
from email_assistant.workflows.main_workflow import build_main_workflow

__all__ = [
    "build_triage_workflow",
    "build_response_workflow",
    "build_main_workflow",
]
