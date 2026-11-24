"""Test response_workflow in isolation to see if interrupt works."""
import asyncio
from langgraph_sdk import get_client

async def test():
    client = get_client(url='http://localhost:2024')
    
    # Test input - simulate state after triage
    test_input = {
        'email_input': {
            'email_id': 'test-999',
            'from_email': 'john@example.com',
            'to_email': 'me@example.com',
            'subject': 'Meeting at 2pm',
            'body': 'Can we schedule a meeting at 2pm tomorrow?',
        },
        'classification_decision': 'respond',  # This is what should_review checks
        'triage_result': {
            'classification': 'respond',
            'needs_review': False,
        }
    }
    
    # Create thread
    print("Creating thread...")
    thread = await client.threads.create()
    thread_id = thread['thread_id']
    print(f"Thread: {thread_id}\n")
    
    # Invoke directly
    print("Starting run...")
    run = await client.runs.create(
        thread_id=thread_id,
        assistant_id='email_assistant',
        input=test_input
    )
    run_id = run['run_id']
    print(f"Run: {run_id}\n")
    
    # Monitor
    print("Monitoring...")
    for i in range(30):
        await asyncio.sleep(1)
        run_status = await client.runs.get(thread_id, run_id)
        status = run_status['status']
        
        if i % 3 == 0:
            state = await client.threads.get_state(thread_id)
            values = state.get('values', {})
            next_nodes = state.get('next', [])
            
            print(f"[{i}s] Status: {status}, Next: {next_nodes}")
            
            if values.get('draft_response'):
                print(f"      Draft: {len(values['draft_response'])} chars")
            
        if status in ['interrupted', 'success', 'error']:
            print(f"\nFinal status: {status}")
            break
    
    # Check final state
    state = await client.threads.get_state(thread_id)
    values = state.get('values', {})
    
    if status == 'interrupted':
        print("\n✅ SUCCESS - Workflow interrupted!")
        print(f"Draft length: {len(values.get('draft_response', ''))}")
    else:
        print(f"\n❌ FAILED - Status: {status}")
        print(f"Draft: {values.get('draft_response', 'None')}")
        print(f"Send status: {values.get('send_status', 'None')}")
    
    return thread_id

if __name__ == '__main__':
    asyncio.run(test())
