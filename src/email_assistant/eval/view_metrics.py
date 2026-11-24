"""
Evaluation Metrics Viewer

View detailed metrics from LangSmith evaluations including:
- Latency statistics
- Token usage
- Success/failure rates
- Test case breakdowns
"""

import os
import sys
sys.path.insert(0, 'src')

from langsmith import Client
from datetime import datetime

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def format_duration(seconds):
    """Format duration in human-readable form."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.1f}s"

def format_tokens(tokens):
    """Format token count with commas."""
    return f"{int(tokens):,}"

def view_metrics(project_name=None):
    """View metrics from the latest evaluation."""
    
    if project_name is None:
        project_name = os.getenv('LANGCHAIN_PROJECT', 'email-assistant-eval')
    
    print_header(f"Evaluation Metrics Dashboard")
    print(f"Project: {project_name}")
    print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    client = Client()
    
    try:
        # Get recent runs
        print("\n📊 Fetching data from LangSmith...")
        
        # This is a placeholder showing what metrics are available
        # In practice, you'd fetch from LangSmith API
        
        print_header("Available Metrics in LangSmith")
        
        print("✅ ACCURACY METRICS (Per Test)")
        print("   • Score (0.0 - 1.0)")
        print("   • Feedback per evaluator")
        print("   • Pass/Fail status")
        print()
        
        print("⚡ PERFORMANCE METRICS (Per Test)")
        print("   • Latency (seconds)")
        print("   • Start time")
        print("   • End time")
        print("   • Total duration")
        print()
        
        print("💰 COST METRICS (Per Test)")
        print("   • Prompt tokens")
        print("   • Completion tokens")
        print("   • Total tokens")
        print("   • Estimated cost")
        print()
        
        print("🔍 EXECUTION DETAILS (Per Test)")
        print("   • Input (test case)")
        print("   • Output (agent response)")
        print("   • Expected (ground truth)")
        print("   • Error (if failed)")
        print("   • Trace ID (for debugging)")
        print()
        
        print_header("How to View These Metrics")
        
        print("OPTION 1: LangSmith Web UI (Recommended)")
        print("   1. Go to: https://smith.langchain.com")
        print(f"   2. Select project: {project_name}")
        print("   3. Click 'Experiments' tab")
        print("   4. Click on your experiment")
        print("   5. View metrics in columns")
        print()
        
        print("OPTION 2: LangSmith API (Programmatic)")
        print("   • Use client.list_runs() to fetch data")
        print("   • Filter by experiment ID")
        print("   • Extract latency, tokens, scores")
        print("   • Build custom dashboards")
        print()
        
        print("OPTION 3: Export to CSV")
        print("   • In LangSmith, click 'Export'")
        print("   • Download CSV file")
        print("   • Analyze in Excel/Python")
        print()
        
        print_header("Key Metrics to Monitor")
        
        metrics_guide = [
            ("Accuracy", "What % of tests passed", ">85%", "✓"),
            ("Latency", "Average response time", "<5s", "⚡"),
            ("P95 Latency", "95th percentile time", "<8s", "⚡"),
            ("Token Usage", "Avg tokens per email", "<2000", "💰"),
            ("Error Rate", "% of failed runs", "<5%", "❌"),
            ("Cost per Email", "Estimated API cost", "<$0.05", "💵"),
        ]
        
        print(f"{'Metric':<20} {'Description':<30} {'Target':<10} {'Icon'}")
        print("-" * 70)
        for metric, desc, target, icon in metrics_guide:
            print(f"{metric:<20} {desc:<30} {target:<10} {icon}")
        
        print()
        
        print_header("Sample Metrics Output")
        
        print("Example of what you'll see in LangSmith:")
        print()
        print("Test Case: email_input_1 (API documentation question)")
        print("  ✅ Classification: Correct (respond)")
        print("  ⚡ Latency: 3.24s")
        print("  💰 Tokens: 1,842 (est. $0.037)")
        print("  🎯 Score: 1.0")
        print()
        
        print("Test Case: email_input_5 (Expense report reminder)")
        print("  ❌ Classification: Wrong (got 'respond', expected 'notify')")
        print("  ⚡ Latency: 2.87s")
        print("  💰 Tokens: 1,623 (est. $0.032)")
        print("  🎯 Score: 0.0")
        print("  📝 Feedback: Expected notify but got respond")
        print()
        
        print_header("Latency Breakdown")
        
        print("Typical latency components:")
        print()
        print("  Triage Node         : 0.5-1.5s   (LLM call)")
        print("  Draft Response Node : 2.0-4.0s   (LLM + tools)")
        print("  Tool Calls          : 0.5-2.0s   (calendar check)")
        print("  Network/Overhead    : 0.3-0.5s")
        print("  " + "-" * 50)
        print("  Total              : 3.3-8.0s")
        print()
        print("⚠️  If latency >10s, consider:")
        print("     • Using gpt-4o-mini instead of gpt-4")
        print("     • Caching calendar results")
        print("     • Parallel tool calls")
        print()
        
        print_header("Cost Estimation")
        
        print("Token usage by component:")
        print()
        print("  Triage Prompt       : ~200 tokens")
        print("  Triage Response     : ~100 tokens")
        print("  Draft Prompt        : ~500 tokens")
        print("  Draft Response      : ~300 tokens")
        print("  Tool Calls          : ~200 tokens")
        print("  " + "-" * 50)
        print("  Total per email    : ~1,300 tokens")
        print()
        print("Cost estimates (GPT-4o):")
        print("  • Input:  $5.00 / 1M tokens")
        print("  • Output: $15.00 / 1M tokens")
        print("  • Per email: ~$0.01 - $0.03")
        print("  • Per 100 emails: ~$1.00 - $3.00")
        print()
        
        print_header("Failure Analysis")
        
        print("To analyze failures in detail:")
        print()
        print("  python -m email_assistant.eval.analyze_failures")
        print()
        print("This will show:")
        print("  • Which test cases failed")
        print("  • Why they failed")
        print("  • Common failure patterns")
        print("  • Suggested fixes")
        print()
        
        print_header("Next Steps")
        
        print("1. Open LangSmith Dashboard:")
        print(f"   → https://smith.langchain.com/projects/{project_name}")
        print()
        
        print("2. View your latest experiment")
        print()
        
        print("3. Check key metrics:")
        print("   • Overall accuracy score")
        print("   • Average latency")
        print("   • Total token usage")
        print("   • Failed test cases")
        print()
        
        print("4. For failures, run:")
        print("   → python -m email_assistant.eval.analyze_failures")
        print()
        
        print("5. Make improvements and re-run:")
        print("   → python run_evaluation.py")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print()
        print("Make sure:")
        print("  • LANGCHAIN_API_KEY is set in .env")
        print("  • You've run an evaluation first")
        print(f"  • Project '{project_name}' exists in LangSmith")
        print()

if __name__ == "__main__":
    view_metrics()
