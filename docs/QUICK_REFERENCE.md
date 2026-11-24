# Quick Reference Card

## 🚀 Start Everything (One Command)

### Windows:
```powershell
start_ai_inbox.bat
```

### Manual (All Platforms):
```bash
# Terminal 1
conda activate agent && langgraph dev

# Terminal 2
conda activate agent && python gmail_watcher.py --interval 5

# Terminal 3
conda activate agent && streamlit run ai_inbox_ui.py
```

---

## 🌐 URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **AI Inbox UI** ⭐ | http://localhost:8501 | Daily email management |
| LangGraph Studio | http://localhost:2024 | Debugging & testing |
| API Docs | http://localhost:2024/docs | API reference |
| LangSmith | https://apac.smith.langchain.com | Evaluation & monitoring |

---

## 📧 Email Processing Flow

```
Gmail → Watcher → LangGraph → AI Processing → Review → Approve → Send
  📥      (5min)     (API)       (2-3sec)      (You)    (1-click)  📤
```

---

## 🎨 Priority Colors

| Color | Priority | Meaning |
|-------|----------|---------|
| 🔴 Red | Urgent | Respond immediately |
| 🔵 Blue | Respond | Normal reply needed |
| ⚪ Gray | Ignore | Low priority/spam |

---

## ⌨️ Common Commands

### Process Specific Emails
```bash
# Process last 5 emails from last 24 hours
python gmail_watcher.py --once --minutes-since 1440 --max-emails 5

# Process last 10 emails from last week
python gmail_watcher.py --once --minutes-since 10080 --max-emails 10

# Process all unread emails (up to 50)
python gmail_watcher.py --once --minutes-since 10080 --max-emails 50

# Quick batch script (Windows)
process_last_5_emails.bat
```

### Continuous Watching
```bash
# Check every 5 minutes for new emails
python gmail_watcher.py --interval 5

# Check every 1 minute (faster testing)
python gmail_watcher.py --interval 1
```

### Check Services Status
```bash
# Check LangGraph server
curl http://localhost:2024/ok

# Check Redis
docker exec agents-from-scratch-redis-1 redis-cli ping

# Check PostgreSQL
docker exec agents-from-scratch-postgres-1 pg_isready
```

### View Logs
```bash
# LangGraph server (Terminal 1)
# Gmail watcher (Terminal 2)
# AI Inbox UI (Terminal 3)

# Docker logs
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Restart Services
```bash
# Stop all
Ctrl+C (in each terminal)
docker-compose down

# Start database
docker-compose up -d postgres redis

# Start application (run in separate terminals)
langgraph dev
python gmail_watcher.py --interval 5
streamlit run ai_inbox_ui.py
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "LangGraph server not running" | Run `langgraph dev` in Terminal 1 |
| "No emails appearing" | Run `python gmail_watcher.py` in Terminal 2 |
| "object of type 'generator' has no len()" | Fixed! Restart watcher: `python gmail_watcher.py` |
| "Gmail auth failed" | Run `python test_gmail_auth.py` |
| "PostgreSQL connection failed" | Run `docker-compose up -d postgres` |
| "Redis connection failed" | Optional - system has fallback |
| "403 Forbidden (LangSmith)" | Check `.env` has APAC endpoint |

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `ai_inbox_ui.py` | AI Inbox interface |
| `gmail_watcher.py` | Automated email fetcher |
| `src/email_assistant/workflows/main_workflow.py` | Main workflow |
| `.env` | Configuration (API keys, passwords) |
| `langgraph.json` | LangGraph server config |
| `docker-compose.yml` | Database services |

---

## 🔧 Configuration Files

### `.env` (Required Variables)
```bash
# OpenAI
OPENAI_API_KEY=sk-...

# LangSmith (APAC)
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_ENDPOINT=https://apac.api.smith.langchain.com
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=email-assistant

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=agent_user
POSTGRES_PASSWORD=Shubh@2024
POSTGRES_DB=agent_memory

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
```

### `credentials.json` (Gmail OAuth)
- Download from Google Cloud Console
- Place in project root
- Run `python test_gmail_auth.py` to generate `token.json`

---

## 📊 Key Metrics (From Evaluation)

| Metric | Value |
|--------|-------|
| Triage Accuracy | 81% |
| P50 Latency | 2.3s |
| P99 Latency | 3.5s |
| Error Rate | 0% |
| Token Reduction | 50-80% |
| Test Scenarios | 16 |

---

## 🎯 Three Interfaces Cheat Sheet

### 1. AI Inbox UI (localhost:8501) ⭐ **MAIN**
**Use for:** Daily email management
```
✅ See all emails
✅ View AI decisions
✅ Edit drafts
✅ Approve/reject
✅ No JSON required
```

