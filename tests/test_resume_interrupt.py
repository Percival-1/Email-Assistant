"""Test resuming from interrupt with feedback."""
import asyncio
from langgraph_sdk import get_client

async def test_resume():
    client = get_client(url='http://localhost:2024')
    
    # Use the thread ID from your LangSmith run
    # Replace this with your actual thread ID
    thread_id = input("Enter thread ID from LangSmith: ").strip()
    
    if not thread_id:
        print("❌ No thread ID provided")
        return
    
    print(f"\n1. Getting current state for thread: {thread_id}")
    state = await client.threads.get_state(thread_id)
    
    print(f"\nCurrent status: {state.get('next', [])}")
    print(f"Tasks: {len(state.get('tasks', []))} pending")
    
    # Check if there's an interrupt
    if state.get('tasks'):
        print(f"\n✅ Interrupt detected!")
        task = state['tasks'][0]
        print(f"   Interrupt ID: {task.get('interrupts', [{}])[0].get('id') if task.get('interrupts') else 'N/A'}")
        
        # Resume with approval
        print(f"\n2. Resuming with approval...")
        feedback = {
            "approved": True,
            "modified_response": None,  # None = use original draft
            "feedback": "Approved via test script"
        }
        
        # Update state to resume
        result = await client.threads.update_state(
            thread_id=thread_id,
            values=feedback,
            as_node="human_review"
        )
        
        print(f"   Resume result: {result}")
        
        # Monitor completion
        print(f"\n3. Monitoring completion...")
        for i in range(10):
            await asyncio.sleep(2)
            state = await client.threads.get_state(thread_id)
            next_nodes = state.get('next', [])
            print(f"   [{i*2}s] Next: {next_nodes}")
            
            if not next_nodes:
                print(f"\n✅ Workflow completed!")
                values = state.get('values', {})
                print(f"   Send status: {values.get('send_status', 'N/A')}")
                break
    else:
        print(f"\n❌ No interrupt found in this thread")
        print(f"   Next: {state.get('next', [])}")

if __name__ == '__main__':
    asyncio.run(test_resume())
