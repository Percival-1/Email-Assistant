# 🚀 Production Deployment Guide

## How Gmail Integration Works in Production

### Manual Testing (What You're Doing Now):
```
You → LangGraph Studio → Paste email manually → Agent processes
```
**Problem:** Not scalable, requires manual input

### Production (Automated):
```
Gmail → Watcher checks every 5min → Agent auto-processes → Sends responses
```
**Benefit:** Fully automated, no manual intervention!

---

## 🎯 Production Architecture

```
┌─────────────────┐
│   Gmail Inbox   │
│  (Your emails)  │
└────────┬────────┘
         │
         │ Every 5 minutes
         ↓
┌─────────────────┐
│ Gmail Watcher   │  ← Python script running 24/7
│ (gmail_watcher  │
│  .py)           │
└────────┬────────┘
         │
         │ For each unread email
         ↓
┌─────────────────┐
│ Email Assistant │
│ (LangGraph      │
│  workflow)      │
└────────┬────────┘
         │
         ├─→ Triage
         ├─→ Draft Response
         ├─→ (Optional) HITL Review
         ├─→ Send Reply
         └─→ Mark as Read
```

---

## 🔧 Setup Options

### Option 1: Continuous Watcher (Local/Server)

**Run continuously on your machine:**
```bash
# Check Gmail every 5 minutes
python gmail_watcher.py --interval 5

# Or every 10 minutes with max 20 emails
python gmail_watcher.py --interval 10 --max-emails 20
```

**Features:**
- ✅ Runs in background
- ✅ Checks Gmail automatically
- ✅ Processes all unread emails
- ✅ Logs everything
- ❌ Needs to stay running

**Use case:** Development, personal use, small business

---

### Option 2: Cron Job (Linux/Mac)

**Schedule to run every N minutes:**

```bash
# Edit crontab
crontab -e

# Add this line (runs every 5 minutes)
*/5 * * * * cd /path/to/agents-from-scratch && python gmail_watcher.py --once
```

**Features:**
- ✅ Runs automatically on schedule
- ✅ No need to keep terminal open
- ✅ Restart-safe
- ✅ System-level scheduling

**Use case:** Production servers, always-on systems

---

### Option 3: Windows Task Scheduler

**Schedule on Windows:**

1. Open **Task Scheduler**
2. Create **New Task**
3. **Trigger:** Every 5 minutes
4. **Action:** Run program
   - Program: `python`
   - Arguments: `gmail_watcher.py --once`
   - Start in: `d:\Agents\LangGraph\agents-from-scratch`
5. **Conditions:** 
   - ✅ Start only if network available
   - ✅ Wake computer to run
6. Click **OK**

**Features:**
- ✅ Native Windows solution
- ✅ Runs in background
- ✅ Survives reboots
- ✅ No terminal needed

**Use case:** Windows servers, desktop automation

---

### Option 4: Cloud Deployment (Recommended for Production)

**Deploy to cloud with LangGraph Platform:**

```bash
# Deploy to LangGraph Cloud
langgraph deploy

# Configure webhook for Gmail push notifications
# (Real-time, no polling needed!)
```

**Features:**
- ✅ Real-time email processing (via webhooks)
- ✅ No polling overhead
- ✅ Scales automatically
- ✅ 99.9% uptime
- ✅ Integrated monitoring
- ✅ HITL via web interface

**Use case:** Production SaaS, high-volume, enterprise

---

## 📊 Comparison

| Method | Latency | Setup | Cost | Use Case |
|--------|---------|-------|------|----------|
| Manual Studio | Real-time | Easy | Free | Testing only |
| **Continuous Watcher** | 5min | Easy | Free | Dev/Personal |
| Cron Job | 5-30min | Medium | Free | Production |
| Task Scheduler | 5-30min | Medium | Free | Windows |
| **Cloud Deploy** | Real-time | Hard | $$$ | Enterprise |

---

## 🚀 Quick Start: Run Watcher Now

### 1. Authenticate Gmail
```bash
python test_gmail_auth.py
```

### 2. Start Watcher
```bash
# Check every 5 minutes
python gmail_watcher.py --interval 5
```

### 3. Watch It Work
```
==========================================================
  Gmail Email Assistant - Watcher Started
==========================================================
Configuration:
  • Check interval: 5 minutes
  • Max emails per run: 10
  • Started at: 2024-11-24 14:30:00

👀 Watching Gmail inbox for new emails...
Press Ctrl+C to stop

==========================================================
🔍 Checking Gmail inbox... (2024-11-24 14:30:05)
==========================================================
📧 Found 2 email(s) to process

--- Processing Email 1/2 ---
From: john@company.com
Subject: Meeting Request for Next Week
✓ Classified as: respond
✓ Draft created: Hi John, Tuesday at 2pm works great...

--- Processing Email 2/2 ---
From: newsletter@service.com
Subject: Weekly Newsletter
✓ Classified as: ignore
✓ Marked as read

==========================================================
✅ Processed 2/2 emails successfully
==========================================================

⏳ Waiting 5 minutes until next check...
```

---

## 🔐 Production Best Practices

### 1. Error Handling
```python
# Watcher includes:
- Retry logic for API failures
- Error logging
- Email skip on parse errors
- Graceful degradation
```

### 2. Rate Limiting
```python
# Respect Gmail API limits:
- Max 250 quota units/user/second
- Max 25,000 quota units/user/day
- 5-10 minute intervals recommended
```

### 3. Monitoring
```bash
# Log all actions
python gmail_watcher.py --interval 5 >> logs/watcher.log 2>&1

# Monitor the logs
tail -f logs/watcher.log
```

### 4. HITL in Production
```python
# For sensitive emails:
1. Agent pauses (interrupt)
2. Sends notification (email/Slack/SMS)
3. User approves via link
4. Agent continues
```

---

## 📝 Configuration File

Create `.env.production`:
```env
# Gmail Settings
GMAIL_CHECK_INTERVAL=5  # minutes
GMAIL_MAX_EMAILS_PER_RUN=10
GMAIL_LOOKBACK_MINUTES=30

# Agent Settings
AUTO_SEND_RESPONSES=false  # true to skip HITL
HITL_NOTIFICATION_EMAIL=you@company.com
HITL_NOTIFICATION_SLACK_WEBHOOK=https://...

# LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=email-assistant-production
```

---

## 🎯 Summary

**For Testing:**
- Use LangGraph Studio with manual input ✅ (you're here)

**For Development:**
- Run `python gmail_watcher.py` continuously ✅ (recommended next step)

**For Production:**
- Set up cron job (Linux/Mac) or Task Scheduler (Windows) ✅
- Or deploy to LangGraph Cloud for real-time ⚡

---

**Try it now:**
```bash
python gmail_watcher.py --interval 5
```

It will automatically:
1. Check your Gmail every 5 minutes
2. Process unread emails
3. Generate responses
4. Log everything
5. No manual input needed! 🎉
