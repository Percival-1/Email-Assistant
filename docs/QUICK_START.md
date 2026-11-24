# Quick Start Guide - Email Assistant

Get the email assistant running in 5 minutes! ⚡

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
# Using uv (recommended)
pip install uv
uv sync --extra dev

# Or using pip
pip install -e .
```

### Step 2: Setup Databases (Docker)

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Verify they're running
docker-compose ps
```

### Step 3: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env and add your API keys:
# - OPENAI_API_KEY
# - LANGSMITH_API_KEY
# - EMAIL_ADDRESS
```

### Step 4: Setup Gmail (Optional but Recommended)

```bash
# 1. Enable Gmail API in Google Cloud Console
# 2. Download credentials to .secrets/secrets.json
# 3. Run setup
python src/email_assistant/tools/gmail/setup_gmail.py
```

### Step 5: Test Storage

```bash
python test_storage.py
```

### Step 6: Run the Assistant

```bash
# Start the server
langgraph dev --graph email_assistant_modular

# In another terminal, process emails
python src/email_assistant/tools/gmail/run_ingest.py \
  --email your@gmail.com \
  --minutes-since 1440
```

---

## 📁 Project Structure

```
src/email_assistant/
├── agent/                    # Modular agent components
│   ├── memory_manager.py    # Memory operations
│   ├── triage.py            # Email classification
│   ├── response.py          # Response generation
│   └── interrupt_handler.py # Human-in-the-loop
│
├── storage/                  # Database layer
│   ├── postgres_memory.py   # PostgreSQL (long-term)
│   ├── redis_cache.py       # Redis (caching)
│   └── integrated_storage.py # Combined manager
│
├── tools/                    # Email & calendar tools
│   ├── default/             # Mock tools
│   └── gmail/               # Real Gmail/Calendar APIs
│
├── thread_context.py        # Conversation tracking
├── email_assistant_modular.py # Main agent (clean!)
└── ...
```

---

## 🎯 What It Does

1. **Triages Emails** → Classify as respond/notify/ignore
2. **Tracks Context** → Remembers conversations across threads
3. **Drafts Responses** → Generates context-aware replies
4. **Manages Calendar** → Checks availability, schedules meetings
5. **Learns from You** → Adapts to your preferences

---

## 🔧 Key Features

### Thread Context
- Remembers full conversation history
- Extracts action items automatically
- Provides context for responses

### Smart Calendar
- Checks availability across multiple days
- Suggests best meeting slots
- Detects conflicts automatically
- Adds Google Meet links

### Storage
- **PostgreSQL**: Long-term memory
- **Redis**: Fast caching (10-25x faster)
- **Integrated**: Smart caching strategy

---

## 📚 Documentation

- **Full Setup**: `DATABASE_SETUP.md`
- **Features**: `ENHANCED_FEATURES_GUIDE.md`
- **Quick Reference**: `QUICK_REFERENCE.md`
- **Final Summary**: `FINAL_IMPLEMENTATION_SUMMARY.md`

---

## 🐛 Troubleshooting

**"Module not found"**
```bash
pip install -e .
```

**"Can't connect to PostgreSQL"**
```bash
docker-compose up -d postgres
```

**"Can't connect to Redis"**
```bash
docker-compose up -d redis
```

**"No emails found"**
```bash
# Try longer time window
python src/email_assistant/tools/gmail/run_ingest.py \
  --email your@gmail.com \
  --minutes-since 10080 \
  --include-read
```

---

## ✨ Next Steps

1. **Read the code** in `src/email_assistant/agent/` - it's modular and clean!
2. **Test features** - try thread context and calendar tools
3. **Customize** - adjust prompts and preferences
4. **Learn** - read through notebooks in `notebooks/`

---

**You're ready to go!** 🎉
