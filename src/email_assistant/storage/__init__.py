"""
Storage Module for Email Assistant

Provides:
- PostgreSQL for long-term memory (preferences, history, analytics)
- Redis for fast caching (thread context, session data)
"""

from .postgres_memory import PostgresMemoryStore, get_postgres_store
from .redis_cache import RedisCache, get_redis_cache
from .integrated_storage import IntegratedStorageManager, get_integrated_storage

__all__ = [
    "PostgresMemoryStore",
    "get_postgres_store",
    "RedisCache",
    "get_redis_cache",
    "IntegratedStorageManager",
    "get_integrated_storage",
]
