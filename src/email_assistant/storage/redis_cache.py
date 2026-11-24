"""
Redis Cache for Thread Context and In-Memory Storage

Fast cache for:
- Thread conversation history
- Recent email context
- Temporary session data
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import timedelta

import redis
from redis.exceptions import RedisError

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis-based cache for fast in-memory storage."""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        db: int = 0,
        password: str = None,
        decode_responses: bool = True,
        socket_timeout: int = 5,
        socket_connect_timeout: int = 5,
    ):
        """Initialize Redis connection.

        Args:
            host: Redis host (defaults to env REDIS_HOST)
            port: Redis port (defaults to env REDIS_PORT or 6379)
            db: Redis database number (defaults to 0)
            password: Redis password (defaults to env REDIS_PASSWORD)
            decode_responses: Decode responses to strings
            socket_timeout: Socket timeout in seconds
            socket_connect_timeout: Connection timeout in seconds
        """
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", "6379"))
        self.db = db
        self.password = password or os.getenv("REDIS_PASSWORD")

        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=decode_responses,
                socket_timeout=socket_timeout,
                socket_connect_timeout=socket_connect_timeout,
            )

            # Test connection
            self.client.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")

        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            logger.warning("Falling back to in-memory cache")
            self.client = None
            # Fallback to dict-based cache
            self._fallback_cache = {}

    def _get_key(self, namespace: str, key: str) -> str:
        """Generate Redis key with namespace.

        Args:
            namespace: Key namespace
            key: Key name

        Returns:
            Namespaced key
        """
        return f"{namespace}:{key}"

    # === Thread Context Methods ===

    def cache_thread_context(
        self, thread_id: str, context: Dict[str, Any], ttl: int = 3600  # 1 hour default
    ) -> bool:
        """Cache thread conversation context.

        Args:
            thread_id: Thread ID
            context: Thread context dict
            ttl: Time-to-live in seconds

        Returns:
            True if successful
        """
        try:
            if self.client:
                key = self._get_key("thread", thread_id)
                self.client.setex(key, ttl, json.dumps(context))
                return True
            else:
                # Fallback
                self._fallback_cache[f"thread:{thread_id}"] = context
                return True

        except Exception as e:
            logger.error(f"Error caching thread context: {e}")
            return False

    def get_thread_context(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get cached thread context.

        Args:
            thread_id: Thread ID

        Returns:
            Thread context dict or None
        """
        try:
            if self.client:
                key = self._get_key("thread", thread_id)
                data = self.client.get(key)
                if data:
                    return json.loads(data)
                return None
            else:
                # Fallback
                return self._fallback_cache.get(f"thread:{thread_id}")

        except Exception as e:
            logger.error(f"Error getting thread context: {e}")
            return None

    def add_message_to_thread(
        self, thread_id: str, message: Dict[str, Any], max_messages: int = 50
    ) -> bool:
        """Add a message to thread's message list.

        Args:
            thread_id: Thread ID
            message: Message dict
            max_messages: Maximum messages to keep

        Returns:
            True if successful
        """
        try:
            if self.client:
                key = self._get_key("thread_messages", thread_id)

                # Add message to list
                self.client.lpush(key, json.dumps(message))

                # Trim to max_messages
                self.client.ltrim(key, 0, max_messages - 1)

                # Set expiry (24 hours)
                self.client.expire(key, 86400)

                return True
            else:
                # Fallback
                list_key = f"thread_messages:{thread_id}"
                if list_key not in self._fallback_cache:
                    self._fallback_cache[list_key] = []
                self._fallback_cache[list_key].insert(0, message)
                self._fallback_cache[list_key] = self._fallback_cache[list_key][
                    :max_messages
                ]
                return True

        except Exception as e:
            logger.error(f"Error adding message to thread: {e}")
            return False

    def get_thread_messages(
        self, thread_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent messages from thread.

        Args:
            thread_id: Thread ID
            limit: Number of recent messages

        Returns:
            List of message dicts (most recent first)
        """
        try:
            if self.client:
                key = self._get_key("thread_messages", thread_id)
                messages = self.client.lrange(key, 0, limit - 1)
                return [json.loads(msg) for msg in messages]
            else:
                # Fallback
                list_key = f"thread_messages:{thread_id}"
                messages = self._fallback_cache.get(list_key, [])
                return messages[:limit]

        except Exception as e:
            logger.error(f"Error getting thread messages: {e}")
            return []

    # === Email Context Methods ===

    def cache_email_context(
        self, email_id: str, context: Dict[str, Any], ttl: int = 7200  # 2 hours
    ) -> bool:
        """Cache email processing context.

        Args:
            email_id: Email ID
            context: Email context
            ttl: Time-to-live in seconds

        Returns:
            True if successful
        """
        try:
            if self.client:
                key = self._get_key("email", email_id)
                self.client.setex(key, ttl, json.dumps(context))
                return True
            else:
                self._fallback_cache[f"email:{email_id}"] = context
                return True

        except Exception as e:
            logger.error(f"Error caching email context: {e}")
            return False

    def get_email_context(self, email_id: str) -> Optional[Dict[str, Any]]:
        """Get cached email context.

        Args:
            email_id: Email ID

        Returns:
            Email context or None
        """
        try:
            if self.client:
                key = self._get_key("email", email_id)
                data = self.client.get(key)
                if data:
                    return json.loads(data)
                return None
            else:
                return self._fallback_cache.get(f"email:{email_id}")

        except Exception as e:
            logger.error(f"Error getting email context: {e}")
            return None

    # === Session Data Methods ===

    def set_session_data(
        self, session_id: str, data: Dict[str, Any], ttl: int = 1800  # 30 minutes
    ) -> bool:
        """Store session data.

        Args:
            session_id: Session ID
            data: Session data
            ttl: Time-to-live in seconds

        Returns:
            True if successful
        """
        try:
            if self.client:
                key = self._get_key("session", session_id)
                self.client.setex(key, ttl, json.dumps(data))
                return True
            else:
                self._fallback_cache[f"session:{session_id}"] = data
                return True

        except Exception as e:
            logger.error(f"Error setting session data: {e}")
            return False

    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data.

        Args:
            session_id: Session ID

        Returns:
            Session data or None
        """
        try:
            if self.client:
                key = self._get_key("session", session_id)
                data = self.client.get(key)
                if data:
                    return json.loads(data)
                return None
            else:
                return self._fallback_cache.get(f"session:{session_id}")

        except Exception as e:
            logger.error(f"Error getting session data: {e}")
            return None

    # === Counter Methods ===

    def increment_counter(self, counter_name: str, amount: int = 1) -> int:
        """Increment a counter.

        Args:
            counter_name: Counter name
            amount: Amount to increment

        Returns:
            New counter value
        """
        try:
            if self.client:
                key = self._get_key("counter", counter_name)
                return self.client.incrby(key, amount)
            else:
                key = f"counter:{counter_name}"
                self._fallback_cache[key] = self._fallback_cache.get(key, 0) + amount
                return self._fallback_cache[key]

        except Exception as e:
            logger.error(f"Error incrementing counter: {e}")
            return 0

    def get_counter(self, counter_name: str) -> int:
        """Get counter value.

        Args:
            counter_name: Counter name

        Returns:
            Counter value
        """
        try:
            if self.client:
                key = self._get_key("counter", counter_name)
                value = self.client.get(key)
                return int(value) if value else 0
            else:
                return self._fallback_cache.get(f"counter:{counter_name}", 0)

        except Exception as e:
            logger.error(f"Error getting counter: {e}")
            return 0

    # === Cache Statistics ===

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dict with cache stats
        """
        try:
            if self.client:
                info = self.client.info()
                return {
                    "connected": True,
                    "used_memory": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "total_commands": info.get("total_commands_processed"),
                    "keyspace_hits": info.get("keyspace_hits"),
                    "keyspace_misses": info.get("keyspace_misses"),
                }
            else:
                return {
                    "connected": False,
                    "fallback_cache_size": len(self._fallback_cache),
                }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}

    # === Utility Methods ===

    def clear_namespace(self, namespace: str) -> int:
        """Clear all keys in a namespace.

        Args:
            namespace: Namespace to clear

        Returns:
            Number of keys deleted
        """
        try:
            if self.client:
                pattern = f"{namespace}:*"
                keys = self.client.keys(pattern)
                if keys:
                    return self.client.delete(*keys)
                return 0
            else:
                # Fallback
                prefix = f"{namespace}:"
                keys_to_delete = [
                    k for k in self._fallback_cache.keys() if k.startswith(prefix)
                ]
                for key in keys_to_delete:
                    del self._fallback_cache[key]
                return len(keys_to_delete)

        except Exception as e:
            logger.error(f"Error clearing namespace: {e}")
            return 0

    def delete(self, namespace: str, key: str) -> bool:
        """Delete a specific key.

        Args:
            namespace: Key namespace
            key: Key name

        Returns:
            True if deleted
        """
        try:
            if self.client:
                full_key = self._get_key(namespace, key)
                return self.client.delete(full_key) > 0
            else:
                full_key = f"{namespace}:{key}"
                if full_key in self._fallback_cache:
                    del self._fallback_cache[full_key]
                    return True
                return False

        except Exception as e:
            logger.error(f"Error deleting key: {e}")
            return False

    def exists(self, namespace: str, key: str) -> bool:
        """Check if key exists.

        Args:
            namespace: Key namespace
            key: Key name

        Returns:
            True if exists
        """
        try:
            if self.client:
                full_key = self._get_key(namespace, key)
                return self.client.exists(full_key) > 0
            else:
                full_key = f"{namespace}:{key}"
                return full_key in self._fallback_cache

        except Exception as e:
            logger.error(f"Error checking existence: {e}")
            return False

    def set_ttl(self, namespace: str, key: str, ttl: int) -> bool:
        """Update TTL for a key.

        Args:
            namespace: Key namespace
            key: Key name
            ttl: Time-to-live in seconds

        Returns:
            True if successful
        """
        try:
            if self.client:
                full_key = self._get_key(namespace, key)
                return self.client.expire(full_key, ttl)
            else:
                # Fallback doesn't support TTL
                return False

        except Exception as e:
            logger.error(f"Error setting TTL: {e}")
            return False

    def close(self):
        """Close Redis connection."""
        if self.client:
            try:
                self.client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis: {e}")


# Global instance
_redis_cache = None


def get_redis_cache() -> RedisCache:
    """Get or create global Redis cache instance.

    Returns:
        RedisCache instance
    """
    global _redis_cache
    if _redis_cache is None:
        _redis_cache = RedisCache()
    return _redis_cache
