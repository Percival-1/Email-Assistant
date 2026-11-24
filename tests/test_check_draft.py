"""Check if draft_response is being generated."""
import asyncio
from langgraph_sdk import get_client

async def test():
    client = get_client(url='http://localhost:2024')
    
    test_input = {
        'email_input': {
            'id': 'test-draft-check',
            'thread_id': 'thread-draft-check',
            'from_email': 'sender@test.com',
            'to_email': 'me@test.com',
            'subject': 'Meeting Request',
            'page_content': 'Can we meet at 2pm tomorrow?',
            'send_time': '2024-11-24T10:00:00'
        }
    }
    
    thread = await client.threads.create()
    thread_id = thread['thread_id']
    print(f"Thread: {thread_id}\n")
    
    run = await client.runs.create(
        thread_id=thread_id,
        assistant_id='email_assistant',
        input=test_input
    )
    
    # Monitor with detailed state checks
    for i in range(30):
        await asyncio.sleep(1)
        run_status = await client.runs.get(thread_id, run['run_id'])
        status = run_status['status']
        
        state = await client.threads.get_state(thread_id)
        values = state.get('values', {})
        next_nodes = state.get('next', [])
        
        draft = values.get('draft_response', '')
        classification = values.get('classification_decision', '')
        
        if i % 3 == 0:
            print(f"[{i}s] Status={status}, Next={next_nodes}")
            print(f"     Classification={classification}, Draft len={len(draft)}")
        
        if status == 'interrupted':
            print(f"\n✅ INTERRUPTED!")
            print(f"Draft: {draft[:200]}")
            return
        elif status in ['success', 'error']:
            print(f"\n❌ Completed: {status}")
            print(f"Draft: {draft if draft else 'NONE'}...")
            return

if __name__ == '__main__':
    asyncio.run(test())
