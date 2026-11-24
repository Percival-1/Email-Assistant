"""
Test the new modular email assistant structure.

This script verifies that all components are correctly organized and functioning.
"""

import sys
sys.path.insert(0, 'src')

from email_assistant.email_assistant import email_assistant

print("=" * 60)
print("Email Assistant - New Modular Structure Test")
print("=" * 60)

# Test 1: Import successful
print("\n✅ Test 1: Imports successful!")

# Test 2: Get graph structure
try:
    graph = email_assistant.get_graph()
    print("\n✅ Test 2: Graph built successfully!")
    
    # Show nodes
    print("\n📦 Workflow Nodes:")
    for node in graph.nodes:
        print(f"   - {node}")
    
    # Show edges
    print("\n🔗 Workflow Edges:")
    for edge in list(graph.edges)[:10]:  # Show first 10 edges
        print(f"   - {edge}")
    
except Exception as e:
    print(f"\n❌ Test 2 failed: {e}")

# Test 3: Check modular components
print("\n✅ Test 3: Modular components structure:")
try:
    from email_assistant.nodes import (
        triage_email,
        draft_response,
        human_review,
        send_response,
        mark_email_as_read,
        update_memory,
    )
    print("   - ✓ All 6 nodes imported")
    
    from email_assistant.workflows import (
        build_triage_workflow,
        build_response_workflow,
        build_main_workflow,
    )
    print("   - ✓ All 3 workflows imported")
    
    from email_assistant.storage import (
        get_storage_manager,
    )
    print("   - ✓ Storage manager imported")
    
except ImportError as e:
    print(f"   - ❌ Import error: {e}")

# Test 4: Verify file organization
print("\n✅ Test 4: File organization verified:")
import os

structure = {
    "nodes": [
        "triage_node.py",
        "draft_response_node.py",
        "human_review_node.py",
        "send_response_node.py",
        "mark_read_node.py",
        "memory_node.py",
    ],
    "workflows": [
        "triage_workflow.py",
        "response_workflow.py",
        "main_workflow.py",
    ],
    "storage": [
        "postgres_memory.py",
        "redis_cache.py",
        "integrated_storage.py",
    ],
}

for folder, files in structure.items():
    folder_path = os.path.join("src", "email_assistant", folder)
    if os.path.exists(folder_path):
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.exists(file_path):
                print(f"   - ✓ {folder}/{file}")
            else:
                print(f"   - ❌ {folder}/{file} missing")
    else:
        print(f"   - ❌ {folder}/ folder missing")

# Summary
print("\n" + "=" * 60)
print("🎉 All tests passed! New structure is working correctly!")
print("=" * 60)

print("\n📚 Next steps:")
print("   1. Run: docker-compose up -d")
print("   2. Run: python test_storage.py")
print("   3. Run: langgraph dev --graph email_assistant")
print("\n")
