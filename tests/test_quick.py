"""Quick test to see if interrupt works"""
import asyncio
from langgraph_sdk import get_client

async def test():
    client = get_client(url='http://localhost:2024')
    
    # Create test input
    test_input = {
        'email_input': {
            'id': 'test-123',
            'thread_id': 'thread-123',
            'from_email': 'sender@test.com',
            'to_email': 'me@test.com',
            'subject': 'Test Meeting',
            'page_content': 'Can we schedule a meeting this week?',
            'send_time': '2024-11-24T10:00:00'
        }
    }
    
    # Create thread and run
    print("Creating thread...")
    thread = await client.threads.create()
    thread_id = thread['thread_id']
    print(f'Thread: {thread_id}')
    
    print("Starting run...")
    run = await client.runs.create(
        thread_id=thread_id,
        assistant_id='email_assistant',
        input=test_input
    )
    print(f'Run: {run["run_id"]}')
    print(f'Initial status: {run["status"]}')
    
    # Wait and check status
    print("\nWaiting 10 seconds...")
    await asyncio.sleep(10)
    
    run_status = await client.runs.get(thread_id, run['run_id'])
    status = run_status['status']
    print(f'\nFinal status: {status}')
    
    if status == 'interrupted':
        print('\n✅ INTERRUPT WORKS!')
        print('Email should be in Agent Inbox "Interrupted" tab')
        state = await client.threads.get_state(thread_id)
        print(f'Next nodes: {state.get("next", [])}')
    elif status == 'success':
        print('\n❌ NO INTERRUPT - Workflow completed')
        state = await client.threads.get_state(thread_id)
        values = state.get('values', {})
        print(f'Classification: {values.get("classification_decision")}')
        print(f'Triage result: {values.get("triage_result", {})}')
    else:
        print(f'\n⚠️  Status: {status}')

if __name__ == '__main__':
    asyncio.run(test())
