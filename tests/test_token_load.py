"""Quick test to verify token loads correctly"""
from email_assistant.tools.gmail.gmail_tools import get_credentials

print("🧪 Testing token loading...")
creds = get_credentials()

if creds:
    print("✅ Token loaded successfully!")
    print(f"   Has token: {bool(creds.token)}")
    print(f"   Has refresh_token: {bool(creds.refresh_token)}")
    print(f"   Has client_id: {bool(creds.client_id)}")
    print(f"   Scopes: {creds.scopes}")
else:
    print("❌ Token failed to load")
