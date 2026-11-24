"""
Setup Token - Convert token.pickle to token.json for gmail_tools

This script:
1. Reads existing token.pickle
2. Converts it to JSON format
3. Saves as .secrets/token.json (for gmail_tools.py)
"""

import os
import pickle
import json
from pathlib import Path


def setup_token():
    """Convert token.pickle to .secrets/token.json"""

    print("=" * 60)
    print("  Token Setup - Converting token.pickle to token.json")
    print("=" * 60)

    # Check if token.pickle exists
    if not os.path.exists("token.pickle"):
        print("\n❌ token.pickle not found!")
        print("   Run this first: python test_gmail_auth.py")
        return False

    print("\n📂 Found token.pickle")

    # Load existing credentials
    print("📖 Reading credentials...")
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)

    # Create .secrets directory if it doesn't exist (at project root)
    secrets_dir = Path(".secrets")
    secrets_dir.mkdir(exist_ok=True)
    print(f"📁 Using .secrets directory at: {secrets_dir.absolute()}")

    # Convert credentials to JSON format
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }

    # Save as token.json
    token_json_path = secrets_dir / "token.json"
    with open(token_json_path, "w") as f:
        json.dump(token_data, f, indent=2)

    print(f"✅ Saved token to: {token_json_path}")

    # Verify it works
    print("\n🧪 Testing token...")
    from email_assistant.tools.gmail.gmail_tools import get_credentials

    creds_test = get_credentials()
    if creds_test:
        print("✅ Token loaded successfully by gmail_tools!")
        print(
            f"   Token expires: {creds.expiry if hasattr(creds, 'expiry') else 'N/A'}"
        )
        return True
    else:
        print("❌ Token could not be loaded by gmail_tools")
        return False


if __name__ == "__main__":
    success = setup_token()

    if success:
        print("\n" + "=" * 60)
        print("✅ Token setup complete!")
        print("=" * 60)
        print("\n🚀 You can now run the watcher with real Gmail:")
        print("   python gmail_watcher.py --interval 5")
        print("\n📧 It will process your real emails instead of mock data!")
    else:
        print("\n" + "=" * 60)
        print("❌ Token setup failed")
        print("=" * 60)
        print("\n📝 Steps to fix:")
        print("   1. Run: python test_gmail_auth.py")
        print("   2. Run: python setup_token.py")
