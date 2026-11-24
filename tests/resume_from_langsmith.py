"""Resume the interrupted thread from LangSmith."""

import asyncio
from langgraph_sdk import get_client


async def resume_with_approval():
    client = get_client(url="http://localhost:2024")

    # From your LangSmith screenshot
    thread_id = "aa9dc2d3-e8fb-aa1d-3cd9-1dca6298b91"  # Your thread ID

    print(f"Resuming thread: {thread_id}")

    # Provide feedback to resume
    feedback = {
        "approved": True,
        "modified_response": None,  # Use original draft
        "feedback": "Approved",
    }

    # Resume execution by updating state (this will resume the interrupt)
    result = await client.threads.update_state(
        thread_id=thread_id,
        values=feedback,  # This becomes the return value of interrupt()
    )

    print(f"Resume initiated: {result}")

    # Monitor completion
    print("\nMonitoring completion...")
    for i in range(15):
        await asyncio.sleep(2)
        state = await client.threads.get_state(thread_id)
        next_nodes = state.get("next", [])
        values = state.get("values", {})

        print(f"[{i*2}s] Next: {next_nodes}")

        if not next_nodes or next_nodes == []:
            print(f"\n✅ Workflow completed!")
            print(f"Send status: {values.get('send_status', 'Not set')}")
            print(f"Human approved: {values.get('human_approved', 'Not set')}")
            break

        if i == 14:
            print(f"\n⏰ Still running after 30s")


if __name__ == "__main__":
    asyncio.run(resume_with_approval())
