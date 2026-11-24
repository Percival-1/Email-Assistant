"""
Failure Analysis Tool

Analyzes evaluation results and provides detailed failure reports.
Run this after evaluation to get detailed insights.
"""

import os
import sys
sys.path.insert(0, 'src')

from langsmith import Client
import pandas as pd
from datetime import datetime, timedelta

# Initialize client
client = Client()

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_section(text):
    print(f"\n{'-'*70}")
    print(f"  {text}")
    print(f"{'-'*70}\n")

def analyze_latest_experiment(project_name=None):
    """Analyze the most recent evaluation experiment."""
    
    if project_name is None:
        project_name = os.getenv('LANGCHAIN_PROJECT', 'email-assistant-eval')
    
    print_header(f"Failure Analysis for Project: {project_name}")
    
    # Get recent experiments
    try:
        # Get experiments from the last 7 days
        since = datetime.now() - timedelta(days=7)
        
        # Note: This is a simplified approach
        # In practice, you'd use the client to fetch experiments
        print("⚠️  To get detailed traces, use the LangSmith web interface:")
        print(f"   → https://smith.langchain.com/projects/{project_name}")
        print()
        
        # Provide analysis template
        print_section("What to Check in LangSmith Dashboard")
        
        print("1. EXPERIMENTS TAB:")
        print("   • Click on your latest experiment")
        print("   • Sort by 'Score' (ascending) to see failures first")
        print("   • Click on individual rows to see details")
        print()
        
        print("2. FOR EACH FAILURE:")
        print("   • Input: What email was tested")
        print("   • Output: What the agent produced")
        print("   • Expected: What was expected")
        print("   • Feedback: Why it failed")
        print("   • Latency: How long it took")
        print("   • Tokens: Cost estimation")
        print()
        
        print("3. TRACES TAB:")
        print("   • Shows step-by-step execution")
        print("   • See LLM calls, tool usage, errors")
        print("   • Click 'Playground' to test fixes")
        print()
        
        print_section("Common Failure Patterns")
        
        print("🔴 Classification Errors:")
        print("   Symptom: Marked 'respond' but should be 'ignore'")
        print("   Fix: Update TRIAGE_SYSTEM_PROMPT with clearer rules")
        print("   Location: src/email_assistant/prompts.py")
        print()
        
        print("🔴 Tool Call Errors:")
        print("   Symptom: Didn't call check_calendar_availability")
        print("   Fix: Improve tool descriptions, add examples")
        print("   Location: src/email_assistant/tools/")
        print()
        
        print("🔴 Response Quality:")
        print("   Symptom: Response too generic or missing details")
        print("   Fix: Add response templates to DRAFT_SYSTEM_PROMPT")
        print("   Location: src/email_assistant/prompts.py")
        print()
        
        print("🔴 High Latency:")
        print("   Symptom: Takes >10 seconds per email")
        print("   Fix: Use smaller model or add caching")
        print("   Location: src/email_assistant/nodes/")
        print()
        
        print("🔴 Runtime Errors:")
        print("   Symptom: Exception thrown, workflow crashes")
        print("   Fix: Add error handling, check inputs")
        print("   Location: Check stack trace in LangSmith")
        print()
        
        print_section("Failure Analysis Checklist")
        
        checklist = [
            "[ ] Opened LangSmith dashboard",
            "[ ] Found latest experiment",
            "[ ] Sorted by score to find failures",
            "[ ] Reviewed top 5 failed tests",
            "[ ] Noted common patterns",
            "[ ] Checked latency metrics",
            "[ ] Reviewed token usage",
            "[ ] Identified root causes",
            "[ ] Planned fixes",
        ]
        
        for item in checklist:
            print(f"  {item}")
        
        print()
        
        print_section("Export Failure Report")
        
        print("To create a detailed report:")
        print()
        print("1. In LangSmith, go to your experiment")
        print("2. Click 'Export' button")
        print("3. Download as CSV")
        print("4. Open in Excel/Google Sheets")
        print("5. Filter by score = 0.0 to see failures")
        print()
        
        print_section("Next Steps")
        
        print("After analyzing failures:")
        print()
        print("  1. Document patterns you found")
        print("  2. Update prompts or code")
        print("  3. Re-run evaluation:")
        print("     → python run_evaluation.py")
        print("  4. Compare scores:")
        print("     → Use LangSmith comparison view")
        print("  5. Iterate until satisfied")
        print()
        
        print_section("Quick Metrics Summary")
        
        print("Target Scores for Production:")
        print("  • Triage Accuracy    : >85%  ✓ Good  | >90%  ⭐ Excellent")
        print("  • Tool Accuracy      : >90%  ✓ Good  | >95%  ⭐ Excellent")
        print("  • Response Exists    : >95%  ✓ Good  | >98%  ⭐ Excellent")
        print("  • Success Rate       : >95%  ✓ Good  | >99%  ⭐ Excellent")
        print("  • Avg Latency        : <5s   ✓ Good  | <3s   ⭐ Excellent")
        print()
        
        print("For Learning Project:")
        print("  • Overall Score      : >70%  ✓ Good  | >80%  ⭐ Great")
        print()
        
    except Exception as e:
        print(f"❌ Error accessing LangSmith: {e}")
        print()
        print("Make sure:")
        print("  • LANGCHAIN_API_KEY is set")
        print("  • You've run an evaluation first")
        print("  • Project name is correct")
        print()

def generate_failure_template():
    """Generate a template for documenting failures."""
    
    template = """
# Evaluation Failure Analysis

**Date:** {date}
**Project:** {project}
**Experiment:** {experiment_name}

## Summary
- Total Tests: 
- Failed Tests: 
- Success Rate: 
- Avg Latency: 

## Failed Test Cases

### Test Case 1: [Test Name]
**Input:**
```
[Email content]
```

**Expected:**
- Classification: 
- Tools: 
- Response: 

**Actual:**
- Classification: 
- Tools: 
- Response: 

**Root Cause:**
[Why did it fail?]

**Fix:**
[What to change]

---

### Test Case 2: [Test Name]
...

## Patterns Identified

1. **Pattern:** [Description]
   - **Occurrences:** X times
   - **Impact:** [High/Medium/Low]
   - **Fix:** [What to do]

2. **Pattern:** [Description]
   ...

## Action Items

- [ ] Fix prompt X in prompts.py
- [ ] Update tool description Y
- [ ] Add error handling in Z
- [ ] Re-evaluate and compare

## Notes
[Additional observations]
"""
    
    # Save template
    os.makedirs('src/email_assistant/eval/results', exist_ok=True)
    template_path = 'src/email_assistant/eval/results/failure_analysis_template.md'
    
    with open(template_path, 'w') as f:
        f.write(template.format(
            date=datetime.now().strftime("%Y-%m-%d"),
            project=os.getenv('LANGCHAIN_PROJECT', 'email-assistant-eval'),
            experiment_name="[Your experiment name]"
        ))
    
    print(f"✅ Template saved to: {template_path}")
    print()
    print("Fill this out while analyzing failures in LangSmith!")
    print()

if __name__ == "__main__":
    print()
    analyze_latest_experiment()
    
    print_header("Generate Failure Analysis Template?")
    response = input("Create template for documenting failures? (y/n): ").strip().lower()
    
    if response == 'y':
        generate_failure_template()
    
    print()
    print("🌐 Open LangSmith Dashboard:")
    print(f"   → https://smith.langchain.com")
    print()
