"""
Integrated Storage Manager

Combines PostgreSQL and Redis for optimal performance:
- Redis: Fast cache for active threads and recent data
- PostgreSQL: Long-term storage for preferences and history
"""

import logging
from typing import Optional, Dict, Any, List

from .postgres_memory import PostgresMemoryStore, get_postgres_store
from .redis_cache import RedisCache, get_redis_cache

logger = logging.getLogger(__name__)


class IntegratedStorageManager:
    """Manages both PostgreSQL and Redis storage with intelligent caching."""
    
    def __init__(
        self,
        postgres_store: PostgresMemoryStore = None,
        redis_cache: RedisCache = None
    ):
        """Initialize storage manager.
        
        Args:
            postgres_store: PostgreSQL store instance (optional)
            redis_cache: Redis cache instance (optional)
        """
        self.postgres = postgres_store or get_postgres_store()
        self.redis = redis_cache or get_redis_cache()
        
        logger.info("Integrated storage manager initialized")
    
    # === User Preferences (Postgres with Redis Cache) ===
    
    def get_preference(
        self,
        namespace: str,
        key: str,
        use_cache: bool = True
    ) -> Optional[str]:
        """Get user preference with caching.
        
        Args:
            namespace: Preference namespace
            key: Preference key
            use_cache: Whether to use Redis cache
            
        Returns:
            Preference value or None
        """
        # Try cache first
        if use_cache:
            cache_key = f"{namespace}_{key}"
            cached = self.redis.get_session_data(cache_key)
            if cached:
                logger.debug(f"Cache HIT: {namespace}/{key}")
                return cached.get("value")
        
        # Get from Postgres
        pref = self.postgres.get_preference(namespace, key)
        
        if pref:
            # Cache for future requests (1 hour)
            if use_cache:
                cache_key = f"{namespace}_{key}"
                self.redis.set_session_data(
                    cache_key,
                    {"value": pref["preference_value"]},
                    ttl=3600
                )
            
            return pref["preference_value"]
        
        return None
    
    def put_preference(
        self,
        namespace: str,
        key: str,
        value: Any
    ) -> bool:
        """Store preference and update cache.
        
        Args:
            namespace: Preference namespace
            key: Preference key
            value: Preference value
            
        Returns:
            True if successful
        """
        # Store in Postgres
        success = self.postgres.put_preference(namespace, key, value)
        
        if success:
            # Update cache
            cache_key = f"{namespace}_{key}"
            self.redis.set_session_data(
                cache_key,
                {"value": value},
                ttl=3600
            )
        
        return success
    
    # === Thread Context (Redis with Postgres Backup) ===
    
    def get_thread_context(
        self,
        thread_id: str,
        include_history: bool = True
    ) -> Dict[str, Any]:
        """Get thread context from cache or storage.
        
        Args:
            thread_id: Thread ID
            include_history: Include full message history
            
        Returns:
            Thread context dict
        """
        # Try Redis cache first
        cached = self.redis.get_thread_context(thread_id)
        if cached:
            logger.debug(f"Cache HIT: thread context for {thread_id}")
            return cached
        
        # Fallback to Postgres
        logger.debug(f"Cache MISS: loading thread from Postgres")
        
        # Get email history from Postgres
        history = self.postgres.get_thread_history(thread_id, limit=50)
        
        if not history:
            return {}
        
        # Build context
        context = {
            "thread_id": thread_id,
            "message_count": len(history),
            "messages": history if include_history else [],
            "participants": list(set(
                [email["from_email"] for email in history] +
                [email["to_email"] for email in history]
            )),
            "first_message": history[-1]["processed_at"] if history else None,
            "last_message": history[0]["processed_at"] if history else None,
        }
        
        # Cache for future requests (1 hour)
        self.redis.cache_thread_context(thread_id, context, ttl=3600)
        
        return context
    
    def add_message_to_thread(
        self,
        thread_id: str,
        email_id: str,
        from_email: str,
        to_email: str,
        subject: str,
        body: str,
        classification: str = None,
        response: str = None
    ) -> bool:
        """Add message to thread in both storages.
        
        Args:
            thread_id: Thread ID
            email_id: Email ID
            from_email: Sender
            to_email: Recipient
            subject: Subject
            body: Body
            classification: Triage classification
            response: Generated response
            
        Returns:
            True if successful
        """
        # Add to Postgres for long-term storage
        postgres_success = self.postgres.save_email(
            email_id=email_id,
            thread_id=thread_id,
            from_email=from_email,
            to_email=to_email,
            subject=subject,
            body=body,
            classification=classification,
            response=response
        )
        
        # Add to Redis for fast access
        message = {
            "email_id": email_id,
            "from_email": from_email,
            "to_email": to_email,
            "subject": subject,
            "body": body,
            "classification": classification,
            "response": response
        }
        redis_success = self.redis.add_message_to_thread(thread_id, message)
        
        # Invalidate cached thread context (will be rebuilt on next access)
        self.redis.delete("thread", thread_id)
        
        return postgres_success and redis_success
    
    def get_recent_messages(
        self,
        thread_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent messages from cache.
        
        Args:
            thread_id: Thread ID
            limit: Number of messages
            
        Returns:
            List of message dicts
        """
        # Try Redis first (fastest)
        messages = self.redis.get_thread_messages(thread_id, limit)
        
        if messages:
            return messages
        
        # Fallback to Postgres
        return self.postgres.get_thread_history(thread_id, limit)
    
    # === Action Items ===
    
    def add_action_item(self, thread_id: str, action_item: str) -> int:
        """Add action item to Postgres.
        
        Args:
            thread_id: Thread ID
            action_item: Action description
            
        Returns:
            Action item ID
        """
        return self.postgres.add_action_item(thread_id, action_item)
    
    def get_action_items(
        self,
        thread_id: str = None,
        status: str = "pending"
    ) -> List[Dict[str, Any]]:
        """Get action items from Postgres.
        
        Args:
            thread_id: Optional thread filter
            status: Status filter
            
        Returns:
            List of action items
        """
        return self.postgres.get_action_items(thread_id, status)
    
    # === Learning Feedback ===
    
    def save_feedback(
        self,
        namespace: str,
        original_content: Any,
        edited_content: Any,
        feedback_type: str
    ) -> int:
        """Save learning feedback to Postgres.
        
        Args:
            namespace: Feedback namespace
            original_content: Original content
            edited_content: Edited content
            feedback_type: Feedback type
            
        Returns:
            Feedback ID
        """
        return self.postgres.save_feedback(
            namespace,
            original_content,
            edited_content,
            feedback_type
        )
    
    # === Statistics ===
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics.
        
        Returns:
            Dict with stats from both storages
        """
        redis_stats = self.redis.get_stats()
        
        return {
            "redis": redis_stats,
            "postgres": {
                "host": self.postgres.host,
                "database": self.postgres.database,
                "connected": True
            }
        }
    
    # === Utility ===
    
    def clear_cache(self, namespace: str = None) -> int:
        """Clear Redis cache.
        
        Args:
            namespace: Optional namespace to clear
            
        Returns:
            Number of keys deleted
        """
        if namespace:
            return self.redis.clear_namespace(namespace)
        else:
            # Clear common namespaces
            count = 0
            for ns in ["thread", "email", "session"]:
                count += self.redis.clear_namespace(ns)
            return count
    
    def close(self):
        """Close all connections."""
        self.postgres.close()
        self.redis.close()
        logger.info("All storage connections closed")


# Global instance
_integrated_storage = None


def get_integrated_storage() -> IntegratedStorageManager:
    """Get or create global integrated storage instance.
    
    Returns:
        IntegratedStorageManager instance
    """
    global _integrated_storage
    if _integrated_storage is None:
        _integrated_storage = IntegratedStorageManager()
    return _integrated_storage
