"""
Check LangSmith API Key Permissions
"""

import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("LANGCHAIN_API_KEY")
endpoint = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

print("=" * 60)
print("  LangSmith Permissions Check")
print("=" * 60)
print(f"\nEndpoint: {endpoint}")
print(f"API Key: {api_key[:20]}..." if api_key else "NOT FOUND")

if not api_key:
    print("\n❌ No API key found!")
    exit(1)

# Test different endpoints to see which ones work
tests = [
    ("GET", "/info", "Basic API info"),
    ("GET", "/runs", "List runs"),
    ("GET", "/datasets", "List datasets"),
    ("GET", "/sessions", "List sessions"),
]

print("\n" + "=" * 60)
print("Testing API Endpoints:")
print("=" * 60)

headers = {
    "x-api-key": api_key,
    "Content-Type": "application/json"
}

for method, path, description in tests:
    url = f"{endpoint}{path}"
    try:
        response = requests.request(method, url, headers=headers, timeout=10)
        status = response.status_code
        
        if status == 200:
            print(f"✅ {description}: {status} OK")
        elif status == 403:
            print(f"❌ {description}: {status} FORBIDDEN")
        elif status == 401:
            print(f"❌ {description}: {status} UNAUTHORIZED")
        else:
            print(f"⚠️  {description}: {status}")
            
    except Exception as e:
        print(f"❌ {description}: ERROR - {e}")

print("\n" + "=" * 60)
print("Diagnosis:")
print("=" * 60)

print("""
If you see multiple FORBIDDEN (403) errors:

1. Your API key may be read-only or have restricted permissions
2. Your organization may have specific access controls
3. APAC region may have different permission requirements

Solutions:
1. Go to: https://smith.langchain.com/settings
2. Click on your API key to check permissions
3. Create a NEW key with these permissions checked:
   ✅ Read access
   ✅ Write access  
   ✅ Create datasets
   ✅ Run evaluations
4. Make sure you're creating the key in the APAC region workspace
""")