### 2. LangGraph Studio (localhost:2024)
**Use for:** Debugging & testing
```
✅ View workflow graph
✅ Test with JSON input
✅ Inspect state
✅ Debug errors
```

### 3. Gmail (gmail.com)
**Use for:** Traditional email
```
✅ Verify sent emails
✅ Check attachments
✅ View full history
```

---

## 🔐 Security Checklist

- [ ] Never commit `.env` to git
- [ ] Never commit `credentials.json` to git
- [ ] Never commit `token.json` to git
- [ ] Add to `.gitignore`: `.env`, `credentials.json`, `token.json`
- [ ] Use environment variables for production
- [ ] Rotate API keys regularly
- [ ] Review Gmail OAuth scopes

---

## 📝 Resume Bullet Points (Ready to Copy)

**Version 1 (Technical):**
> Developed production-grade email assistant using LangGraph, achieving 81% triage accuracy and 2.3s median latency across 16 test scenarios, with PostgreSQL/Redis storage, Gmail API integration, and LangSmith evaluation pipeline

**Version 2 (Architecture):**
> Architected modular AI email agent with 6-node workflow (triage, draft, review, send), implementing HITL patterns, HTML token optimization (50-80% reduction), and distributed storage using PostgreSQL and Redis

**Version 3 (Business Impact):**
> Built automated email assistant processing Gmail inbox with 81% classification accuracy, reducing response time to 2.3s, with human-in-the-loop review workflow and comprehensive evaluation suite

**Version 4 (Full-Stack):**
> Engineered end-to-end AI agent system integrating OpenAI GPT-4, Gmail/Calendar APIs, PostgreSQL, Redis, and LangSmith observability, with automated deployment pipeline and 0% error rate in production testing

---

## 🎓 Learning Path

1. **Understand the basics** → Read [HOW_IT_WORKS.md](HOW_IT_WORKS.md)
2. **Set up services** → Follow [QUICK_START.md](QUICK_START.md)
3. **Configure Gmail** → Read [GMAIL_QUICKSTART.md](GMAIL_QUICKSTART.md)
4. **Use AI Inbox** → Read [AI_INBOX_GUIDE.md](AI_INBOX_GUIDE.md)
5. **Understand architecture** → Read [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)
6. **Run evaluation** → Follow [LANGSMITH_EVALUATION_GUIDE.md](LANGSMITH_EVALUATION_GUIDE.md)
7. **Deploy to production** → Check [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)

---

## 🆘 Get Help

### Documentation
- **AI Inbox Guide:** [AI_INBOX_GUIDE.md](AI_INBOX_GUIDE.md)
- **System Architecture:** [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)
- **Complete Setup:** [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)
- **Deployment:** [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)

### Quick Fixes
- **LangSmith Issues:** [FIX_LANGSMITH.md](FIX_LANGSMITH.md)
- **Quick Fixes:** [QUICK_FIX.md](QUICK_FIX.md)
- **Gmail Setup:** [GMAIL_SETUP_GUIDE.md](GMAIL_SETUP_GUIDE.md)

### Check Status
```bash
# API health
curl http://localhost:2024/ok

# View threads
curl http://localhost:2024/threads

# Check database
docker exec agents-from-scratch-postgres-1 psql -U agent_user -d agent_memory -c "\dt"
```

---

## ⚡ Performance Tips

### Faster Testing
```bash
# Reduce watcher interval
python gmail_watcher.py --interval 1  # Check every 1 minute

# Use smaller model for triage
# Edit src/email_assistant/nodes/triage_node.py
# Change: gpt-4o-mini → gpt-3.5-turbo (faster, cheaper)
```

### Production Optimization
```bash
# Increase watcher interval
python gmail_watcher.py --interval 10  # Check every 10 minutes

# Use connection pooling (already configured in PostgreSQL)
# Enable Redis persistence (edit docker-compose.yml)
```

---

## 🎉 You're Ready!

### Daily Workflow:
1. Run `start_ai_inbox.bat` (or manual commands)
2. Open http://localhost:8501
3. Review emails, approve/edit drafts
4. That's it! 🚀

### Monitoring:
- Check AI Inbox UI for new emails
- Review LangSmith for performance metrics
- Monitor Gmail sent folder for verification

### Maintenance:
- Weekly: Run evaluation (`python run_evaluation.py`)
- Monthly: Update dependencies (`pip install --upgrade -r requirements.txt`)
- As needed: Regenerate Gmail token (`python test_gmail_auth.py`)

---

**Congratulations! You have a fully functional AI email assistant! 🎊**

**Main Interface:** http://localhost:8501 (AI Inbox UI)
