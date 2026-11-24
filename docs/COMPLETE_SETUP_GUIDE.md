# Complete Setup Guide - Email Assistant

Step-by-step guide to get your email assistant fully operational and tested.

## 📋 Prerequisites

- Python 3.11+
- Docker (for PostgreSQL + Redis)
- Gmail account
- OpenAI API key
- LangSmith account (optional, for evaluation)

## 🚀 Part 1: Installation

### Step 1: Clone & Navigate

```bash
cd d:\Agents\LangGraph\agents-from-scratch
```

### Step 2: Install Dependencies

**Option A: Using uv (Recommended - Faster)**
```bash
# Install uv
pip install uv

# Install all dependencies
uv sync --extra dev
```

**Option B: Using pip**
```bash
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# Upgrade pip
python -m pip install --upgrade pip

# Install in editable mode
pip install -e .
```

### Step 3: Verify Installation

```bash
# Should show no errors
python -c "import langchain, langgraph, openai; print('✓ All imports successful')"
```

## 🔑 Part 2: API Keys Setup

### Step 1: Get OpenAI API Key

1. Go to: https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy key (starts with `sk-`)

### Step 2: Get LangSmith API Key (Optional but Recommended)

1. Go to: https://smith.langchain.com
2. Sign in or create account
3. Go to Settings → API Keys
4. Create new key
5. Copy key (starts with `lsv2_`)

### Step 3: Create .env File

```bash
# Copy example
cp .env.example .env

# Edit .env (use notepad or your editor)
notepad .env
```

**Add these values:**
```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# LangSmith (for evaluation & tracing)
LANGCHAIN_API_KEY=lsv2-your-key-here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=email-assistant-test

# Gmail (we'll add these later)
# GMAIL_TOKEN=...
# GMAIL_SECRET=...

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=email_assistant
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 🗄️ Part 3: Database Setup

### Step 1: Start Databases with Docker

```bash
# Start PostgreSQL + Redis
docker-compose up -d

# Verify they're running
docker ps
```

**You should see:**
```
CONTAINER ID   IMAGE         PORTS
abc123...      postgres      0.0.0.0:5432->5432/tcp
def456...      redis         0.0.0.0:6379->6379/tcp
```

### Step 2: Verify Database Connections

```bash
python test_storage.py
```

**Expected output:**
```
✓ PostgreSQL connection successful
✓ Redis connection successful
✓ Tables created
✓ Test data inserted
✓ All storage tests passed!
```

**If errors:**
- Check Docker is running: `docker ps`
- Check ports are free: `netstat -ano | findstr :5432`
- Restart containers: `docker-compose restart`

## 🧪 Part 4: Test Without Gmail (Mock Mode)

### Step 1: Test Structure

```bash
python test_new_structure.py
```

**Expected output:**
```
✅ Test 1: Imports successful!
✅ Test 2: Graph built successfully!
✅ Test 3: Modular components structure verified!
✅ Test 4: File organization verified!
🎉 All tests passed!
```

### Step 2: Test Email Parser

```bash
python test_email_parser.py
```

**Expected output:**
```
📊 Statistics:
  Raw Tokens:    1,842 tokens
  Parsed Tokens:  623 tokens
  Tokens Saved:  1,219 tokens
  Savings:       66.2%
```

### Step 3: Run Basic Evaluation (Mock Data)

```bash
python run_evaluation.py
# Choose option 1 (Triage - Basic)
```

**Expected output:**
```
📊 Accuracy Metrics:
Triage Accuracy     : 87.50%
Tool Accuracy       : 81.25%

Overall Score: 85.00%
✅ Good performance!
```

## 📧 Part 5: Gmail Integration (Optional)

### Step 1: Enable Gmail API

1. Go to: https://console.cloud.google.com
2. Create new project: "Email Assistant"
3. Enable APIs:
   - Gmail API
   - Google Calendar API
4. Create OAuth 2.0 credentials:
   - Application type: Desktop app
   - Download JSON → Save as `credentials.json`

### Step 2: Setup Gmail Authentication

```bash
# Create secrets directory
mkdir src\email_assistant\tools\gmail\.secrets

# Copy credentials
copy credentials.json src\email_assistant\tools\gmail\.secrets\secrets.json

# Run authentication (opens browser)
python -c "from email_assistant.tools.gmail.gmail_tools import get_credentials; get_credentials()"
```

**Follow the browser prompts:**
1. Select your Gmail account
2. Click "Advanced" → "Go to Email Assistant (unsafe)"
3. Click "Allow"
4. Close browser

**Verify:**
- File created: `src\email_assistant\tools\gmail\.secrets\token.json`

### Step 3: Add Gmail Credentials to .env

```bash
# Get token content
type src\email_assistant\tools\gmail\.secrets\token.json

# Copy the JSON content
# Add to .env:
GMAIL_TOKEN={"token":"...","refresh_token":"..."}
```

## 🎯 Part 6: Testing with Real/Mock Emails

### Test Scenario 1: Meeting Request

Create file: `test_emails/meeting_request.py`

```python
import sys
sys.path.insert(0, 'src')

