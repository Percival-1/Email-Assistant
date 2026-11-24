"""
Gmail Watcher - Automatically processes emails from Gmail

This script runs continuously and:
1. Checks Gmail for unread emails every N minutes
2. Sends each email to LangGraph API server
3. Creates threads visible in Agent Inbox (dev.agentinbox.ai)
4. All runs automatically traced to LangSmith

Usage:
    python gmail_watcher.py --interval 5 --max-emails 10

Requirements:
    - LangGraph server running: langgraph dev
    - Agent Inbox configured: https://dev.agentinbox.ai
"""

import time
import argparse
from datetime import datetime
from langgraph_sdk import get_client
from email_assistant.tools.gmail.gmail_tools import fetch_group_emails

# LangGraph API client
client = get_client(url="http://localhost:2024")


def process_gmail_inbox(email_address="me", minutes_since=10, max_emails=10):
    """
    Fetch and process unread emails from Gmail via LangGraph API.

    Args:
        email_address: Gmail address (default: "me" for authenticated user)
        minutes_since: Look for emails from last N minutes
        max_emails: Maximum emails to process in one run

    Returns:
        Number of emails processed
    """
    # Check if LangGraph server is running
    try:
        assistants = client.assistants.list()
        print(f"[OK] Connected to LangGraph server")
        print(f"[OK] Available graphs: {[a['assistant_id'] for a in assistants]}")
    except Exception as e:
        print(f"[ERROR] LangGraph server not running!")
        print(f"        Start it with: langgraph dev")
        print(f"        Error: {e}")
        return 0

    print(f"\n{'='*60}")
    print(f"[CHECK] Gmail inbox... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"{'='*60}")

    try:
        # Fetch recent emails from Gmail (returns a generator/iterator)
        emails_generator = fetch_group_emails(
            email_address=email_address, minutes_since=minutes_since
        )

        # Convert generator to list so we can get the count
        emails = list(emails_generator)

        if not emails or len(emails) == 0:
            print("[OK] No new emails to process")
            return 0

        print(f"[OK] Found {len(emails)} email(s) to process")

        # Process each email
        processed_count = 0
        for idx, email in enumerate(emails[:max_emails], 1):
            print(f"\n--- Processing Email {idx}/{len(emails)} ---")
            print(f"From: {email.get('from_email', 'Unknown')}")
            print(f"Subject: {email.get('subject', 'No Subject')[:60]}...")

            # Prepare input for agent (matches StateInput and EmailData schemas)
            workflow_input = {
                "email_input": {
                    "id": email.get("id", ""),
                    "thread_id": email.get("thread_id", ""),
                    "from_email": email.get("from_email", ""),
                    "to_email": email.get("to_email", email_address),
                    "subject": email.get("subject", ""),
                    "page_content": email.get("page_content", ""),
                    "send_time": email.get("send_time", ""),
                }
            }

            try:
                # Run through agent workflow (automatically traced to LangSmith)
                result = email_assistant.invoke(workflow_input)

                # Log result
                classification = result.get("classification_decision", "unknown")
                print(f"[OK] Classified as: {classification}")

                # Show draft and get approval for respond/urgent emails
                if (
                    classification in ["respond", "urgent"]
                    and "draft_response" in result
                ):
                    draft = result.get("draft_response", "")

                    if draft:
                        print(f"\n{'='*60}")
                        print(f"[DRAFT] AI-Generated Response:")
                        print(f"{'='*60}")
                        print(draft)
                        print(f"{'='*60}")

                        # Get user approval
                        while True:
                            choice = (
                                input(
                                    "\n[HITL] Approve? (y)es / (e)dit / (n)o / (s)kip: "
                                )
                                .lower()
                                .strip()
                            )

                            if choice in ["y", "yes"]:
                                print("[OK] Draft approved - will send")
                                # TODO: Implement send_email function
                                print("[INFO] Email would be sent here")
                                break
                            elif choice in ["e", "edit"]:
                                print("\n[EDIT] Enter your edited version:")
                                print(
                                    "(Type your message, then press Enter twice to finish)"
                                )
                                print("=" * 60)
                                lines = []
                                while True:
                                    line = input()
                                    if line == "" and len(lines) > 0:
                                        break
                                    lines.append(line)
                                edited = "\n".join(lines)
                                if edited.strip():
                                    print(f"\n[OK] Using edited version")
                                    # TODO: Implement send_email with edited version
                                    print("[INFO] Edited email would be sent here")
                                    break
                                else:
                                    print("[WARN] Empty edit, try again")
                            elif choice in ["n", "no"]:
                                print("[OK] Draft rejected - will not send")
                                break
                            elif choice in ["s", "skip"]:
                                print("[OK] Skipped - saved for later")
                                break
                            else:
                                print("[ERROR] Invalid choice. Use: y/e/n/s")
                    else:
                        print("[WARN] No draft generated")
                else:
                    if classification == "ignore":
                        print(f"[OK] Email ignored (low priority)")
                    else:
                        print(f"[OK] No draft needed for: {classification}")

                print(f"[INFO] View in LangSmith: https://apac.smith.langchain.com")

                processed_count += 1

            except KeyboardInterrupt:
                print("\n[STOP] User interrupted")
                raise
            except Exception as e:
                print(f"[FAIL] Error processing email: {e}")
                import traceback

                traceback.print_exc()
                continue

        print(f"\n{'='*60}")
        print(f"[OK] Processed {processed_count}/{len(emails)} emails successfully")
        print(f"{'='*60}")
        print(f"\n[INFO] View all runs in LangSmith:")
        print(
            f"       https://apac.smith.langchain.com/o/a9d2a1c0-2d02-4186-85ab-0d3aaf410964/projects/p/email-assistant"
        )

        return processed_count

    except Exception as e:
        print(f"[ERROR] Error fetching emails: {e}")
        return 0


def run_watcher(interval_minutes=5, max_emails=10):
    """
    Run the Gmail watcher continuously.

    Args:
        interval_minutes: How often to check Gmail (in minutes)
        max_emails: Max emails to process per check
    """
    print("=" * 60)
    print("  Gmail Email Assistant - Watcher Started")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  • Check interval: {interval_minutes} minutes")
    print(f"  • Max emails per run: {max_emails}")
    print(f"  • Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n[WATCH] Watching Gmail inbox for new emails...")
    print(f"Press Ctrl+C to stop\n")

    try:
        while True:
            # Process inbox
            processed = process_gmail_inbox(
                minutes_since=interval_minutes * 2,  # Look back a bit further
                max_emails=max_emails,
            )

            # Wait for next check
            wait_seconds = interval_minutes * 60
            print(f"\n[WAIT] Waiting {interval_minutes} minutes until next check...")
            time.sleep(wait_seconds)

    except KeyboardInterrupt:
        print("\n\n[BYE] Watcher stopped by user")
        print(f"Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def run_once(minutes_since=30, max_emails=10):
    """
    Run once and exit (for cron jobs).

    Args:
        minutes_since: Look for emails from last N minutes
        max_emails: Max emails to process
    """
    processed = process_gmail_inbox(minutes_since=minutes_since, max_emails=max_emails)
    return processed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gmail Email Assistant Watcher")
    parser.add_argument(
        "--interval", type=int, default=5, help="Check interval in minutes (default: 5)"
    )
    parser.add_argument(
        "--max-emails",
        type=int,
        default=10,
        help="Maximum emails to process per check (default: 10)",
    )
    parser.add_argument(
        "--once", action="store_true", help="Run once and exit (for cron jobs)"
    )
    parser.add_argument(
        "--minutes-since",
        type=int,
        default=30,
        help="Look for emails from last N minutes (default: 30)",
    )

    args = parser.parse_args()

    if args.once:
        # Run once and exit (for cron jobs)
        processed = run_once(
            minutes_since=args.minutes_since, max_emails=args.max_emails
        )
        exit(0 if processed >= 0 else 1)
    else:
        # Run continuously
        run_watcher(interval_minutes=args.interval, max_emails=args.max_emails)
