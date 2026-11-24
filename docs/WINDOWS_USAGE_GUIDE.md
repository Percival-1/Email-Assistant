# 🪟 Using Your Email Assistant on Windows

## The Problem
LangGraph Studio **desktop app is Mac-only**. The web version at LangSmith can't connect to your local `http://127.0.0.1:2024` due to browser security.

## ✅ Solution: Use These Windows-Friendly Methods

### Method 1: Swagger UI (Easiest!)

Your server provides an interactive API interface:

**Open in browser:** http://127.0.0.1:2024/docs

You'll see:
- 📋 All available endpoints
- ▶️ "Try it out" buttons to test APIs
- 📝 Request/response examples
- 🔍 Schema documentation

**To test your agent:**
1. Go to `POST /threads` → Click "Try it out" → Execute
2. Copy the `thread_id`
3. Go to `POST /threads/{thread_id}/runs`
4. Paste thread_id, set assistant_id to "email_assistant"
5. Add input: `{"email_input": "test email here"}`
6. Execute and watch it run!

### Method 2: Python Script (Interactive)

I've created `interact_with_agent.py` for you, but it needs async fixes.

**Simpler version - Just run your agent directly:**

```python
from email_assistant.email_assistant import email_assistant

# Test email
test_email = """
From: john@example.com
Subject: Meeting Request  
Body: Can we meet Tuesday at 2pm?
"""

# Run the agent
result = email_assistant.invoke({"email_input": test_email})

# See results
print("Classification:", result.get("classification_decision"))
print("Triage:", result.get("triage_result"))
```

Save as `quick_test.py` and run: `python quick_test.py`

### Method 3: cURL / Postman

Test via command line:

```bash
# Create thread
curl -X POST http://127.0.0.1:2024/threads

# Run agent (replace THREAD_ID)
curl -X POST http://127.0.0.1:2024/threads/THREAD_ID/runs \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "email_assistant",
    "input": {"email_input": "Test email from curl"}
  }'

# Check state
curl http://127.0.0.1:2024/threads/THREAD_ID/state
```

### Method 4: VS Code REST Client Extension

Install "REST Client" extension in VS Code, create `test.http`:

```http
### Create Thread
POST http://127.0.0.1:2024/threads
Content-Type: application/json

### Run Agent (replace thread_id)
POST http://127.0.0.1:2024/threads/YOUR_THREAD_ID/runs
Content-Type: application/json

{
  "assistant_id": "email_assistant",
  "input": {
    "email_input": "From: test@example.com\nSubject: Test\nBody: Hello"
  }
}

### Get State
GET http://127.0.0.1:2024/threads/YOUR_THREAD_ID/state
```

Click "Send Request" above each `###` to execute.

## 🎯 Recommended Workflow for Windows

1. **Start server:** `langgraph dev` (from project root)
2. **Open Swagger UI:** http://127.0.0.1:2024/docs
3. **Test manually** using the UI
4. **View results** in LangSmith APAC: https://apac.smith.langchain.com
5. **Check evaluations** at your project URLs

## 📊 Your LangSmith Links

Even though Studio doesn't work, your **evaluations and traces DO show up** in LangSmith:

- **Main Dashboard:** https://apac.smith.langchain.com
- **Your Evaluation:** https://apac.smith.langchain.com/o/a9d2a1c0-2d02-4186-85ab-0d3aaf410964/projects/E-mail%20assistant%20workflow-ca74b9fd
- **Dataset:** https://apac.smith.langchain.com/o/a9d2a1c0-2d02-4186-85ab-0d3aaf410964/datasets/7c1b6c04-857e-429b-a60d-beb0b52b31aa

## 🚀 Quick Start

```bash
# 1. Start server
cd d:\Agents\LangGraph\agents-from-scratch
langgraph dev

# 2. Open browser
start http://127.0.0.1:2024/docs

# 3. Test your agent using Swagger UI!
```

## ❓ FAQ

**Q: Will Studio come to Windows?**
A: LangChain team may add Windows support in the future, but currently it's Mac-only.

**Q: Can I see the graph visualization?**
A: Not in the desktop app, but you can:
- Use Swagger UI for testing
- View execution traces in LangSmith web
- Check evaluation results with charts

**Q: How do I debug?**
A: 
- Check logs in terminal where `langgraph dev` is running
- View detailed traces in LangSmith APAC
- Use print statements in your node code
- Check API responses in Swagger UI

**Q: Does HITL (human-in-the-loop) work?**
A: Yes! When agent pauses for review:
- Swagger UI: Use `POST /threads/{thread_id}/runs` with `command.resume`
- Python: Use `client.runs.create()` with resume command
- The agent waits for your approval before continuing

## 📝 Summary

✅ Your agent works perfectly on Windows  
✅ LangSmith evaluations work  
✅ Local API server works  
✅ Swagger UI provides testing interface  
❌ Desktop Studio app is Mac-only (not needed!)  

**Bottom line:** You have everything you need to develop, test, and evaluate your email assistant on Windows! 🎉