from email_assistant.email_assistant import email_assistant

# Test email
email_input = {
    "from": "alice.smith@company.com",
    "to": "john@company.com",
    "subject": "Quick sync on Q3 roadmap",
    "body": """Hi John,

I hope this email finds you well. I wanted to reach out to schedule 
a meeting to discuss our Q3 product roadmap and upcoming launches.

Would you be available next Tuesday or Wednesday afternoon? 
I'm flexible on timing - whatever works best for your schedule.

Looking forward to connecting!

Best regards,
Alice Smith
Product Manager""",
    "id": "test-email-001",
    "thread_id": "thread-001"
}

# Run the agent
print("Processing email...\n")
result = email_assistant.invoke({"email_input": email_input})

print("\n" + "="*60)
print("RESULT:")
print("="*60)
print(f"\nClassification: {result.get('classification_decision', 'N/A')}")
print(f"\nTriage Result: {result.get('triage_result', {})}")
print(f"\nDraft Response:\n{result.get('draft_response', 'N/A')}")
print(f"\nTools Called: {result.get('tools_called', [])}")
print("\n" + "="*60)
```

**Run it:**
```bash
python test_emails/meeting_request.py
```

**Expected behavior:**
1. Classifies as "RESPOND"
2. Checks calendar availability
3. Schedules meeting (or proposes times)
4. Drafts professional response
5. Mentions meeting details

### Test Scenario 2: Email Thread (Context)

Create file: `test_emails/thread_conversation.py`

```python
import sys
sys.path.insert(0, 'src')

from email_assistant.email_assistant import email_assistant
from email_assistant.thread_context import get_context_manager
from langchain.chat_models import init_chat_model

# Initialize context manager
llm = init_chat_model("openai:gpt-4o-mini", temperature=0.0)
context_manager = get_context_manager(llm=llm)

# Simulate previous message in thread
thread_id = "thread-002"
previous_message = {
    "from_email": "bob@company.com",
    "to_email": "john@company.com",
    "subject": "API Documentation Review",
    "page_content": "Hi John, could you review the new API docs by Friday?",
    "send_time": "2024-01-20T10:00:00",
    "thread_id": thread_id
}

# Add to context (simulating history)
print("Adding previous message to thread context...\n")
context_manager.base_context.add_thread_message(thread_id, previous_message)

# Current reply in thread
email_input = {
    "from": "bob@company.com",
    "to": "john@company.com",
    "subject": "Re: API Documentation Review",
    "body": """Hi John,

Just following up on my previous email. Have you had a chance 
to look at the API documentation yet?

The deadline is coming up soon (Friday). Let me know if you 
need any clarification or more time.

Thanks,
Bob""",
    "id": "test-email-002",
    "thread_id": thread_id
}

# Run the agent
print("Processing follow-up email...\n")
result = email_assistant.invoke({
    "email_input": email_input,
    "thread_id": thread_id
})

print("\n" + "="*60)
print("RESULT:")
print("="*60)
print(f"\nClassification: {result.get('classification_decision', 'N/A')}")
print(f"\n📧 Draft Response:\n{result.get('draft_response', 'N/A')}")
print("\n" + "="*60)
print("\nNote: Response should acknowledge the previous request")
print("      and provide status update on the documentation review.")
```

**Run it:**
```bash
python test_emails/thread_conversation.py
```

**Expected behavior:**
1. Loads previous context
2. Understands this is a follow-up
3. Acknowledges original request
4. Provides status update
5. References the Friday deadline

### Test Scenario 3: Notification Email

Create file: `test_emails/notification.py`

```python
import sys
sys.path.insert(0, 'src')

from email_assistant.email_assistant import email_assistant

# System notification
email_input = {
    "from": "noreply@aws.amazon.com",
    "to": "john@company.com",
    "subject": "AWS Alert: High CPU Utilization",
    "body": """ALERT: High CPU Utilization

The following EC2 instance has exceeded the CPU utilization 
threshold of 90% for more than 15 minutes:

Instance ID: i-0b2d3e4f5a6b7c8d9
Region: us-west-2
Current utilization: 95.3%
Time: 2024-01-20 14:30:00 UTC

This is an automated message. Please do not reply.""",
    "id": "test-email-003",
    "thread_id": "thread-003"
}

# Run the agent
print("Processing system notification...\n")
result = email_assistant.invoke({"email_input": email_input})

print("\n" + "="*60)
print("RESULT:")
print("="*60)
print(f"\nClassification: {result.get('classification_decision', 'N/A')}")
print(f"\nExpected: NOTIFY (important but no response needed)")
print("\n" + "="*60)
```

**Run it:**
```bash
python test_emails/notification.py
```

**Expected behavior:**
1. Classifies as "NOTIFY"
2. No response generated
3. Marks for user attention
4. No calendar actions

### Test Scenario 4: Spam/Marketing

Create file: `test_emails/spam_marketing.py`

```python
import sys
sys.path.insert(0, 'src')

from email_assistant.email_assistant import email_assistant

