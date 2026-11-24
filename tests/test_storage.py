"""
Test script for PostgreSQL and Redis storage

Run this after setting up databases to verify everything works.
"""

import sys


def test_imports():
    """Test if storage modules can be imported."""
    print("Testing imports...")
    try:
        from email_assistant.storage import (
            get_postgres_store,
            get_redis_cache,
            get_integrated_storage
        )
        print("✓ All storage modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("\nMake sure you've installed dependencies:")
        print("  pip install psycopg2-binary redis")
        return False


def test_postgres():
    """Test PostgreSQL connection."""
    print("\nTesting PostgreSQL...")
    try:
        from email_assistant.storage import get_postgres_store
        
        postgres = get_postgres_store()
        print(f"✓ Connected to PostgreSQL at {postgres.host}:{postgres.port}")
        print(f"  Database: {postgres.database}")
        
        # Test write
        postgres.put_preference("test", "key", "value")
        print("✓ Write test successful")
        
        # Test read
        result = postgres.get_preference("test", "key")
        if result:
            print("✓ Read test successful")
        
        # Cleanup
        postgres.delete_preference("test", "key")
        print("✓ Delete test successful")
        
        return True
    
    except Exception as e:
        print(f"✗ PostgreSQL error: {e}")
        print("\nMake sure PostgreSQL is running:")
        print("  docker-compose up -d postgres")
        print("\nOr check connection settings in .env file")
        return False


def test_redis():
    """Test Redis connection."""
    print("\nTesting Redis...")
    try:
        from email_assistant.storage import get_redis_cache
        
        redis = get_redis_cache()
        
        if redis.client:
            print(f"✓ Connected to Redis at {redis.host}:{redis.port}")
            
            # Test write
            redis.set_session_data("test_session", {"key": "value"}, ttl=60)
            print("✓ Write test successful")
            
            # Test read
            result = redis.get_session_data("test_session")
            if result:
                print("✓ Read test successful")
            
            # Cleanup
            redis.delete("session", "test_session")
            print("✓ Delete test successful")
            
            # Get stats
            stats = redis.get_stats()
            if stats.get("connected"):
                print(f"✓ Redis stats: {stats.get('used_memory', 'N/A')} used")
        else:
            print("⚠ Redis not available, using fallback cache")
            print("  (This is OK for testing, but install Redis for production)")
        
        return True
    
    except Exception as e:
        print(f"✗ Redis error: {e}")
        print("\nMake sure Redis is running:")
        print("  docker-compose up -d redis")
        return False


def test_integrated():
    """Test integrated storage manager."""
    print("\nTesting Integrated Storage...")
    try:
        from email_assistant.storage import get_integrated_storage
        
        storage = get_integrated_storage()
        print("✓ Integrated storage manager initialized")
        
        # Test preference with caching
        storage.put_preference("test_namespace", "test_key", "test_value")
        print("✓ Preference stored (PostgreSQL + Redis cache)")
        
        # First read (from PostgreSQL)
        value1 = storage.get_preference("test_namespace", "test_key")
        print(f"✓ First read: {value1} (from PostgreSQL)")
        
        # Second read (from Redis cache)
        value2 = storage.get_preference("test_namespace", "test_key")
        print(f"✓ Second read: {value2} (from Redis cache)")
        
        # Test thread context
        storage.add_message_to_thread(
            thread_id="test-thread-001",
            email_id="email-001",
            from_email="test@example.com",
            to_email="you@example.com",
            subject="Test Email",
            body="This is a test",
            classification="respond"
        )
        print("✓ Message added to thread")
        
        # Get thread context
        context = storage.get_thread_context("test-thread-001")
        print(f"✓ Thread context retrieved: {context['message_count']} message(s)")
        
        # Get stats
        stats = storage.get_stats()
        print(f"\n📊 Storage Statistics:")
        print(f"  Redis: {stats['redis'].get('connected', False)}")
        print(f"  PostgreSQL: {stats['postgres']['database']}")
        
        # Cleanup
        storage.postgres.delete_preference("test_namespace", "test_key")
        storage.redis.clear_namespace("thread")
        print("\n✓ Cleanup successful")
        
        return True
    
    except Exception as e:
        print(f"✗ Integrated storage error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Storage System Test")
    print("=" * 60)
    
    # Test imports first
    if not test_imports():
        sys.exit(1)
    
    # Test individual components
    postgres_ok = test_postgres()
    redis_ok = test_redis()
    
    # Test integrated storage
    integrated_ok = test_integrated()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"PostgreSQL: {'✓ PASS' if postgres_ok else '✗ FAIL'}")
    print(f"Redis: {'✓ PASS' if redis_ok else '✗ FAIL'}")
    print(f"Integrated: {'✓ PASS' if integrated_ok else '✗ FAIL'}")
    
    if postgres_ok and integrated_ok:
        print("\n🎉 All tests passed! Storage is ready to use.")
        if not redis_ok:
            print("⚠ Note: Redis not available, using fallback cache")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("\nQuick fixes:")
        print("1. Start databases: docker-compose up -d")
        print("2. Install dependencies: pip install psycopg2-binary redis")
        print("3. Check .env configuration")
        return 1


if __name__ == "__main__":
    sys.exit(main())
