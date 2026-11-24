"""Query the specific thread from LangSmith screenshot."""
import asyncio
from langgraph_sdk import get_client

async def query():
    client = get_client(url='http://localhost:2024')
    
    # From your screenshot - try common thread ID patterns
    # The screenshot shows: Thread: 01a20c...
    # Let's list recent threads
    
    print("Fetching recent threads...")
    threads = await client.threads.search(limit=10)
    
    print(f"\nFound {len(threads)} threads:\n")
    for t in threads:
        tid = t.get('thread_id', 'unknown')
        created = t.get('created_at', 'unknown')
        print(f"  {tid}")
        print(f"    Created: {created}")
        
        # Get state
        try:
            state = await client.threads.get_state(tid)
            values = state.get('values', {})
            draft = values.get('draft_response', '')
            status = state.get('next', [])
            
            print(f"    Status: {status}")
            print(f"    Draft length: {len(draft)}")
            
            if draft:
                print(f"    Draft preview: {draft[:100]}")
            
            # Check for interrupts
            tasks = state.get('tasks', [])
            if tasks:
                print(f"    ✅ HAS INTERRUPT! Tasks: {len(tasks)}")
                for task in tasks:
                    if task.get('interrupts'):
                        for interrupt in task['interrupts']:
                            int_value = interrupt.get('value', {})
                            print(f"       Interrupt draft: {int_value.get('draft_response', '')[:80]}")
            
            print()
        except Exception as e:
            print(f"    Error getting state: {e}\n")

if __name__ == '__main__':
    asyncio.run(query())