# Marketing email
email_input = {
    "from": "marketing@newsletter.com",
    "to": "john@company.com",
    "subject": "🎉 Special Offer: 50% Off Everything!",
    "body": """<html>
<body>
<h1>HUGE SALE - DON'T MISS OUT!</h1>
<p>Dear Valued Customer,</p>
<p>Get 50% off EVERYTHING in our store this weekend only!</p>
<p>Use code: SAVE50</p>
<a href="http://shop.example.com">Shop Now</a>
<p><small>Unsubscribe | Privacy Policy | Terms</small></p>
<img src="tracking.png" width="1" height="1">
</body>
</html>""",
    "id": "test-email-004",
    "thread_id": "thread-004"
}

# Run the agent
print("Processing marketing email...\n")
result = email_assistant.invoke({"email_input": email_input})

print("\n" + "="*60)
print("RESULT:")
print("="*60)
print(f"\nClassification: {result.get('classification_decision', 'N/A')}")
print(f"\nExpected: IGNORE (marketing/promotional)")
print("\n📊 Token Optimization:")
print(f"  Original HTML: ~500 tokens")
print(f"  Parsed text: ~50 tokens")
print(f"  Savings: 90%")
print("\n" + "="*60)
```

**Run it:**
```bash
python test_emails/spam_marketing.py
```

**Expected behavior:**
1. Classifies as "IGNORE"
2. HTML parsed (token savings shown)
3. No response generated
4. Marked as read

## 📊 Part 7: Run Complete Evaluation

```bash
# Run full evaluation suite
python run_evaluation.py

# Choose option 3 (Both evaluations)
```

**What it tests:**
- 16 different email scenarios
- Classification accuracy
- Tool usage
- Response quality
- Latency
- Token usage

**View results:**
1. Terminal output shows scores
2. Charts saved to: `src/email_assistant/eval/results/`
3. LangSmith dashboard: https://smith.langchain.com

## 🎯 Part 8: Monitor Performance

### View Metrics

```bash
python -m email_assistant.eval.view_metrics
```

### Analyze Failures

```bash
python -m email_assistant.eval.analyze_failures
```

### Check LangSmith Dashboard

1. Go to: https://smith.langchain.com
2. Select project: `email-assistant-test`
3. View:
   - Experiments → Evaluation runs
   - Traces → Individual executions
   - Datasets → Test cases

## ✅ Verification Checklist

After completing setup, verify:

**Installation:**
- [ ] Dependencies installed (`python -c "import langchain"`)
- [ ] No import errors
- [ ] Virtual environment activated

**Configuration:**
- [ ] .env file created
- [ ] OpenAI API key set
- [ ] LangSmith API key set (optional)
- [ ] Database credentials configured

**Databases:**
- [ ] Docker containers running
- [ ] PostgreSQL accessible
- [ ] Redis accessible
- [ ] `test_storage.py` passes

**Testing:**
- [ ] Structure test passes
- [ ] Email parser test passes
- [ ] Mock evaluation passes (>75% accuracy)

**Optional Gmail:**
- [ ] Gmail API enabled
- [ ] OAuth credentials created
- [ ] token.json file exists
- [ ] Can fetch test emails

**Test Scenarios:**
- [ ] Meeting request works
- [ ] Thread context works
- [ ] Notification classified correctly
- [ ] Spam/marketing ignored

**Evaluation:**
- [ ] Evaluation runs without errors
- [ ] Results visible in terminal
- [ ] Charts generated
- [ ] LangSmith dashboard shows data

## 🚨 Troubleshooting

### "Module not found" errors
```bash
# Verify installation
pip list | grep langchain

# Reinstall if needed
pip install -e .
```

### Docker containers not starting
```bash
# Check if ports are in use
netstat -ano | findstr :5432
netstat -ano | findstr :6379

# Stop conflicting services or change ports in docker-compose.yml
```

### "Authentication error" in LangSmith
```bash
# Verify API key
echo %LANGCHAIN_API_KEY%  # Windows
echo $LANGCHAIN_API_KEY    # Linux/Mac

# Should output your key, not empty
```

### Low evaluation scores
- Expected for first run: 70-85%
- Improve by editing prompts in `src/email_assistant/prompts.py`
- Re-run evaluation to compare

### Gmail authentication fails
- Use Chrome or Firefox (not Edge)
- Allow pop-ups for console.cloud.google.com
- Try incognito mode
- Check OAuth consent screen settings

## 🎓 Next Steps

1. **Customize Prompts**
   - Edit `src/email_assistant/prompts.py`
   - Adjust classification rules
   - Modify response style

2. **Add Test Cases**
   - Add to `src/email_assistant/eval/email_dataset.py`
   - Re-run evaluation
   - Track improvements

3. **Monitor Production**
   - Use LangSmith tracing
   - Track latency and costs
   - Analyze failures

4. **Scale Up**
   - Add error handling
   - Implement retry logic
   - Set up monitoring
   - Deploy to cloud

## 📞 Support

**Issues:** Create GitHub issue
**Documentation:** See other .md files in root
**Questions:** Check HOW_IT_WORKS.md

---

**Setup complete? Test it:** `python run_evaluation.py`
