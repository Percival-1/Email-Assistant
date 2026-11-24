"""
Thread Context Management for Gmail Integration

This module handles conversation context across email threads,
maintaining conversation history and extracting relevant information
for better decision-making.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ThreadContext:
    """Manages context for email threads."""
    
    def __init__(self):
        self.threads: Dict[str, Dict[str, Any]] = {}
    
    def add_thread_message(self, thread_id: str, message: Dict[str, Any]):
        """Add a message to a thread's context.
        
        Args:
            thread_id: Gmail thread ID
            message: Message data including from, to, subject, body, timestamp
        """
        if thread_id not in self.threads:
            self.threads[thread_id] = {
                "messages": [],
                "participants": set(),
                "subject": message.get("subject", ""),
                "first_message_time": message.get("send_time"),
                "last_message_time": message.get("send_time"),
                "summary": None,
                "action_items": [],
                "mentioned_dates": [],
                "mentioned_times": []
            }
        
        thread = self.threads[thread_id]
        thread["messages"].append(message)
        thread["participants"].add(message.get("from_email", ""))
        thread["participants"].add(message.get("to_email", ""))
        thread["last_message_time"] = message.get("send_time")
        
        # Extract dates and times mentioned
        self._extract_temporal_info(thread_id, message.get("page_content", ""))
    
    def get_thread_context(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get full context for a thread.
        
        Args:
            thread_id: Gmail thread ID
            
        Returns:
            Thread context dictionary or None if not found
        """
        return self.threads.get(thread_id)
    
    def get_conversation_history(self, thread_id: str, max_messages: int = 10) -> str:
        """Get formatted conversation history for a thread.
        
        Args:
            thread_id: Gmail thread ID
            max_messages: Maximum number of recent messages to include
            
        Returns:
            Formatted conversation history as string
        """
        thread = self.threads.get(thread_id)
        if not thread:
            return "No previous conversation history."
        
        messages = thread["messages"][-max_messages:]
        
        history = "=== CONVERSATION HISTORY ===\n\n"
        for i, msg in enumerate(messages, 1):
            timestamp = msg.get("send_time", "Unknown time")
            sender = msg.get("from_email", "Unknown")
            body = msg.get("page_content", "")[:200]  # Truncate long messages
            
            history += f"Message {i} ({timestamp}):\n"
            history += f"From: {sender}\n"
            history += f"{body}\n"
            if len(msg.get("page_content", "")) > 200:
                history += "...\n"
            history += "\n"
        
        # Add context summary
        history += "=== THREAD SUMMARY ===\n"
        history += f"Participants: {', '.join(thread['participants'])}\n"
        history += f"Messages: {len(thread['messages'])}\n"
        history += f"Duration: {thread['first_message_time']} to {thread['last_message_time']}\n"
        
        if thread.get("action_items"):
            history += f"\nAction Items Mentioned:\n"
            for item in thread["action_items"]:
                history += f"- {item}\n"
        
        if thread.get("mentioned_dates"):
            history += f"\nDates Mentioned: {', '.join(thread['mentioned_dates'])}\n"
        
        return history
    
    def get_key_points(self, thread_id: str) -> str:
        """Extract key points from thread context.
        
        Args:
            thread_id: Gmail thread ID
            
        Returns:
            Key points summary
        """
        thread = self.threads.get(thread_id)
        if not thread:
            return "No context available."
        
        key_points = "=== KEY POINTS ===\n\n"
        
        # Participants
        key_points += f"**Participants:** {', '.join(thread['participants'])}\n"
        
        # Timeline
        key_points += f"**Timeline:** {thread['first_message_time']} to {thread['last_message_time']}\n"
        
        # Message count
        key_points += f"**Messages:** {len(thread['messages'])}\n\n"
        
        # Recent topics (from last 3 messages)
        recent_messages = thread["messages"][-3:]
        topics = []
        for msg in recent_messages:
            content = msg.get("page_content", "")
            # Simple topic extraction (first sentence)
            first_sentence = content.split('.')[0][:100] if content else ""
            if first_sentence:
                topics.append(first_sentence)
        
        if topics:
            key_points += "**Recent Topics:**\n"
            for i, topic in enumerate(topics, 1):
                key_points += f"{i}. {topic}\n"
        
        return key_points
    
    def _extract_temporal_info(self, thread_id: str, text: str):
        """Extract dates and times mentioned in text.
        
        Args:
            thread_id: Gmail thread ID
            text: Message text to analyze
        """
        import re
        
        thread = self.threads[thread_id]
        
        # Simple date patterns (can be enhanced)
        date_patterns = [
            r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}\b',
            r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
            r'\b(?:today|tomorrow|next week|next month)\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            thread["mentioned_dates"].extend(matches)
        
        # Time patterns
        time_patterns = [
            r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)\b',
            r'\b\d{1,2}\s*(?:AM|PM|am|pm)\b'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            thread["mentioned_times"].extend(matches)
        
        # Remove duplicates
        thread["mentioned_dates"] = list(set(thread["mentioned_dates"]))
        thread["mentioned_times"] = list(set(thread["mentioned_times"]))
    
    def clear_thread(self, thread_id: str):
        """Clear context for a specific thread.
        
        Args:
            thread_id: Gmail thread ID
        """
        if thread_id in self.threads:
            del self.threads[thread_id]
    
    def clear_all(self):
        """Clear all thread contexts."""
        self.threads.clear()


