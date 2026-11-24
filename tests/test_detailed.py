"""Detailed test with state checking at each step"""
import asyncio
from langgraph_sdk import get_client
import time

async def test():
    client = get_client(url='http://localhost:2024')
    
    # Create test input
    test_input = {
        'email_input': {
            'id': 'test-456',
            'thread_id': 'thread-456',
            'from_email': 'sender@test.com',
            'to_email': 'me@test.com',
            'subject': 'Urgent Meeting Request',
            'page_content': 'Hi, can we schedule an urgent meeting for tomorrow at 2 PM? This is important.',
            'send_time': '2024-11-24T10:00:00'
        }
    }
    
    # Create thread and run
    print("1. Creating thread...")
    thread = await client.threads.create()
    thread_id = thread['thread_id']
    print(f"   Thread: {thread_id}")
    
    print("\n2. Starting run...")
    run = await client.runs.create(
        thread_id=thread_id,
        assistant_id='email_assistant',
        input=test_input
    )
    run_id = run['run_id']
    print(f"   Run: {run_id}")
    
    # Monitor status changes
    print("\n3. Monitoring execution...")
    for i in range(20):  # Check for 20 seconds
        await asyncio.sleep(1)
        run_status = await client.runs.get(thread_id, run_id)
        status = run_status['status']
        
        if i % 2 == 0:  # Every 2 seconds
            state = await client.threads.get_state(thread_id)
            values = state.get('values', {})
            next_nodes = state.get('next', [])
            
            print(f"\n   [{i}s] Status: {status}")
            if next_nodes:
                print(f"        Next: {next_nodes}")
            if values.get('classification_decision'):
                print(f"        Classification: {values.get('classification_decision')}")
            if values.get('draft_response'):
                draft_len = len(values.get('draft_response', ''))
                print(f"        Draft: {draft_len} chars")
        
        if status in ['interrupted', 'success', 'error']:
            break
    
    # Final state
    print(f"\n4. Final Status: {status}\n")
    
    if status == 'interrupted':
        print("✅ INTERRUPT DETECTED!")
        state = await client.threads.get_state(thread_id)
        values = state.get('values', {})
        
        print(f"\nState at interrupt:")
        print(f"  classification_decision: {values.get('classification_decision')}")
        print(f"  triage_result: {values.get('triage_result')}")
        draft = values.get('draft_response', '')
        print(f"  draft_response length: {len(draft)}")
        if draft:
            print(f"  draft preview: {draft[:200]}...")
        else:
            print(f"  draft preview: EMPTY! ❌")
        
    elif status == 'success':
        print("❌ NO INTERRUPT - Completed without pausing")
        state = await client.threads.get_state(thread_id)
        values = state.get('values', {})
        print(f"\nFinal state:")
        print(f"  classification: {values.get('classification_decision')}")
        print(f"  triage_result: {values.get('triage_result')}")
        print(f"  draft_response: {values.get('draft_response', '')[:100] if values.get('draft_response') else 'None'}...")
        print(f"  send_status: {values.get('send_status')}")
    
    return thread_id

if __name__ == '__main__':
    asyncio.run(test())
