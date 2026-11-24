"""Check where _SECRETS_DIR is pointing"""
from pathlib import Path
import os

# Check what gmail_tools is using
from email_assistant.tools.gmail.gmail_tools import _SECRETS_DIR

print("=" * 60)
print("Checking _SECRETS_DIR configuration")
print("=" * 60)

print(f"\n_SECRETS_DIR: {_SECRETS_DIR}")
print(f"Absolute path: {_SECRETS_DIR.absolute()}")
print(f"Exists: {_SECRETS_DIR.exists()}")

token_path = _SECRETS_DIR / "token.json"
print(f"\ntoken.json path: {token_path}")
print(f"token.json exists: {token_path.exists()}")

if token_path.exists():
    print(f"✅ Token file found at: {token_path.absolute()}")
else:
    print(f"❌ Token file NOT found at: {token_path.absolute()}")

# Check where .secrets actually is
actual_secrets = Path(".secrets")
print(f"\n.secrets in current dir: {actual_secrets.absolute()}")
print(f"Exists: {actual_secrets.exists()}")

actual_token = actual_secrets / "token.json"
print(f".secrets/token.json exists: {actual_token.exists()}")

# Check current working directory
print(f"\nCurrent working directory: {Path.cwd()}")
