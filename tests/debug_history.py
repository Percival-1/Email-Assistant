"""Debug the workflow execution history"""
import asyncio
from langgraph_sdk import get_client

async def debug():
    client = get_client(url='http://localhost:2024')
    thread_id = '01a20c94-f434-7e32-97ee-73582e1a38bc'  # From latest test
    
    print("Getting thread history...")
    history = await client.threads.get_history(thread_id)
    
    print(f"\n=== EXECUTION HISTORY ({len(history)} states) ===\n")
    
    for i, state in enumerate(history):
        values = state.get('values', {})
        tasks = state.get('tasks', [])
        next_nodes = state.get('next', [])
        
        print(f"\n--- State {i} ---")
        print(f"Next nodes to execute: {next_nodes}")
        
        if tasks:
            for task in tasks:
                print(f"Task: {task.get('name')} - {task.get('interrupts', [])}")
        
        # Show key state changes
        if values.get('classification_decision'):
            print(f"  classification_decision: {values['classification_decision']}")
        if values.get('triage_result'):
            print(f"  triage_result: {values['triage_result']}")
        if values.get('draft_response'):
            print(f"  draft_response: {values['draft_response'][:50]}...")
        if values.get('human_approved') is not None:
            print(f"  human_approved: {values['human_approved']}")

asyncio.run(debug())
