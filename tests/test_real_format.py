"""Test with format matching real Gmail emails."""
import asyncio
from langgraph_sdk import get_client

async def test():
    client = get_client(url='http://localhost:2024')
    
    # Match the format from your LangSmith screenshot
    test_input = {
        'email_input': {
            'from_email': 'john@example.com',
            'subject': 'Re: interview',
            'body': 'can we postponed it for the next Sunday at sharp 3 pm?',
            'to_email': 'me@example.com'
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
    
    for i in range(30):
        await asyncio.sleep(1)
        run_status = await client.runs.get(thread_id, run['run_id'])
        status = run_status['status']
        
        if i % 3 == 0:
            state = await client.threads.get_state(thread_id)
            values = state.get('values', {})
            draft = values.get('draft_response', '')
            print(f"[{i}s] Status={status}, Draft len={len(draft)}")
        
        if status == 'interrupted':
            print(f"\n✅ INTERRUPTED!")
            state = await client.threads.get_state(thread_id)
            draft = state['values'].get('draft_response', '')
            print(f"Draft: {draft[:200]}...")
            return
        elif status in ['success', 'error']:
            print(f"\n❌ Completed: {status}")
            return

if __name__ == '__main__':
    asyncio.run(test())
