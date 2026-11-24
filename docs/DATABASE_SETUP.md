## 🗄️ Database Setup Guide

This guide helps you set up **PostgreSQL** (long-term memory) and **Redis** (fast caching) for the email assistant.

---

## Quick Start with Docker (Recommended)

### Step 1: Start Databases

```bash
# Start PostgreSQL and Redis with Docker Compose
docker-compose up -d

# Check if running
docker-compose ps
```

This starts:
- **PostgreSQL** on port `5432`
- **Redis** on port `6379`
- **pgAdmin** (Web UI) on `http://localhost:5050`
- **Redis Commander** (Web UI) on `http://localhost:8081`

### Step 2: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with database settings (already set for Docker)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=email_assistant
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_password

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

### Step 3: Install Dependencies

```bash
# Install new dependencies
pip install psycopg2-binary redis

# Or reinstall all
pip install -e .
```

### Step 4: Test Connection

```python
# test_storage.py
from email_assistant.storage import get_postgres_store, get_redis_cache

# Test PostgreSQL
postgres = get_postgres_store()
print("✓ PostgreSQL connected")

# Test Redis
redis = get_redis_cache()
print("✓ Redis connected")

# Get stats
print("\nRedis Stats:", redis.get_stats())
```

Run it:
```bash
python test_storage.py
```

---

## Manual Setup (Without Docker)

### PostgreSQL Setup

**Install PostgreSQL:**

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
brew services start postgresql

# Windows
# Download installer from postgresql.org
```

**Create Database:**

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE email_assistant;

# Create user (optional)
CREATE USER email_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE email_assistant TO email_user;

# Exit
\q
```

### Redis Setup

**Install Redis:**

```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis

# Windows
# Download from redis.io or use WSL
```

**Test Redis:**

```bash
redis-cli ping
# Should return: PONG
```

---

## 📊 Storage Architecture

### PostgreSQL (Long-Term Memory)

**What It Stores:**
- User preferences (triage, response style, calendar)
- Email history (all processed emails)
- Action items
- Learning feedback
- Analytics data

**Tables:**
1. `user_preferences` - Learned preferences
2. `email_history` - All emails processed
3. `action_items` - Extracted action items
4. `learning_feedback` - User edits for learning

**Schema:**
```sql
-- User preferences
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    namespace TEXT NOT NULL,
    preference_key TEXT NOT NULL,
    preference_value JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(namespace, preference_key)
);

-- Email history
CREATE TABLE email_history (
    id SERIAL PRIMARY KEY,
    email_id TEXT UNIQUE NOT NULL,
    thread_id TEXT NOT NULL,
    from_email TEXT NOT NULL,
    to_email TEXT NOT NULL,
    subject TEXT,
    body TEXT,
    classification TEXT,
    response TEXT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- And more... (automatically created)
```

### Redis (Fast Cache)

**What It Stores:**
- Thread conversation context (1 hour TTL)
- Recent messages (24 hours TTL)
- Session data (30 minutes TTL)
- Temporary counters

**Keys:**
- `thread:{thread_id}` - Thread context
- `thread_messages:{thread_id}` - Message list
- `email:{email_id}` - Email context
- `session:{session_id}` - Session data
- `counter:{name}` - Counters

---

## 🔄 How It Works Together

### Write Path (New Email)

```
Email Received
    ↓
Save to PostgreSQL (permanent)
    ↓
Cache in Redis (fast access)
    ↓
Process with cached context
```

### Read Path (Get Context)

```
Need Thread Context
    ↓
Check Redis Cache ──────→ Cache HIT? → Return cached data
    ↓ MISS
Load from PostgreSQL
    ↓
Cache in Redis (1 hour)
    ↓
Return data
```

### Benefits

| Operation | Storage | Why |
|-----------|---------|-----|
| **Get preferences** | Redis → Postgres | Fast cache, permanent storage |
| **Thread context** | Redis → Postgres | Fast repeated access |
| **Recent messages** | Redis → Postgres | Real-time performance |
| **Email history** | Postgres | Long-term analytics |
| **Learning feedback** | Postgres | Training data |

---

## 💻 Usage Examples

### Example 1: Store and Retrieve Preferences

```python
from email_assistant.storage import get_integrated_storage

storage = get_integrated_storage()

# Store preference
storage.put_preference(
    namespace="triage_preferences",
    key="user_preferences",
    value="Respond to meeting requests, ignore newsletters"
)

# Retrieve (uses cache)
prefs = storage.get_preference("triage_preferences", "user_preferences")
print(prefs)
```

### Example 2: Thread Context Management

