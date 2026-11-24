# ⚡ Gmail Setup - Quick Start

## 🎯 5-Minute Setup

### Step 1: Google Cloud Console (2 minutes)
1. Go to: https://console.cloud.google.com/
2. Create project: **"Email Assistant"**
3. Search & enable: **"Gmail API"** → Click ENABLE
4. Search & enable: **"Google Calendar API"** → Click ENABLE

### Step 2: OAuth Setup (2 minutes)
1. Go to: **APIs & Services** → **OAuth consent screen**
2. Choose: **External** → Click CREATE
3. Fill:
   - App name: **Email Assistant**
   - Your email in both fields
   - Click SAVE AND CONTINUE (3 times, don't add scopes yet)
4. Click **ADD USERS** → Add your Gmail → Click ADD

### Step 3: Get Credentials (1 minute)
1. Go to: **APIs & Services** → **Credentials**
2. Click: **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Type: **Desktop app**
4. Name: **Email Assistant**
5. Click: **CREATE**
6. Click: **DOWNLOAD JSON** (download icon)
7. Rename to: **`credentials.json`**
8. Move to: **`d:\Agents\LangGraph\agents-from-scratch\credentials.json`**

### Step 4: Authenticate
```bash
cd d:\Agents\LangGraph\agents-from-scratch
python test_gmail_auth.py
```

**What happens:**
- ✅ Browser opens
- ✅ Sign in with Gmail
- ✅ Click "Allow"
- ✅ Browser shows "Authentication successful"
- ✅ Script confirms connection

### Step 5: Update .env
```env
EMAIL_ADDRESS=your.actual.email@gmail.com
```

### Step 6: Test!
```bash
langgraph dev
```

Then in Studio, test with a real email!

---

## 🎉 That's It!

You now have:
- ✅ Gmail API access
- ✅ Calendar API access
- ✅ OAuth tokens saved
- ✅ Ready to process real emails

## 📝 Files Created

After authentication:
```
credentials.json  ← OAuth client secrets (from Google)
token.pickle      ← Your access tokens (created by script)
```

**Important:** Add to `.gitignore`:
```
token.pickle
token.json
*.pickle
```

---

Need detailed help? See **GMAIL_SETUP_GUIDE.md**
