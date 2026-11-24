# 📧 Gmail Integration Setup Guide

## Step 1: Create Google Cloud Project

### 1.1 Go to Google Cloud Console
Visit: https://console.cloud.google.com/

### 1.2 Create New Project
1. Click **"Select a project"** at the top
2. Click **"NEW PROJECT"**
3. Project Name: **"Email Assistant"**
4. Click **"CREATE"**
5. Wait for project creation (30 seconds)
6. Make sure the new project is selected

---

## Step 2: Enable Gmail & Calendar APIs

### 2.1 Enable Gmail API
1. In the search bar, type: **"Gmail API"**
2. Click on **"Gmail API"**
3. Click **"ENABLE"** button
4. Wait for it to enable

### 2.2 Enable Google Calendar API
1. In the search bar, type: **"Google Calendar API"**
2. Click on **"Google Calendar API"**
3. Click **"ENABLE"** button

---

## Step 3: Configure OAuth Consent Screen

### 3.1 Go to OAuth Consent
1. Click hamburger menu (☰) → **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** (unless you have Google Workspace)
3. Click **"CREATE"**

### 3.2 Fill App Information
- **App name:** Email Assistant
- **User support email:** Your email
- **Developer contact:** Your email
- Click **"SAVE AND CONTINUE"**

### 3.3 Add Scopes
1. Click **"ADD OR REMOVE SCOPES"**
2. Search and add these scopes:
   - `https://www.googleapis.com/auth/gmail.readonly` - Read emails
   - `https://www.googleapis.com/auth/gmail.send` - Send emails
   - `https://www.googleapis.com/auth/gmail.modify` - Modify labels
   - `https://www.googleapis.com/auth/calendar` - Calendar access
3. Click **"UPDATE"**
4. Click **"SAVE AND CONTINUE"**

### 3.4 Add Test Users
1. Click **"ADD USERS"**
2. Add your Gmail address
3. Click **"ADD"**
4. Click **"SAVE AND CONTINUE"**
5. Click **"BACK TO DASHBOARD"**

---

## Step 4: Create OAuth Credentials

### 4.1 Create OAuth Client
1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. Application type: **"Desktop app"**
4. Name: **"Email Assistant Desktop"**
5. Click **"CREATE"**

### 4.2 Download Credentials
1. Click **"DOWNLOAD JSON"** (download icon)
2. Save the file as **`credentials.json`**
3. Move it to your project root: `d:\Agents\LangGraph\agents-from-scratch\credentials.json`

---

## Step 5: Update Your Environment

### 5.1 Update .env File
Open `.env` and update:
```env
# Your Gmail address
EMAIL_ADDRESS=your.actual.email@gmail.com
```

### 5.2 Verify credentials.json Location
Make sure `credentials.json` is in project root:
```
d:\Agents\LangGraph\agents-from-scratch\
├── credentials.json  ← HERE!
├── .env
├── pyproject.toml
└── src/
```

---

## Step 6: Test Gmail Connection

### 6.1 Run Authentication Script

Create a test script to authenticate:

```python
# test_gmail_auth.py
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar'
]

def authenticate_gmail():
    """Authenticate and get credentials."""
    creds = None
    
    # Check if token exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

# Test connection
print("=" * 60)
print("  Gmail Authentication Test")
print("=" * 60)

try:
    creds = authenticate_gmail()
    
    # Test Gmail API
    print("\n📧 Testing Gmail API...")
    gmail = build('gmail', 'v1', credentials=creds)
    results = gmail.users().messages().list(userId='me', maxResults=5).execute()
    messages = results.get('messages', [])
    
    print(f"✅ Connected! Found {len(messages)} recent emails")
    
    # Test Calendar API
    print("\n📅 Testing Calendar API...")
    calendar = build('calendar', 'v3', credentials=creds)
    calendars = calendar.calendarList().list().execute()
    
    print(f"✅ Connected! Found {len(calendars.get('items', []))} calendars")
    
    print("\n" + "=" * 60)
    print("✅ All APIs connected successfully!")
    print("=" * 60)
    print("\nYou can now use the email assistant with real Gmail!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check credentials.json exists")
    print("2. Make sure APIs are enabled")
    print("3. Check you added your email as test user")
```

