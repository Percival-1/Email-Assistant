"""
Approve interrupted threads and resume to send emails.

This script finds interrupted threads in LangSmith and approves them,
allowing the workflow to continue and send the email.
"""
import asyncio
from langgraph_sdk import get_client

async def approve_interrupts():
    client = get_client(url='http://localhost:2024')
    
    print("=" * 70)
    print("SEARCHING FOR INTERRUPTED THREADS")
    print("=" * 70)
    
    # Search for recent threads
    threads = await client.threads.search(limit=20)
    
    interrupted_threads = []
    
    for thread in threads:
        thread_id = thread['thread_id']
        
        try:
            # Get thread state
            state = await client.threads.get_state(thread_id)
            tasks = state.get('tasks', [])
            
            # Check if thread has interrupts
            if tasks:
                for task in tasks:
                    if task.get('interrupts'):
                        interrupted_threads.append({
                            'thread_id': thread_id,
                            'state': state,
                            'task': task
                        })
                        break
        except Exception as e:
            # Skip threads with errors
            continue
    
    if not interrupted_threads:
        print("\n❌ No interrupted threads found")
        print("\nTip: Run the Gmail watcher and send a test email first:")
        print("     python gmail_watcher_agent_inbox.py")
        return
    
    print(f"\n✅ Found {len(interrupted_threads)} interrupted thread(s)\n")
    
    # Process each interrupted thread
    for i, item in enumerate(interrupted_threads, 1):
        thread_id = item['thread_id']
        state = item['state']
        task = item['task']
        
        print("=" * 70)
        print(f"THREAD {i}: {thread_id}")
        print("=" * 70)
        
        # Get interrupt details
        interrupt_data = task['interrupts'][0]
        interrupt_value = interrupt_data.get('value', {})
        
        draft = interrupt_value.get('draft', '')
        original_email = interrupt_value.get('original_email', {})
        
        print(f"\nFrom: {original_email.get('from', 'Unknown')}")
        print(f"Subject: {original_email.get('subject', 'Unknown')}")
        print(f"\nDraft ({len(draft)} chars):")
        print("-" * 70)
        print(draft[:300] + ("..." if len(draft) > 300 else ""))
        print("-" * 70)
        
        # Ask for approval
        print("\nOptions:")
        print("  [a] Approve and send")
        print("  [e] Edit draft then send")
        print("  [s] Skip this thread")
        print("  [q] Quit")
        
        choice = input("\nYour choice: ").lower().strip()
        
        if choice == 'q':
            print("\n👋 Exiting...")
            break
        elif choice == 's':
            print("⏭️  Skipped")
            continue
        elif choice == 'e':
            print(f"\nCurrent draft:\n{draft}\n")
            new_draft = input("Enter modified draft (or press Enter to keep original): ").strip()
            if new_draft:
                draft = new_draft
                print("✏️  Draft updated")
        
        # Approve and resume
        print(f"\n🚀 Approving and resuming thread...")
        
        try:
            # Resume with approval - pass the modified dict back
            await client.threads.update_state(
                thread_id=thread_id,
                values={
                    "draft": draft,
                    "approved": True,
                    "original_email": original_email
                }
            )
            
            print("✅ Thread resumed!")
            
            # Wait a bit for execution
            print("\n⏳ Waiting for email to send...")
            await asyncio.sleep(5)
            
            # Check final state
            final_state = await client.threads.get_state(thread_id)
            final_values = final_state.get('values', {})
            
            send_status = final_values.get('send_status')
            if send_status:
                print(f"📧 Send status: {send_status}")
            else:
                print("⚠️  Send status not available yet")
                
            print(f"   Human approved: {final_values.get('human_approved', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Error resuming thread: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)

if __name__ == '__main__':
    asyncio.run(approve_interrupts())
