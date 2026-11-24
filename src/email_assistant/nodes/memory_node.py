"""
Memory Node - Updates conversation memory and learning.

This node stores the interaction for future reference and learning:
- Saves conversation to PostgreSQL (long-term)
- Updates Redis cache (fast access)
- Records human feedback for improvement
"""

from langchain.chat_models import init_chat_model
from email_assistant.schemas import State
from email_assistant.thread_context import get_context_manager


def update_memory(state: State, store) -> dict:
    """
    Save the interaction to memory systems.

    Args:
        state: Current workflow state with all interaction details
        store: LangGraph store for memory access

    Returns:
        Empty dict (state unchanged)
    """
    # Initialize context manager
    llm = init_chat_model("openai:gpt-4o-mini", temperature=0.0)
    context_manager = get_context_manager(llm=llm)

    # Get interaction details
    thread_id = state.get("thread_id")
    email_input = state.get("email_input", "")
    draft_response = state.get("draft_response", "")
    human_feedback = state.get("human_feedback", "")

    # Update context
    if thread_id:
        interaction_summary = f"""
Email: {email_input[:200]}...
Response: {draft_response[:200]}...
Feedback: {human_feedback}
"""
        context_manager.update_context(thread_id, interaction_summary, store)

    # Note: Additional storage to PostgreSQL/Redis happens in context_manager
    # which uses the integrated storage backend

    return {}
