"""
Gmail Watcher - Agent Inbox Integration (Async)

Automatically processes emails from Gmail via LangGraph API.
Tracks processed emails to prevent duplicates.

Usage:
    python gmail_watcher_agent_inbox.py --interval 5 --max-emails 10
"""

import time
import argparse
import asyncio
import json
from pathlib import Path
from datetime import datetime
from langgraph_sdk import get_client
from email_assistant.tools.gmail.gmail_tools import fetch_group_emails

# File to track processed emails
PROCESSED_EMAILS_FILE = Path(".langgraph_api") / "processed_emails.json"


def load_processed_emails():
    """Load set of already processed email IDs."""
    try:
        if PROCESSED_EMAILS_FILE.exists():
            with open(PROCESSED_EMAILS_FILE, "r") as f:
                data = json.load(f)
                return set(data.get("processed_ids", []))
    except Exception as e:
        print(f"[WARN] Could not load processed emails: {e}")

    return set()


def save_processed_emails(processed_ids):
    """Save set of processed email IDs."""
    try:
        # Ensure directory exists
        PROCESSED_EMAILS_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Keep only last 1000 IDs to prevent file from growing indefinitely
        ids_list = list(processed_ids)[-1000:]

        with open(PROCESSED_EMAILS_FILE, "w") as f:
            json.dump(
                {"processed_ids": ids_list, "last_updated": datetime.now().isoformat()},
                f,
                indent=2,
            )
    except Exception as e:
        print(f"[WARN] Could not save processed emails: {e}")


def mark_as_processed(email_id, processed_ids):
    """Mark an email as processed and save."""
    processed_ids.add(email_id)
    save_processed_emails(processed_ids)


async def process_gmail_inbox(email_address="me", minutes_since=10, max_emails=10):
    """Process unread emails from Gmail via LangGraph API (async)."""

    # Load processed emails
    processed_ids = load_processed_emails()
    print(f"[INFO] Already processed: {len(processed_ids)} email(s)")

    # Get client
    client = get_client(url="http://localhost:2024")

    # Test connection
    try:
        await client.threads.search()
        print(f"[OK] Connected to LangGraph server")
        print(f"[OK] Using graph: email_assistant")
    except Exception as e:
        print(f"[ERROR] Cannot connect to LangGraph server!")
        print(f"        Start it with: langgraph dev")
        print(f"        Error: {e}")
        return 0

    print(f"\n{'='*60}")
    print(f"[CHECK] Gmail inbox... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"{'='*60}")

    try:
        # Fetch emails
        emails_generator = fetch_group_emails(
            email_address=email_address, minutes_since=minutes_since
        )
        emails = list(emails_generator)

        if not emails:
            print("[OK] No new emails to process")
            return 0

        # Filter out already processed emails
        new_emails = [email for email in emails if email.get("id") not in processed_ids]

        if not new_emails:
            print(f"[OK] Found {len(emails)} email(s), but all already processed")
            return 0

        print(
            f"[OK] Found {len(new_emails)} NEW email(s) to process (filtered {len(emails) - len(new_emails)} already processed)"
        )
        print(f"[INFO] Sending to Agent Inbox for HITL approval...")

        processed_count = 0
        for idx, email in enumerate(new_emails[:max_emails], 1):
            email_id = email.get("id", "")

            print(f"\n--- Processing Email {idx}/{len(new_emails)} ---")
            print(f"ID: {email_id}")
            print(f"From: {email.get('from_email', 'Unknown')}")
            print(f"Subject: {email.get('subject', 'No Subject')[:60]}...")

            workflow_input = {
                "email_input": {
                    "id": email_id,
                    "thread_id": email.get("thread_id", ""),
                    "from_email": email.get("from_email", ""),
                    "to_email": email.get("to_email", email_address),
                    "subject": email.get("subject", ""),
                    "page_content": email.get("page_content", ""),
                    "send_time": email.get("send_time", ""),
                }
            }

            try:
                # Create thread (async)
                thread = await client.threads.create()
                thread_id = thread["thread_id"]

                print(f"[OK] Created thread: {thread_id}")

                # Start run (async)
                run = await client.runs.create(
                    thread_id=thread_id,
                    assistant_id="email_assistant",
                    input=workflow_input,
                )

                print(f"[OK] Started run: {run['run_id']}")
                print(f"[INFO] View in Agent Inbox: https://dev.agentinbox.ai")

                # Mark as processed
                mark_as_processed(email_id, processed_ids)
                print(f"[OK] Marked as processed")

                processed_count += 1

            except Exception as e:
                print(f"[FAIL] Error: {e}")
                import traceback

                traceback.print_exc()
                continue

        print(f"\n{'='*60}")
        print(f"[OK] Sent {processed_count}/{len(new_emails)} emails to Agent Inbox")
        print(f"{'='*60}")
        print(f"\n[INFO] Next steps:")
        print(f"       1. Open: https://dev.agentinbox.ai")
        print(f"       2. Go to 'Interrupted' tab")
        print(f"       3. Approve/edit/reject drafts")

        return processed_count

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback

        traceback.print_exc()
        return 0


def run_watcher(interval_minutes=5, max_emails=10):
    """Run watcher continuously."""
    print("=" * 60)
    print("  Gmail Watcher - Agent Inbox Integration")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  • Check interval: {interval_minutes} minutes")
    print(f"  • Agent Inbox: https://dev.agentinbox.ai")
    print(f"  • Tracking file: {PROCESSED_EMAILS_FILE}")
    print(f"\n[WATCH] Watching Gmail inbox...")
    print(f"Press Ctrl+C to stop\n")

    try:
        while True:
            # Process inbox (run async function)
            asyncio.run(
                process_gmail_inbox(
                    minutes_since=interval_minutes * 2,
                    max_emails=max_emails,
                )
            )

            # Wait
            wait_seconds = interval_minutes * 60
            print(f"\n[WAIT] Waiting {interval_minutes} minutes...")
            time.sleep(wait_seconds)

    except KeyboardInterrupt:
        print("\n\n[BYE] Stopped by user")


def run_once(minutes_since=30, max_emails=10):
    """Run once and exit."""
    return asyncio.run(
        process_gmail_inbox(minutes_since=minutes_since, max_emails=max_emails)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gmail Watcher - Agent Inbox Integration"
    )
    parser.add_argument(
        "--interval", type=int, default=5, help="Check interval in minutes"
    )
    parser.add_argument(
        "--max-emails", type=int, default=10, help="Max emails to process per check"
    )
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument(
        "--minutes-since", type=int, default=30, help="Fetch emails from last N minutes"
    )
    parser.add_argument(
        "--reset", action="store_true", help="Reset processed emails tracking"
    )

    args = parser.parse_args()

    # Reset tracking if requested
    if args.reset:
        try:
            if PROCESSED_EMAILS_FILE.exists():
                PROCESSED_EMAILS_FILE.unlink()
                print(f"[OK] Reset processed emails tracking")
            else:
                print(f"[INFO] No tracking file to reset")
        except Exception as e:
            print(f"[ERROR] Could not reset: {e}")
        exit(0)

    if args.once:
        processed = run_once(
            minutes_since=args.minutes_since, max_emails=args.max_emails
        )
        exit(0 if processed >= 0 else 1)
    else:
        run_watcher(interval_minutes=args.interval, max_emails=args.max_emails)
