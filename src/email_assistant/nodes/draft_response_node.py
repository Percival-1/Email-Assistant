"""
Draft Response Node - Generates appropriate email responses.

This node uses LLM with tools to:
- Draft professional email responses
- Check calendar availability for meeting requests
- Schedule meetings when appropriate
- Ask clarifying questions if needed
"""

from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chat_models import init_chat_model
from email_assistant.schemas import State
from email_assistant.prompts import DRAFT_SYSTEM_PROMPT
from email_assistant.tools import get_tools
from email_assistant.tools.gmail.calendar_tools_enhanced import (
    check_availability_enhanced,
    schedule_meeting_enhanced,
)
from email_assistant.thread_context import get_context_manager


def draft_response(state: State, store) -> dict:
    """
    Generate a draft response to the email.

    Args:
        state: Current workflow state with email_input and triage_result
        store: LangGraph store for memory access

    Returns:
        Updated state with draft_response and tool_calls if any
    """
    import logging

    logger = logging.getLogger(__name__)
    logger.info("📝 Draft response node started")

    try:
        # Initialize LLM with tools
        llm = init_chat_model("openai:gpt-4o", temperature=0.7)

        # Get available tools
        # Note: Using enhanced calendar tools for better availability checking
        from email_assistant.tools.default.email_tools import (
            write_email,
            Done,
            Question,
        )

        tools = [
            write_email,
            Done,
            Question,
            check_availability_enhanced,
            schedule_meeting_enhanced,
        ]
        llm_with_tools = llm.bind_tools(tools)

        # Get thread context
        context_manager = get_context_manager(llm=llm)
        thread_id = state.get("thread_id")
        context = context_manager.get_context(thread_id, store) if thread_id else ""

        # Build messages
        email_input = state["email_input"]
        triage_result = state.get("triage_result", {})

        system_msg = SystemMessage(content=DRAFT_SYSTEM_PROMPT)

        # Determine if this is a meeting/scheduling request
        email_content = str(email_input).lower()
        is_meeting_request = any(
            keyword in email_content
            for keyword in [
                "meet",
                "schedule",
                "calendar",
                "appointment",
                "call",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
                "morning",
                "afternoon",
                "evening",
                "am",
                "pm",
                "o'clock",
                "time",
                "available",
                "free",
            ]
        )

        if is_meeting_request:
            meeting_instructions = (
                """
⚠️ MEETING REQUEST DETECTED ⚠️

REQUIRED STEPS (in order):
1. Use check_availability_enhanced tool FIRST
   - Extract proposed dates/times from email
   - If no specific times mentioned, check next 3-5 business days
   - Specify meeting duration in minutes
   
2. After seeing calendar results:
   - If attendee proposed time(s) and you're available → use schedule_meeting_enhanced
   - If no times proposed or you're busy → suggest alternatives from available slots
   
3. Draft confirmation email with write_email tool

Today is: """
                + datetime.now().strftime("%Y-%m-%d %A")
                + """
"""
            )
        else:
            meeting_instructions = ""

        user_msg = HumanMessage(content=f"""
Previous context:
{context}

Email classification:
{triage_result.get('classification', 'N/A')}

Email to respond to:
{email_input}

{meeting_instructions}

Draft an appropriate response following the instructions in your system prompt.
""")

        # Get response with potential tool calls - implement agent loop
        messages = [system_msg, user_msg]
        logger.info(f"   Starting agent loop...")

        # Agent loop: execute tools until we get final text response
        max_iterations = 5
        draft = ""
        final_tool_calls = []

        for iteration in range(max_iterations):
            response = llm_with_tools.invoke(messages)

            tool_calls = response.tool_calls if hasattr(response, "tool_calls") else []
            draft = response.content if hasattr(response, "content") else ""

            logger.info(
                f"   Iteration {iteration + 1}: {len(draft)} chars, {len(tool_calls)} tools"
            )

            if tool_calls:
                # Execute tools
                from langchain_core.messages import ToolMessage, AIMessage

                # Add AI response to conversation
                messages.append(response)

                for tc in tool_calls:
                    tool_name = tc.get("name")
                    logger.info(f"      Executing: {tool_name}")

                    # Find and run tool
                    tool_result = "Tool not found"
                    for tool in tools:
                        if tool.name == tool_name:
                            try:
                                tool_result = tool.invoke(tc.get("args", {}))
                            except Exception as e:
                                tool_result = f"Error: {str(e)}"
                            break

                    # Add result to conversation
                    messages.append(
                        ToolMessage(
                            content=str(tool_result), tool_call_id=tc.get("id", "")
                        )
                    )

                # Continue loop
                final_tool_calls = tool_calls
                continue

            # No tools, we're done
            if draft:
                logger.info(f"   ✅ Final draft: {len(draft)} characters")
                break

        return {
            "draft_response": draft,
            "tool_calls": final_tool_calls,
            "messages": state.get("messages", []) + messages[2:],
        }

    except Exception as e:
        logger.error(f"   ❌ Error in draft_response: {e}")
        import traceback

        traceback.print_exc()
        # Return empty draft on error
        return {
            "draft_response": f"Error generating draft: {str(e)}",
            "tool_calls": [],
        }
