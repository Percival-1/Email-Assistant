"""Check if environment variables are loaded in LangGraph server."""
import asyncio
from langgraph_sdk import get_client

async def test():
    client = get_client(url='http://localhost:2024')
    
    # Simple workflow that just echoes environment status
    test_input = {
        'email_input': {
            'from_email': 'test@example.com',
            'subject': 'Env Test',
            'body': 'Testing environment',
            'to_email': 'me@example.com'
        }
    }
    
    thread = await client.threads.create()
    thread_id = thread['thread_id']
    
    run = await client.runs.create(
        thread_id=thread_id,
        assistant_id='email_assistant',
        input=test_input
    )
    
    # Wait for completion
    for _ in range(20):
        await asyncio.sleep(2)
        run_status = await client.runs.get(thread_id, run['run_id'])
        if run_status['status'] in ['success', 'error', 'interrupted']:
            break
    
    # Check final state
    state = await client.threads.get_state(thread_id)
    draft = state['values'].get('draft_response', '')
    
    print(f"Status: {run_status['status']}")
    print(f"Draft: {draft[:200] if draft else 'EMPTY'}")
    
    # Look for error in draft
    if 'Error' in draft or 'credentials' in draft.lower():
        print("\n❌ PROBLEM: OpenAI credentials not loaded!")
        print("Draft contains error message:")
        print(draft)
    elif draft:
        print("\n✅ Draft generated successfully!")
    else:
        print("\n❌ No draft generated at all")

if __name__ == '__main__':
    asyncio.run(test())
