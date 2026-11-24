# System Architecture - How Everything Connects

## 🎯 The Big Picture

```
┌─────────────┐
│   Gmail     │ ← Your actual Gmail inbox
│  (Email)    │   (emails arrive here)
└──────┬──────┘
       │
       │ (1) Fetches unread emails every 5 min
       ↓
┌─────────────────────┐
│  Gmail Watcher      │ ← Python script (gmail_watcher.py)
│  (gmail_watcher.py) │   Polls Gmail API
└──────┬──────────────┘
       │
       │ (2) Sends email to LangGraph API
       ↓
┌────────────────────────────────────────────────┐
│          LangGraph Server                      │
│          (localhost:2024)                      │
│                                                │
│  ┌──────────────────────────────────────┐    │
│  │   Email Processing Workflow          │    │
│  │                                       │    │
│  │   1. Triage Node                     │    │
│  │      ↓ (classify: urgent/respond/    │    │
│  │          ignore)                      │    │
│  │   2. Draft Response Node             │    │
│  │      ↓ (generate reply)              │    │
│  │   3. Human Review Node               │    │
│  │      ↓ (⏸️ INTERRUPT - wait for you) │    │
│  │   4. Send Response Node              │    │
│  │      ↓ (send via Gmail)              │    │
│  │   5. Mark Read Node                  │    │
│  │      ↓ (update Gmail)                │    │
│  └──────────────────────────────────────┘    │
│                                                │
│  ┌──────────────────────────────────────┐    │
│  │   Storage                             │    │
│  │   - PostgreSQL (long-term memory)    │    │
│  │   - Redis (thread context cache)     │    │
│  └──────────────────────────────────────┘    │
└────────┬───────────────────────┬───────────────┘
         │                       │
         │                       │ (3) Fetches thread state
         │                       ↓
         │              ┌─────────────────┐
         │              │  AI Inbox UI    │ ← YOU interact here!
         │              │ (localhost:8501)│   Streamlit web app
         │              │                 │
         │              │  - View emails  │
         │              │  - See AI logic │
         │              │  - Edit drafts  │
         │              │  - Approve/     │
         │              │    Reject       │
         │              └─────────────────┘
         │                       │
         │                       │ (4) Approve/Reject command
         │                       ↓
         └───────────────────────┘
                 │
                 │ (5) Sends email via Gmail API
                 ↓
         ┌─────────────┐
         │   Gmail     │ ← Sent email appears here
         │ (Sent box)  │
         └─────────────┘
```

---

## 🔄 Data Flow (Step by Step)

### Step 1: Email Arrives
```
User sends email
    ↓
Gmail inbox receives it
    ↓
Marked as "unread"
```

### Step 2: Watcher Detects
```
gmail_watcher.py runs every 5 minutes
    ↓
Calls Gmail API: list unread emails
    ↓
Finds new email(s)
    ↓
Extracts: id, threadId, from, subject, body, timestamp
    ↓
Sends to LangGraph API: POST /threads/{id}/runs
```

### Step 3: AI Processing
```
LangGraph receives email
    ↓
Creates thread with unique ID
    ↓
Workflow starts:

[Triage Node]
    ↓
Analyzes email with GPT-4o-mini
    ↓
Classifies: urgent / respond / ignore
    ↓
Stores in state: {"priority": "urgent", "reasoning": "..."}

[Draft Response Node]
    ↓
If priority != "ignore":
    Generates response with GPT-4o
    ↓
Stores in state: {"content": "Dear...", "tone": "professional"}

[Human Review Node]
    ↓
Calls interrupt() - PAUSES workflow
    ↓
Waits for user approval
```

### Step 4: You Review in AI Inbox
```
AI Inbox UI polls LangGraph API
    ↓
GET /threads → sees new thread
    ↓
GET /threads/{id}/state → gets email + triage + draft
    ↓
Displays email card:
    - Original email
    - AI triage reasoning
    - Draft response
    - [Approve] [Reject] buttons
    ↓
You click [Approve & Send]
    ↓
UI sends: POST /threads/{id}/runs
    with command: {"resume": {"approved": true}}
```