```python
# Add message to thread
storage.add_message_to_thread(
    thread_id="thread-123",
    email_id="email-456",
    from_email="john@example.com",
    to_email="you@example.com",
    subject="Project Update",
    body="Can we meet next week?",
    classification="respond"
)

# Get thread context (cached)
context = storage.get_thread_context("thread-123")
print(f"Messages: {context['message_count']}")
print(f"Participants: {context['participants']}")

# Get recent messages (from cache)
messages = storage.get_recent_messages("thread-123", limit=5)
for msg in messages:
    print(f"{msg['from_email']}: {msg['subject']}")
```

### Example 3: Action Items

```python
# Add action item
action_id = storage.add_action_item(
    thread_id="thread-123",
    action_item="Schedule meeting with John for next week"
)

# Get pending action items
items = storage.get_action_items(status="pending")
for item in items:
    print(f"- {item['action_item']}")
```

### Example 4: Cache Statistics

```python
# Get storage stats
stats = storage.get_stats()

print("Redis Stats:")
print(f"  Memory: {stats['redis']['used_memory']}")
print(f"  Hits: {stats['redis']['keyspace_hits']}")
print(f"  Misses: {stats['redis']['keyspace_misses']}")

print("\nPostgreSQL:")
print(f"  Host: {stats['postgres']['host']}")
print(f"  Database: {stats['postgres']['database']}")
```

---

## 🧹 Maintenance

### Clear Redis Cache

```python
from email_assistant.storage import get_redis_cache

redis = get_redis_cache()

# Clear specific namespace
redis.clear_namespace("thread")

# Or use integrated storage
from email_assistant.storage import get_integrated_storage
storage = get_integrated_storage()
storage.clear_cache("thread")
```

### Backup PostgreSQL

```bash
# Backup database
pg_dump -U postgres email_assistant > backup.sql

# Restore database
psql -U postgres email_assistant < backup.sql
```

### Monitor Redis

```bash
# Connect to Redis CLI
redis-cli

# Monitor commands
MONITOR

# Check memory
INFO memory

# See all keys
KEYS *

# Clear all data (careful!)
FLUSHALL
```

---

## 🐛 Troubleshooting

### "Could not connect to PostgreSQL"

```bash
# Check if running
docker-compose ps
# or
pg_isready -h localhost -p 5432

# Check credentials in .env
cat .env | grep POSTGRES
```

### "Redis connection failed"

```bash
# Check if running
redis-cli ping

# Check Redis logs
docker-compose logs redis

# Test connection
python -c "import redis; r = redis.Redis(host='localhost', port=6379); print(r.ping())"
```

### "Table does not exist"

```python
# Reinitialize schema
from email_assistant.storage import get_postgres_store

postgres = get_postgres_store()
postgres._init_schema()
print("Schema reinitialized")
```

---

## 🔐 Production Considerations

### Security

```bash
# Use strong passwords
POSTGRES_PASSWORD=generate_strong_password_here

# Enable Redis authentication
redis-server --requirepass your_password
REDIS_PASSWORD=your_password
```

### Performance

```python
# Adjust connection pool size
postgres = PostgresMemoryStore(
    min_conn=5,  # Minimum connections
    max_conn=20  # Maximum connections
)
```

### Monitoring

```bash
# Monitor PostgreSQL connections
psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Monitor Redis memory
redis-cli INFO memory
```

---

## 📊 Database Schema Diagram

```
PostgreSQL (Persistent Storage)
├── user_preferences
│   ├── namespace (triage, response, calendar)
│   ├── preference_key
│   └── preference_value (JSONB)
├── email_history
│   ├── email_id (unique)
│   ├── thread_id (indexed)
│   ├── from_email, to_email
│   ├── subject, body
│   └── classification, response
├── action_items
│   ├── thread_id
│   ├── action_item
│   └── status (pending/completed)
└── learning_feedback
    ├── namespace
    ├── original_content
    └── edited_content

Redis (Fast Cache - TTL-based)
├── thread:{id} → Thread context (1h)
├── thread_messages:{id} → Message list (24h)
├── email:{id} → Email context (2h)
├── session:{id} → Session data (30m)
└── counter:{name} → Counters
```

---

## 🎯 Next Steps

1. **Start databases**: `docker-compose up -d`
2. **Test connection**: Run test_storage.py
3. **Run assistant**: It will use Postgres + Redis automatically
4. **Monitor**: Check pgAdmin and Redis Commander web UIs

**You're all set with production-grade storage!** 🚀

---

## 📚 Additional Resources

- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Redis Docs**: https://redis.io/documentation
- **Docker Compose**: https://docs.docker.com/compose/
- **psycopg2**: https://www.psycopg.org/docs/
- **redis-py**: https://redis-py.readthedocs.io/
