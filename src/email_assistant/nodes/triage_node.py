"""
Triage Node - Classifies incoming emails and determines routing.

This node analyzes the email content and decides:
- Priority level (high, medium, low)
- Category (meeting_request, question, complaint, etc.)
- Whether human review is needed
"""

from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model
from email_assistant.schemas import State
from email_assistant.prompts import TRIAGE_SYSTEM_PROMPT
from email_assistant.thread_context import get_context_manager


def triage_email(state: State, store) -> dict:
    """
    Analyze and classify the incoming email.

    Args:
        state: Current workflow state with email_input
        store: LangGraph store for memory access

    Returns:
        Updated state with triage_result and classification_decision
    """
    import logging

    logger = logging.getLogger(__name__)
    logger.info("🔍 Triage node started")

    # Initialize LLM
    llm = init_chat_model("openai:gpt-4o-mini", temperature=0.0)

    # Get thread context
    context_manager = get_context_manager(llm=llm)
    thread_id = state.get("thread_id")
    context = context_manager.get_context(thread_id, store) if thread_id else ""

    # Build prompt with context
    email_input = state["email_input"]
    prompt = f"""{TRIAGE_SYSTEM_PROMPT}

Previous conversation context:
{context}

Current email:
{email_input}

Classify this email and determine:
1. Priority: high/medium/low
2. Category: meeting_request/question/complaint/feedback/other
3. Needs_review: true/false (does a human need to review before responding?)
4. Classification: ignore/respond/notify
"""

    # Get classification
    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)

    # Parse response (simplified - in production use structured output)
    content = response.content.lower()

    # Determine classification decision
    if "ignore" in content:
        classification_decision = "ignore"
    elif "respond" in content:
        classification_decision = "respond"
    elif "notify" in content:
        classification_decision = "notify"
    else:
        # Default based on content
        classification_decision = "respond"

    triage_result = {
        "classification": classification_decision,
        "needs_review": "needs review" in content or "human review" in content,
        "raw_response": response.content,
    }

    logger.info(f"   ✅ Classification: {classification_decision}")
    logger.info(f"   Triage result: {triage_result}")

    return {
        "triage_result": triage_result,
        "classification_decision": classification_decision,  # Add to state for evaluation
        "messages": state.get("messages", []) + [response],
    }