### Step 5: Workflow Resumes
```
LangGraph receives approval
    ↓
Workflow continues from interrupt:

[Send Response Node]
    ↓
Calls Gmail API: create draft
    ↓
Sends draft via Gmail
    ↓
Stores sent status in state

[Mark Read Node]
    ↓
Marks original email as read in Gmail
    ↓
Workflow complete ✅
```

---

## 🖥️ Three Interfaces Explained

### 1. Gmail (gmail.com)
**What it is:** Your actual email account
**What you see:**
- Inbox with incoming emails
- Sent folder with sent replies
- Drafts (if approval pending)

**When to use:**
- Check if email was actually sent
- Verify sent message content
- Traditional email management

---

### 2. LangGraph Studio (localhost:2024)
**What it is:** Developer debugging tool
**What you see:**
```
┌─────────────────────────────────────┐
│  Graph Visualization                │
│                                     │
│    [triage] → [draft] → [review]   │
│                 ↓                   │
│            [send] → [mark_read]    │
│                                     │
│  Input (JSON):                      │
│  {                                  │
│    "email": {                       │
│      "subject": "Test"              │
│    }                                │
│  }                                  │
│                                     │
│  State:                             │
│  {                                  │
│    "triage": {"priority": "urgent"} │
│    "draft": {"content": "..."}      │
│  }                                  │
└─────────────────────────────────────┘
```

**When to use:**
- Debug workflow errors
- Test individual nodes
- Inspect state transitions
- View execution logs

**NOT user-friendly for daily use** (requires JSON input)

---

### 3. AI Inbox UI (localhost:8501) ⭐ **Main Interface**
**What it is:** Gmail-like UI for your AI assistant
**What you see:**
```
┌─────────────────────────────────────────────┐
│  📧 AI Email Inbox                          │
│                                             │
│  Sidebar:                   Main Area:      │
│  ┌─────────────┐          ┌──────────────┐ │
│  │ 🔄 Refresh  │          │  Email Cards │ │
│  │             │          │              │ │
│  │ Filters:    │          │  ┌─────────┐ │ │
│  │ ✅ Urgent   │          │  │ 🔴 From │ │ │
│  │ ✅ Respond  │          │  │ Subject │ │ │
│  │ ⬜ Ignore   │          │  │         │ │ │
│  │             │          │  │ 🤖 AI:  │ │ │
│  │ Stats:      │          │  │ Urgent  │ │ │
│  │ 📊 Total: 5 │          │  │         │ │ │
│  │             │          │  │ ✏️ Draft│ │ │
│  │ API:        │          │  │ [text]  │ │ │
│  │ ✅ Connected│          │  │         │ │ │
│  └─────────────┘          │  │ [✅][❌]│ │ │
│                           │  └─────────┘ │ │
│                           │              │ │
│                           │  ┌─────────┐ │ │
│                           │  │ Next... │ │ │
│                           │  └─────────┘ │ │
│                           └──────────────┘ │
└─────────────────────────────────────────────┘
```

**When to use:**
- **Daily email management** (primary use!)
- Review AI decisions
- Approve/edit/reject drafts
- Monitor processing status

**User-friendly** - no JSON, no technical knowledge needed

---

## 💾 Storage Architecture

