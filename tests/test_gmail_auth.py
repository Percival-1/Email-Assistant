"""
Test Gmail Authentication
Run this FIRST to authenticate with your Gmail account
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
import json
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
]


def authenticate_gmail():
    """Authenticate and get credentials."""
    creds = None

    # Check if token exists
    if os.path.exists("token.pickle"):
        print("📂 Found existing token...")
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🔐 Starting authentication flow...")
            print("    Browser will open - please sign in with your Gmail")
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials in both formats
        print("💾 Saving credentials...")

        # 1. Save as token.pickle (for backward compatibility)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

        # 2. Save as .secrets/token.json (for gmail_tools.py)
        secrets_dir = Path(".secrets")
        secrets_dir.mkdir(exist_ok=True)

        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }

        with open(secrets_dir / "token.json", "w") as f:
            json.dump(token_data, f, indent=2)

        print(f"   ✅ Saved token.pickle")
        print(f"   ✅ Saved .secrets/token.json")

    return creds


# Main test
print("=" * 60)
print("  Gmail Authentication Test")
print("=" * 60)

# Check for credentials.json
if not os.path.exists("credentials.json"):
    print("\n❌ Error: credentials.json not found!")
    print("\nPlease follow these steps:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create a new project")
    print("3. Enable Gmail API and Calendar API")
    print("4. Create OAuth credentials (Desktop app)")
    print("5. Download as credentials.json")
    print("6. Place it in project root")
    print("\nSee GMAIL_SETUP_GUIDE.md for detailed instructions")
    exit(1)

try:
    creds = authenticate_gmail()

    # Test Gmail API
    print("\n📧 Testing Gmail API...")
    gmail = build("gmail", "v1", credentials=creds)

    # Get profile
    profile = gmail.users().getProfile(userId="me").execute()
    email_address = profile.get("emailAddress")
    print(f"✅ Authenticated as: {email_address}")

    # List recent messages
    results = gmail.users().messages().list(userId="me", maxResults=5).execute()
    messages = results.get("messages", [])
    print(f"✅ Found {len(messages)} recent emails")

    # Show first email subject
    if messages:
        msg = gmail.users().messages().get(userId="me", id=messages[0]["id"]).execute()
        headers = msg["payload"]["headers"]
        subject = next(
            (h["value"] for h in headers if h["name"] == "Subject"), "No Subject"
        )
        print(f'   Most recent: "{subject[:50]}..."')

    # Test Calendar API
    print("\n📅 Testing Calendar API...")
    calendar = build("calendar", "v3", credentials=creds)
    calendars = calendar.calendarList().list().execute()
    cal_items = calendars.get("items", [])

    print(f"✅ Found {len(cal_items)} calendars:")
    for cal in cal_items[:3]:  # Show first 3
        print(f"   • {cal.get('summary', 'Unknown')}")

    print("\n" + "=" * 60)
    print("✅ All APIs connected successfully!")
    print("=" * 60)
    print(f"\n📧 Your email: {email_address}")
    print("📝 Update .env file with:")
    print(f"   EMAIL_ADDRESS={email_address}")
    print("\n🚀 You can now run the email assistant with real Gmail!")
    print("   Command: langgraph dev")

except FileNotFoundError:
    print("\n❌ Error: credentials.json not found!")
    print("Please download from Google Cloud Console")
    print("See GMAIL_SETUP_GUIDE.md for instructions")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure credentials.json is in project root")
    print("2. Check APIs are enabled in Google Cloud Console")
    print("3. Verify you added your email as test user")
    print("4. See GMAIL_SETUP_GUIDE.md for detailed setup")
