"""Check what tool names are actually available."""
from email_assistant.tools.default.email_tools import write_email, Done, Question
from email_assistant.tools.gmail.calendar_tools_enhanced import (
    check_availability_enhanced,
    schedule_meeting_enhanced,
)

tools = [
    write_email,
    Done,
    Question,
    check_availability_enhanced,
    schedule_meeting_enhanced,
]

print("Tool names available:")
for tool in tools:
    print(f"  - {tool.name} (type: {type(tool).__name__})")
    
print("\nChecking if tools are callable:")
for tool in tools:
    try:
        # Check if it has the structure expected
        print(f"  {tool.name}: has 'invoke' = {hasattr(tool, 'invoke')}")
    except Exception as e:
        print(f"  ERROR with {tool}: {e}")