```
┌─────────────────────────────────────┐
│          PostgreSQL                 │
│      (Long-term Memory)             │
│                                     │
│  Tables:                            │
│  - email_memory                     │
│    (past conversations)             │
│  - conversation_context             │
│    (user preferences, history)      │
│  - user_preferences                 │
│    (tone, response style)           │
│                                     │
│  Used for:                          │
│  - Remember past interactions       │
│  - Learn user preferences           │
│  - Track email threads              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│            Redis                    │
│      (In-Memory Cache)              │
│                                     │
│  Keys:                              │
│  - thread:{id}:context              │
│    (current conversation state)     │
│  - thread:{id}:metadata             │
│    (processing status)              │
│                                     │
│  Used for:                          │
│  - Fast access to active threads    │
│  - Temporary state storage          │
│  - Cache AI responses               │
│                                     │
│  Optional: Has in-memory fallback   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│       LangGraph State               │
│    (Built-in Checkpointing)         │
│                                     │
│  Stores:                            │
│  - Current workflow position        │
│  - Node execution history           │
│  - Interrupt points                 │
│                                     │
│  Used for:                          │
│  - Resume from interrupts           │
│  - Replay workflows                 │
│  - Time-travel debugging            │
└─────────────────────────────────────┘
```

---

## 🔌 API Endpoints Used

### LangGraph API (localhost:2024)

| Endpoint | Method | Used By | Purpose |
|----------|--------|---------|---------|
| `/ok` | GET | AI Inbox UI | Health check |
| `/threads` | GET | AI Inbox UI | List all threads |
| `/threads` | POST | Gmail Watcher | Create new thread |
| `/threads/{id}/runs` | POST | Watcher, UI | Start/resume workflow |
| `/threads/{id}/state` | GET | AI Inbox UI | Get current state |
| `/threads/{id}/history` | GET | AI Inbox UI | Get execution history |

### Gmail API (googleapis.com)

| Endpoint | Method | Used By | Purpose |
|----------|--------|---------|---------|
| `users.messages.list` | GET | Gmail Watcher | List unread emails |
| `users.messages.get` | GET | Gmail Watcher | Get email details |
| `users.messages.send` | POST | Send Node | Send email |
| `users.messages.modify` | POST | Mark Read Node | Mark as read |
| `users.drafts.create` | POST | Draft Node | Create draft |

---

## 🎮 Control Flow

### Manual Control Points

1. **Start/Stop Services**
   - Terminal 1: `langgraph dev` (server)
   - Terminal 2: `gmail_watcher.py` (fetcher)
   - Terminal 3: `streamlit run ai_inbox_ui.py` (UI)

2. **Gmail Watcher Interval**
   ```bash
   # Fast testing (1 minute)
   python gmail_watcher.py --interval 1
   
   # Normal (5 minutes)
   python gmail_watcher.py --interval 5
   
   # Production (10 minutes)
   python gmail_watcher.py --interval 10
   ```

3. **Email Approval (in AI Inbox)**
   - Approve → Email sent immediately
   - Edit → Modify draft, then approve
   - Reject → No email sent, marked ignored

### Automatic Processes

1. **Email Fetching**
   - Runs every N minutes automatically
   - No user intervention needed

2. **AI Processing**
   - Triggered by new email
   - Runs through workflow automatically
   - Pauses at human review

3. **State Persistence**
   - PostgreSQL saves conversations
   - Redis caches active threads
   - LangGraph checkpoints workflow

---

## 🔍 How to Monitor

### Real-Time Monitoring

1. **AI Inbox UI** (Primary)
   - See emails as they're processed
   - View AI decisions in real-time
   - Action buttons for immediate control

2. **Gmail Watcher Terminal**
   ```
   INFO: Checking for new emails...
   INFO: Found 1 unread email(s)
   INFO: Processing: Bug in production
   INFO: Thread created: thread_abc123
   INFO: Waiting 5 minutes...
   ```

3. **LangGraph Server Terminal**
   ```
   INFO: Thread created: thread_abc123
   INFO: Running triage_node...
   INFO: Priority: urgent
   INFO: Running draft_response_node...
   INFO: Interrupt at human_review_node
   INFO: Awaiting approval...
   ```

### Historical Monitoring

