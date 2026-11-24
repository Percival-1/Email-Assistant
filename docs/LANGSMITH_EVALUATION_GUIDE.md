# LangSmith Evaluation Guide

Complete guide to evaluate your email assistant using LangSmith.

## 🎯 What You'll Evaluate

1. **Triage Accuracy** - Does it correctly classify emails (respond/notify/ignore)?
2. **Response Quality** - Are the generated responses appropriate?
3. **Tool Usage** - Does it call the right tools (calendar, send email)?
4. **Thread Context** - Does it maintain conversation history?

## 📋 Prerequisites

### 1. Install Dependencies

```bash
# Already in pyproject.toml, but verify
pip install langsmith matplotlib pandas
```

### 2. Set Up LangSmith

**Get API Keys:**
1. Go to [smith.langchain.com](https://smith.langchain.com)
2. Create account or sign in
3. Go to Settings → API Keys
4. Create new API key

**Set Environment Variables:**

Add to your `.env` file:
```bash
# LangSmith Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=email-assistant-eval

# Your OpenAI key
OPENAI_API_KEY=your_openai_key_here
```

**Or set in terminal:**

```bash
# Windows (PowerShell)
$env:LANGCHAIN_TRACING_V2="true"
$env:LANGCHAIN_API_KEY="your_key_here"
$env:LANGCHAIN_PROJECT="email-assistant-eval"

# Linux/Mac
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your_key_here
export LANGCHAIN_PROJECT=email-assistant-eval
```

## 🧪 Evaluation Types

### 1. Triage Evaluation (Basic)

Tests if the assistant correctly classifies emails.

**Run it:**
```bash
cd d:\Agents\LangGraph\agents-from-scratch
python -m email_assistant.eval.evaluate_triage
```

**What it checks:**
- ✅ Email classification (respond/notify/ignore)
- ✅ Runs on 16 test emails
- ✅ Generates comparison chart

**Output:**
- Results in LangSmith dashboard
- Chart saved to `eval/results/triage_comparison_TIMESTAMP.png`

### 2. End-to-End Evaluation (Advanced)

Tests the complete workflow including response generation.

**Run it:**
```bash
python -m email_assistant.eval.evaluate_end_to_end
```

**What it checks:**
- ✅ Triage classification
- ✅ Response quality
- ✅ Tool calls (calendar, send email)
- ✅ Response appropriateness

### 3. Thread Context Evaluation

Tests conversation memory and context tracking.

**Run it:**
```bash
python -m email_assistant.eval.evaluate_thread_context
```

**What it checks:**
- ✅ Maintains thread history
- ✅ Remembers previous messages
- ✅ Uses context in responses

## 📊 Understanding Results

### In LangSmith Dashboard

1. Go to [smith.langchain.com](https://smith.langchain.com)
2. Select your project: `email-assistant-eval`
3. Click "Datasets" to see test data
4. Click "Experiments" to see evaluation runs

**Metrics to watch:**
- **Accuracy**: % of correct classifications
- **Latency**: Response time
- **Token Usage**: Cost estimation
- **Error Rate**: Failed runs

### Local Results

**Chart Output:**
```
eval/results/
├── triage_comparison_20250124_153045.png
├── end_to_end_results_20250124_153120.png
└── thread_context_results_20250124_153145.png
```

## 🎨 Custom Evaluators

### Create Your Own Evaluator

```python
from langsmith import Client
from langsmith import testing as t

def my_custom_evaluator(outputs: dict, reference_outputs: dict) -> bool:
    """Your custom evaluation logic."""
    # Check if response mentions specific keywords
    response = outputs.get("response", "").lower()
    expected = reference_outputs.get("expected_keywords", [])
    
    return any(keyword in response for keyword in expected)

# Run evaluation
client = Client()
client.evaluate(
    target_function,
    data="your-dataset",
    evaluators=[my_custom_evaluator],
    experiment_prefix="Custom Eval"
)
```

## 🔍 Evaluation Best Practices

### 1. Start Small
```bash
# Test with 5 emails first
python -m email_assistant.eval.evaluate_triage --limit 5
```

### 2. Iterate on Prompts
1. Run evaluation
2. Check failures in LangSmith
3. Update prompts in `src/email_assistant/prompts.py`
4. Re-run evaluation
5. Compare results

### 3. Track Experiments
```python
# Name your experiments clearly
experiment_prefix = "v1-baseline"  # First run
experiment_prefix = "v2-improved-triage"  # After changes
experiment_prefix = "v3-with-context"  # After adding features
```

### 4. Use Tags
```python
client.evaluate(
    target_function,
    data=dataset_name,
    evaluators=[evaluator],
    metadata={"version": "v2", "prompt_change": "added context"}
)
```

## 📈 Improving Scores

### Low Triage Accuracy?

**Check:**
1. Triage prompt in `prompts.py`
2. Classification logic in `nodes/triage_node.py`
3. Test cases in `eval/email_dataset.py`

**Fix:**
```python
# Update TRIAGE_SYSTEM_PROMPT in prompts.py
TRIAGE_SYSTEM_PROMPT = """
Your improved prompt here...
Add more examples, clearer guidelines...
"""
```

### Poor Response Quality?

**Check:**
1. Draft prompt in `prompts.py`
2. Response generation in `nodes/draft_response_node.py`
3. Tool availability

**Fix:**
```python
# Update DRAFT_SYSTEM_PROMPT
DRAFT_SYSTEM_PROMPT = """
Add more guidelines for professional tone,
specific response patterns, etc.
"""
```

### Wrong Tool Calls?

**Check:**
1. Tool descriptions in `tools/base.py`
2. Tool binding in `nodes/draft_response_node.py`

**Fix:**
```python
# Make tool descriptions more explicit
@tool
def schedule_meeting(...):
    """
    Schedule a meeting in Google Calendar.
    
    USE THIS TOOL when:
    - User explicitly asks to schedule/set up a meeting
    - You need to block time on the calendar
    
    DO NOT use for:
    - Just checking availability (use check_calendar_availability)
    """
```

## 🎯 Evaluation Workflow

```
1. Baseline Evaluation
   ↓
   Run: python -m email_assistant.eval.evaluate_triage
   ↓
   Check: LangSmith dashboard for scores
   
2. Identify Issues
   ↓
   Look at: Failed test cases
   ↓
   Analyze: Why did it fail?
   
3. Make Improvements
   ↓
   Update: Prompts, logic, or tools
   ↓
   Document: What you changed
   
4. Re-evaluate
   ↓
   Run: Same evaluation with new prefix
   ↓
   Compare: Old vs new scores
   
5. Iterate
   ↓
   Repeat: Until scores are acceptable
```

## 📋 Evaluation Checklist

Before considering your assistant "ready":

- [ ] **Triage Accuracy** > 85%
- [ ] **Response Quality** > 80% (human review)
- [ ] **Tool Calls** > 90% correct
- [ ] **Latency** < 5 seconds per email
- [ ] **Error Rate** < 5%
- [ ] **Context Retention** > 85%

## 🚨 Common Issues

### 1. "Module not found: langsmith"
```bash
pip install langsmith
```

### 2. "Authentication error"
```bash
# Check your API key
echo $env:LANGCHAIN_API_KEY
# Should output your key
```

### 3. "Dataset not found"
```bash
# The script creates it automatically on first run
# Just run the evaluation again
```

### 4. "No data in results"
```bash
# Check that LANGCHAIN_TRACING_V2=true
echo $env:LANGCHAIN_TRACING_V2
```

## 🎓 Next Steps

### Beginner
1. ✅ Run basic triage evaluation
2. ✅ View results in LangSmith
3. ✅ Check the generated chart

### Intermediate
1. ✅ Run end-to-end evaluation
2. ✅ Create custom evaluators
3. ✅ Compare multiple experiments

### Advanced
1. ✅ Set up CI/CD evaluation pipeline
2. ✅ Create custom datasets
3. ✅ Build regression testing

## 📚 Resources

- **LangSmith Docs**: https://docs.smith.langchain.com/
- **Evaluation Guide**: https://docs.smith.langchain.com/evaluation
- **Example Evaluators**: https://docs.smith.langchain.com/evaluation/evaluators

## 💡 Tips

1. **Tag everything**: Use descriptive experiment names
2. **Document changes**: Note what you modified
3. **Compare visually**: Use LangSmith comparison view
4. **Test incrementally**: Small changes, frequent tests
5. **Monitor costs**: Check token usage in dashboard

---

**Ready to evaluate?** Start with:
```bash
python -m email_assistant.eval.evaluate_triage
```

Then check your results at: [smith.langchain.com](https://smith.langchain.com)
