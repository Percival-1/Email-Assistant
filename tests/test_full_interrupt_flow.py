"""Test complete interrupt and resume flow."""
import asyncio
from langgraph_sdk import get_client

async def test():
    client = get_client(url='http://localhost:2024')
    
    # Test input
    test_input = {
        'email_input': {
            'id': 'test-interrupt-flow',
            'thread_id': 'thread-interrupt-flow',
            'from_email': 'sender@test.com',
            'to_email': 'me@test.com',
            'subject': 'Urgent Meeting Request',
            'page_content': 'Hi, can we schedule an urgent meeting for tomorrow at 2 PM?',
            'send_time': '2024-11-24T10:00:00'
        }
    }
    
    # Step 1: Create thread and start run
    print("=" * 60)
    print("STEP 1: Starting workflow")
    print("=" * 60)
    thread = await client.threads.create()
    thread_id = thread['thread_id']
    print(f"Thread ID: {thread_id}\n")
    
    run = await client.runs.create(
        thread_id=thread_id,
        assistant_id='email_assistant',
        input=test_input
    )
    run_id = run['run_id']
    print(f"Run ID: {run_id}\n")
    
    # Step 2: Wait for interrupt
    print("=" * 60)
    print("STEP 2: Waiting for interrupt...")
    print("=" * 60)
    for i in range(30):
        await asyncio.sleep(1)
        run_status = await client.runs.get(thread_id, run_id)
        status = run_status['status']
        
        if status == 'interrupted':
            print(f"\n✅ INTERRUPT DETECTED after {i+1}s!")
            break
        elif status in ['success', 'error']:
            print(f"\n❌ Run completed without interrupt: {status}")
            return
        
        if i % 5 == 0:
            print(f"[{i}s] Status: {status}")
    
    # Step 3: Get interrupt details
    print("\n" + "=" * 60)
    print("STEP 3: Interrupt details")
    print("=" * 60)
    state = await client.threads.get_state(thread_id)
    values = state.get('values', {})
    tasks = state.get('tasks', [])
    
    print(f"Draft response: {values.get('draft_response', '')[:100]}...")
    print(f"Tasks pending: {len(tasks)}")
    
    if tasks and tasks[0].get('interrupts'):
        interrupt_data = tasks[0]['interrupts'][0]
        print(f"\nInterrupt value:")
        print(f"  Type: {interrupt_data.get('value', {}).get('type')}")
        print(f"  Classification: {interrupt_data.get('value', {}).get('classification')}")
        draft_len = len(interrupt_data.get('value', {}).get('draft_response', ''))
        print(f"  Draft length: {draft_len} chars")
    
    # Step 4: Resume with approval
    print("\n" + "=" * 60)
    print("STEP 4: Resuming with approval")
    print("=" * 60)
    
    # Provide feedback as the resume value
    feedback = {
        "approved": True,
        "modified_response": None,
        "feedback": "Auto-approved by test script"
    }
    
    # Update state to resume
    await client.threads.update_state(
        thread_id=thread_id,
        values=feedback
    )
    print("Resume initiated\n")
    
    # Step 5: Wait for completion
    print("=" * 60)
    print("STEP 5: Monitoring completion")
    print("=" * 60)
    for i in range(20):
        await asyncio.sleep(1)
        state = await client.threads.get_state(thread_id)
        next_nodes = state.get('next', [])
        
        if i % 2 == 0:
            print(f"[{i}s] Next: {next_nodes}")
        
        if not next_nodes or next_nodes == []:
            print(f"\n✅ WORKFLOW COMPLETED!")
            values = state.get('values', {})
            print(f"\nFinal state:")
            print(f"  Human approved: {values.get('human_approved')}")
            print(f"  Send status: {values.get('send_status', 'Not set')}")
            print(f"  Human feedback: {values.get('human_feedback', 'None')}")
            break
    else:
        print(f"\n⏰ Still running after 20s")

if __name__ == '__main__':
    asyncio.run(test())