1. **LangSmith Dashboard** (https://apac.smith.langchain.com)
   - View all past runs
   - Analyze latency/tokens/cost
   - Debug errors

2. **PostgreSQL Database**
   ```sql
   SELECT * FROM email_memory 
   ORDER BY timestamp DESC 
   LIMIT 10;
   ```

3. **Gmail Sent Folder**
   - Verify emails actually sent
   - Check content of sent replies

---

## 🚦 System States

### Email States
```
unread (Gmail)
    ↓
processing (LangGraph)
    ↓
awaiting_review (Human Review Node - INTERRUPT)
    ↓
approved / rejected (User decision)
    ↓
sent / ignored (Final state)
    ↓
read (Gmail)
```

### Thread States
```
created → running → interrupted → resumed → completed
```

### Service States
```
LangGraph Server:  stopped | running | error
Gmail Watcher:     stopped | running | error
AI Inbox UI:       stopped | running | error
PostgreSQL:        stopped | running
Redis:             stopped | running (optional)
```

---

## 📊 Performance Characteristics

### Latency
- **Email detection:** 0-5 minutes (watcher interval)
- **AI processing:** 2-3 seconds (triage + draft)
- **UI update:** Instant (polls every 5 seconds)
- **Email sending:** 1-2 seconds (Gmail API)

### Throughput
- **Gmail API quota:** 1 billion units/day (~250K emails)
- **LangGraph:** No hard limit (depends on hardware)
- **PostgreSQL:** Thousands of conversations
- **Redis:** Hundreds of active threads

### Resource Usage
- **CPU:** Low (~5% on modern PC)
- **RAM:** ~500MB (all services)
- **Disk:** ~100KB per email conversation
- **Network:** ~10KB per email (without attachments)

---

## 🎯 Summary Diagram

```
YOU (User)
  ↕️ (interact via browser)
AI Inbox UI (localhost:8501)
  ↕️ (HTTP API calls)
LangGraph Server (localhost:2024)
  ↕️ (triggers workflow)
Email Processing Workflow
  ↕️ (stores data)
PostgreSQL + Redis
  ↕️ (fetches/sends emails)
Gmail API
  ↕️ (syncs with)
Gmail Inbox (gmail.com)
```

**Key Insight:** 
- **Gmail** = Source of truth (where emails live)
- **LangGraph** = Brain (AI processing)
- **Storage** = Memory (past conversations)
- **AI Inbox UI** = Control center (where YOU control the AI)

---

## ✅ Verification Checklist

To verify everything is connected:

1. **Start all services:**
   ```bash
   # Terminal 1
   langgraph dev
   
   # Terminal 2
   python gmail_watcher.py --interval 1
   
   # Terminal 3
   streamlit run ai_inbox_ui.py
   ```

2. **Check connections:**
   - [ ] AI Inbox shows "✅ Connected"
   - [ ] Gmail Watcher shows "INFO: Checking for new emails..."
   - [ ] LangGraph shows "Server running on http://localhost:2024"

3. **Send test email:**
   - [ ] Send email to your Gmail
   - [ ] Watch watcher terminal detect it
   - [ ] Watch LangGraph terminal process it
   - [ ] See it appear in AI Inbox UI

4. **Approve draft:**
   - [ ] Click "Approve & Send" in AI Inbox
   - [ ] Watch LangGraph terminal show "sent"
   - [ ] Check Gmail sent folder for email

**All working? You're connected! 🎉**

---

## 🆘 Quick Troubleshooting

| Problem | Check | Solution |
|---------|-------|----------|
| UI shows "Disconnected" | LangGraph running? | `langgraph dev` |
| No emails appearing | Watcher running? | `python gmail_watcher.py` |
| Watcher shows errors | Gmail auth? | `python test_gmail_auth.py` |
| Can't approve drafts | Thread state? | Check interrupt at review node |
| PostgreSQL errors | Docker running? | `docker-compose up -d` |

---

**You now have a complete AI-powered email system with a user-friendly interface! 🚀**
