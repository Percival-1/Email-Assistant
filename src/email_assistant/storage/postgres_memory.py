"""
PostgreSQL Storage for Long-Term Memory

Stores user preferences, learned behaviors, and historical data.
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from urllib.parse import quote_plus

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import SimpleConnectionPool

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class PostgresMemoryStore:
    """PostgreSQL-based long-term memory storage."""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        database: str = None,
        user: str = None,
        password: str = None,
        database_url: str = None,
        min_conn: int = 1,
        max_conn: int = 10,
    ):
        """Initialize PostgreSQL connection pool.

        Args:
            host: Database host (defaults to env POSTGRES_HOST)
            port: Database port (defaults to env POSTGRES_PORT or 5432)
            database: Database name (defaults to env POSTGRES_DB)
            user: Database user (defaults to env POSTGRES_USER)
            password: Database password (defaults to env POSTGRES_PASSWORD)
            database_url: Full database URL (optional, overrides individual params)
            min_conn: Minimum connections in pool
            max_conn: Maximum connections in pool
        """
        # Check for DATABASE_URL first (common in production)
        if database_url or os.getenv("DATABASE_URL"):
            conn_string = database_url or os.getenv("DATABASE_URL")
            self.host = None  # Will be parsed from URL
            self.port = None
            self.database = None
            self.user = None
            self.password = None
        else:
            # Build connection from individual params
            self.host = host or os.getenv("POSTGRES_HOST", "localhost")
            self.port = port or int(os.getenv("POSTGRES_PORT", "5432"))
            self.database = database or os.getenv("POSTGRES_DB", "email_assistant")
            self.user = user or os.getenv("POSTGRES_USER", "postgres")
            raw_password = password or os.getenv("POSTGRES_PASSWORD", "")

            # URL-encode password to handle special characters like @, #, etc.
            self.password = quote_plus(raw_password) if raw_password else ""

            # Build connection string with encoded password
            conn_string = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

        # Create connection pool
        try:
            self.pool = SimpleConnectionPool(min_conn, max_conn, conn_string)
            logger.info(
                f"Connected to PostgreSQL at {self.host or 'from URL'}:{self.port or ''}/{self.database or ''}"
            )

            # Initialize schema
            self._init_schema()

        except psycopg2.Error as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Get a connection from the pool."""
        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)

    def _init_schema(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # User preferences table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id SERIAL PRIMARY KEY,
                        namespace TEXT NOT NULL,
                        preference_key TEXT NOT NULL,
                        preference_value JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(namespace, preference_key)
                    )
                """)

                # Email history table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS email_history (
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
                    )
                """)

                # Create index on thread_id for fast lookups
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_thread_id 
                    ON email_history(thread_id)
                """)

                # Action items table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS action_items (
                        id SERIAL PRIMARY KEY,
                        thread_id TEXT NOT NULL,
                        action_item TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP
                    )
                """)

                # Learning feedback table (for memory updates)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS learning_feedback (
                        id SERIAL PRIMARY KEY,
                        namespace TEXT NOT NULL,
                        original_content JSONB,
                        edited_content JSONB,
                        feedback_type TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                conn.commit()
                logger.info("PostgreSQL schema initialized")

    # === User Preferences Methods ===

    def get_preference(self, namespace: str, key: str) -> Optional[Dict[str, Any]]:
        """Get user preference from storage.

        Args:
            namespace: Preference namespace (e.g., "triage_preferences")
            key: Preference key (e.g., "user_preferences")

        Returns:
            Preference value as dict or None if not found
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT preference_value, updated_at
                    FROM user_preferences
                    WHERE namespace = %s AND preference_key = %s
                """,
                    (namespace, key),
                )

                row = cur.fetchone()
                if row:
                    return dict(row)
                return None

    def put_preference(self, namespace: str, key: str, value: Any) -> bool:
        """Store or update user preference.

        Args:
            namespace: Preference namespace
            key: Preference key
            value: Preference value (will be JSON-encoded)

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Ensure value is JSON-serializable
                json_value = json.dumps(value) if not isinstance(value, str) else value

                cur.execute(
                    """
                    INSERT INTO user_preferences (namespace, preference_key, preference_value, updated_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (namespace, preference_key)
                    DO UPDATE SET 
                        preference_value = EXCLUDED.preference_value,
                        updated_at = CURRENT_TIMESTAMP
                """,
                    (namespace, key, Json(json_value)),
                )

                conn.commit()
                logger.info(f"Updated preference: {namespace}/{key}")
                return True

    def delete_preference(self, namespace: str, key: str) -> bool:
        """Delete a preference.

        Args:
            namespace: Preference namespace
            key: Preference key

        Returns:
            True if deleted
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM user_preferences
                    WHERE namespace = %s AND preference_key = %s
                """,
                    (namespace, key),
                )

                conn.commit()
                return cur.rowcount > 0

    def list_preferences(self, namespace: str) -> List[Dict[str, Any]]:
        """List all preferences in a namespace.

        Args:
            namespace: Preference namespace

        Returns:
            List of preference dicts
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT preference_key, preference_value, updated_at
                    FROM user_preferences
                    WHERE namespace = %s
                    ORDER BY updated_at DESC
                """,
                    (namespace,),
                )

                return [dict(row) for row in cur.fetchall()]

    # === Email History Methods ===

    def save_email(
        self,
        email_id: str,
        thread_id: str,
        from_email: str,
        to_email: str,
        subject: str,
        body: str,
        classification: str = None,
        response: str = None,
    ) -> bool:
        """Save email to history.

        Args:
            email_id: Unique email ID
            thread_id: Thread ID
            from_email: Sender email
            to_email: Recipient email
            subject: Email subject
            body: Email body
            classification: Triage classification
            response: Generated response

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO email_history 
                    (email_id, thread_id, from_email, to_email, subject, body, classification, response)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (email_id) DO UPDATE SET
                        classification = EXCLUDED.classification,
                        response = EXCLUDED.response,
                        processed_at = CURRENT_TIMESTAMP
                """,
                    (
                        email_id,
                        thread_id,
                        from_email,
                        to_email,
                        subject,
                        body,
                        classification,
                        response,
                    ),
                )

                conn.commit()
                return True

    def get_thread_history(
        self, thread_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get email history for a thread.

        Args:
            thread_id: Thread ID
            limit: Maximum number of emails to return

        Returns:
            List of email dicts
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM email_history
                    WHERE thread_id = %s
                    ORDER BY processed_at DESC
                    LIMIT %s
                """,
                    (thread_id, limit),
                )

                return [dict(row) for row in cur.fetchall()]

    # === Action Items Methods ===

    def add_action_item(self, thread_id: str, action_item: str) -> int:
        """Add an action item.

        Args:
            thread_id: Thread ID
            action_item: Action item description

        Returns:
            Action item ID
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO action_items (thread_id, action_item)
                    VALUES (%s, %s)
                    RETURNING id
                """,
                    (thread_id, action_item),
                )

                action_id = cur.fetchone()[0]
                conn.commit()
                return action_id

    def get_action_items(
        self, thread_id: str = None, status: str = "pending"
    ) -> List[Dict[str, Any]]:
        """Get action items.

        Args:
            thread_id: Optional thread ID filter
            status: Status filter (pending, completed)

        Returns:
            List of action item dicts
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if thread_id:
                    cur.execute(
                        """
                        SELECT *
                        FROM action_items
                        WHERE thread_id = %s AND status = %s
                        ORDER BY created_at DESC
                    """,
                        (thread_id, status),
                    )
                else:
                    cur.execute(
                        """
                        SELECT *
                        FROM action_items
                        WHERE status = %s
                        ORDER BY created_at DESC
                    """,
                        (status,),
                    )

                return [dict(row) for row in cur.fetchall()]

    def complete_action_item(self, action_id: int) -> bool:
        """Mark action item as completed.

        Args:
            action_id: Action item ID

        Returns:
            True if updated
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE action_items
                    SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """,
                    (action_id,),
                )

                conn.commit()
                return cur.rowcount > 0

    # === Learning Feedback Methods ===

    def save_feedback(
        self,
        namespace: str,
        original_content: Any,
        edited_content: Any,
        feedback_type: str,
    ) -> int:
        """Save learning feedback for analysis.

        Args:
            namespace: Feedback namespace
            original_content: Original content
            edited_content: Edited content
            feedback_type: Type of feedback (email, meeting, etc.)

        Returns:
            Feedback ID
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO learning_feedback 
                    (namespace, original_content, edited_content, feedback_type)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """,
                    (
                        namespace,
                        Json(original_content),
                        Json(edited_content),
                        feedback_type,
                    ),
                )

                feedback_id = cur.fetchone()[0]
                conn.commit()
                return feedback_id

    def get_recent_feedback(
        self, namespace: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent feedback for learning analysis.

        Args:
            namespace: Feedback namespace
            limit: Maximum number of feedback items

        Returns:
            List of feedback dicts
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM learning_feedback
                    WHERE namespace = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """,
                    (namespace, limit),
                )

                return [dict(row) for row in cur.fetchall()]

    def close(self):
        """Close all connections in pool."""
        if self.pool:
            self.pool.closeall()
            logger.info("PostgreSQL connection pool closed")


# Global instance
_postgres_store = None


def get_postgres_store() -> PostgresMemoryStore:
    """Get or create global PostgreSQL store instance.

    Returns:
        PostgresMemoryStore instance
    """
    global _postgres_store
    if _postgres_store is None:
        _postgres_store = PostgresMemoryStore()
    return _postgres_store