Save and run:
```bash
python test_gmail_auth.py
```

**What happens:**
1. Browser will open automatically
2. Sign in with your Gmail account
3. Grant permissions
4. Browser will show "Authentication successful"
5. Script will test both Gmail and Calendar APIs

---

## Step 7: Run Email Assistant with Real Gmail

### 7.1 Update Your Agent to Use Gmail Tools

The agent should already have Gmail tools, but let's verify:

```bash
# Check if Gmail tools are imported
grep -r "gmail_tools" src/email_assistant/
```

### 7.2 Run the Agent

```bash
# Start the LangGraph server
langgraph dev
```

### 7.3 Test with Real Email

In LangGraph Studio:
1. Select **"email_assistant"** graph
2. Click **"New Thread"**
3. Use this input to fetch a REAL email:
```json
{
  "email_input": {
    "fetch_from_inbox": true,
    "max_results": 1
  }
}
```

OR to process a specific email by ID:
```json
{
  "email_input": {
    "message_id": "YOUR_MESSAGE_ID_HERE"
  }
}
```

---

## 🎯 Testing Workflow

### Test 1: Read Recent Emails
```python
from email_assistant.tools.gmail.gmail_tools import list_emails

# List recent unread emails
emails = list_emails(max_results=5, query="is:unread")
print(f"Found {len(emails)} unread emails")
```

### Test 2: Process One Email
1. Open LangGraph Studio
2. Select "email_assistant"
3. Create new thread
4. The agent will:
   - ✅ Fetch real email from inbox
   - ✅ Classify it (meeting/question/action/fyi)
   - ✅ Draft appropriate response
   - 🛑 Pause for your review (HITL)
   - ✅ Send reply to Gmail (after approval)
   - ✅ Mark original as read

### Test 3: Schedule Meeting from Email
Send yourself an email like:
```
Subject: Team Sync
Body: Can we meet next Tuesday at 2pm?
```

Then run the agent - it will:
1. Read the email
2. Detect it's a meeting request
3. Check your calendar
4. Create the event
5. Draft confirmation email
6. Wait for your approval
7. Send and mark as read

---

## 🔒 Security Notes

**What gets created:**
- `credentials.json` - OAuth client secrets (safe to commit if private repo)
- `token.pickle` - Your access tokens (**NEVER commit this!**)

**Add to .gitignore:**
```
token.pickle
token.json
*.pickle
credentials.json  # Optional - only if public repo
```

---

## ❓ Troubleshooting

### "Invalid credentials" error
- Make sure `credentials.json` is in project root
- Re-download from Google Cloud Console

### "Access blocked" error
- Add your email as test user in OAuth consent screen
- Wait a few minutes after adding

### "API not enabled" error
- Enable Gmail API and Calendar API
- Wait 1-2 minutes for propagation

### "Redirect URI mismatch"
- Use "Desktop app" type (not "Web application")
- Port 0 lets it use any available port

### Browser doesn't open
- Check firewall settings
- Try running as administrator
- Manually open the URL shown in terminal

---

## 🎉 Success Checklist

- [ ] Google Cloud project created
- [ ] Gmail API enabled
- [ ] Calendar API enabled
- [ ] OAuth consent screen configured
- [ ] Test user added (your email)
- [ ] OAuth credentials created
- [ ] `credentials.json` downloaded
- [ ] `credentials.json` in project root
- [ ] `.env` updated with your email
- [ ] `test_gmail_auth.py` runs successfully
- [ ] `token.pickle` created
- [ ] Can list emails from your inbox
- [ ] Can access your calendar
- [ ] Agent processes real emails

---

**Next:** Run `python test_gmail_auth.py` to authenticate!
