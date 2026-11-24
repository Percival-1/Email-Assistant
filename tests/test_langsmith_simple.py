"""
Simple test to see if data appears in LangSmith
"""

import os
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

client = Client()

print("=" * 60)
print("  LangSmith Connection Test")
print("=" * 60)

# Check endpoint
endpoint = os.getenv("LANGCHAIN_ENDPOINT")
project = os.getenv("LANGCHAIN_PROJECT")

print(f"\nEndpoint: {endpoint}")
print(f"Project: {project}")

# List datasets
print("\n📊 Your Datasets:")
try:
    datasets = list(client.list_datasets(limit=10))
    if datasets:
        for ds in datasets:
            print(f"  • {ds.name} (ID: {ds.id})")
            print(f"    URL: https://apac.smith.langchain.com/o/{ds.tenant_id}/datasets/{ds.id}")
    else:
        print("  No datasets found")
except Exception as e:
    print(f"  Error listing datasets: {e}")

# List recent runs
print("\n🏃 Recent Experiment Runs:")
try:
    # Get project info
    projects = list(client.list_projects(limit=5))
    if projects:
        for proj in projects:
            print(f"  • Project: {proj.name}")
            print(f"    URL: https://apac.smith.langchain.com/o/{proj.tenant_id}/projects/{proj.name}")
    else:
        print("  No projects found")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 60)
print("✅ Check these URLs in your browser!")
print("=" * 60)