class ThreadContextManager:
    """Enhanced thread context manager with LLM-powered summarization."""
    
    def __init__(self, llm=None):
        """Initialize with optional LLM for intelligent summarization.
        
        Args:
            llm: Language model instance for summarization
        """
        self.base_context = ThreadContext()
        self.llm = llm
    
    def add_message(self, thread_id: str, message: Dict[str, Any]):
        """Add message and optionally generate intelligent summary.
        
        Args:
            thread_id: Gmail thread ID
            message: Message data
        """
        self.base_context.add_thread_message(thread_id, message)
        
        # Generate summary if thread has 3+ messages
        thread = self.base_context.get_thread_context(thread_id)
        if thread and len(thread["messages"]) >= 3 and not thread.get("summary"):
            self._generate_summary(thread_id)
    
    def _generate_summary(self, thread_id: str):
        """Generate LLM-powered summary of thread.
        
        Args:
            thread_id: Gmail thread ID
        """
        if not self.llm:
            return
        
        thread = self.base_context.get_thread_context(thread_id)
        if not thread:
            return
        
        # Prepare conversation for summarization
        conversation = ""
        for msg in thread["messages"]:
            sender = msg.get("from_email", "Unknown")
            content = msg.get("page_content", "")
            conversation += f"{sender}: {content}\n\n"
        
        try:
            # Generate summary using LLM
            summary_prompt = f"""Summarize this email conversation in 2-3 sentences, focusing on:
1. Main topic/purpose
2. Key decisions or action items
3. Any pending questions

Conversation:
{conversation}

Summary:"""
            
            response = self.llm.invoke(summary_prompt)
            thread["summary"] = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"Generated summary for thread {thread_id}")
        except Exception as e:
            logger.warning(f"Failed to generate summary for thread {thread_id}: {e}")
    
    def get_context_for_response(self, thread_id: str) -> str:
        """Get formatted context optimized for response generation.
        
        Args:
            thread_id: Gmail thread ID
            
        Returns:
            Formatted context string
        """
        thread = self.base_context.get_thread_context(thread_id)
        if not thread:
            return "No previous context."
        
        context = "=== EMAIL THREAD CONTEXT ===\n\n"
        
        # Add summary if available
        if thread.get("summary"):
            context += f"**Summary:** {thread['summary']}\n\n"
        
        # Add key participants
        context += f"**Participants:** {', '.join(thread['participants'])}\n\n"
        
        # Add recent conversation (last 5 messages)
        context += "**Recent Conversation:**\n"
        recent_messages = thread["messages"][-5:]
        for msg in recent_messages:
            sender = msg.get("from_email", "").split('@')[0]  # Short form
            timestamp = msg.get("send_time", "")
            content = msg.get("page_content", "")[:150]
            
            context += f"\n[{timestamp}] {sender}:\n{content}"
            if len(msg.get("page_content", "")) > 150:
                context += "..."
            context += "\n"
        
        # Add temporal context
        if thread.get("mentioned_dates"):
            context += f"\n**Dates Mentioned:** {', '.join(thread['mentioned_dates'][:5])}\n"
        
        if thread.get("mentioned_times"):
            context += f"**Times Mentioned:** {', '.join(thread['mentioned_times'][:5])}\n"
        
        return context
    
    def extract_action_items(self, thread_id: str) -> List[str]:
        """Extract action items from thread using LLM.
        
        Args:
            thread_id: Gmail thread ID
            
        Returns:
            List of action items
        """
        if not self.llm:
            return []
        
        thread = self.base_context.get_thread_context(thread_id)
        if not thread:
            return []
        
        # Check cache
        if thread.get("action_items"):
            return thread["action_items"]
        
        # Prepare conversation
        conversation = ""
        for msg in thread["messages"]:
            content = msg.get("page_content", "")
            conversation += f"{content}\n\n"
        
        try:
            prompt = f"""Extract action items from this email thread. 
List only clear, actionable items. Format as bullet points.

Thread:
{conversation}

Action Items:"""
            
            response = self.llm.invoke(prompt)
            action_text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse action items
            import re
            items = re.findall(r'[-*•]\s*(.+)', action_text)
            thread["action_items"] = items
            
            return items
        except Exception as e:
            logger.warning(f"Failed to extract action items: {e}")
            return []
    
    def get_full_context(self, thread_id: str, include_history: bool = True) -> Dict[str, Any]:
        """Get comprehensive context for a thread.
        
        Args:
            thread_id: Gmail thread ID
            include_history: Whether to include full message history
            
        Returns:
            Dictionary with all context information
        """
        thread = self.base_context.get_thread_context(thread_id)
        if not thread:
            return {}
        
        context = {
            "thread_id": thread_id,
            "participants": list(thread["participants"]),
            "subject": thread["subject"],
            "message_count": len(thread["messages"]),
            "first_message": thread["first_message_time"],
            "last_message": thread["last_message_time"],
            "summary": thread.get("summary"),
            "action_items": thread.get("action_items", []),
            "mentioned_dates": thread.get("mentioned_dates", []),
            "mentioned_times": thread.get("mentioned_times", [])
        }
        
        if include_history:
            context["messages"] = thread["messages"]
        
        return context


# Global context manager instance
_global_context_manager = None

def get_context_manager(llm=None) -> ThreadContextManager:
    """Get or create global context manager instance.
    
    Args:
        llm: Optional LLM instance for summarization
        
    Returns:
        ThreadContextManager instance
    """
    global _global_context_manager
    if _global_context_manager is None:
        _global_context_manager = ThreadContextManager(llm=llm)
    return _global_context_manager
