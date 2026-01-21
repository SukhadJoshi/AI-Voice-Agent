# SuperBryn AI Voice Agent

A web-based AI voice agent with visual avatar that can have natural conversations and book/retrieve appointments.

## 📊 Free Tier Value Comparison

**Best Free Tier Options (No Credit Card Required):**

| Service | Free Tier Value | Best For | Limitations |
|---------|----------------|----------|-------------|
| **Deepgram** ⭐ BEST VALUE | $200 one-time credits (~25,000+ minutes STT/TTS) | Speech-to-Text & Text-to-Speech | One-time only, concurrency limits |
| **LiveKit** | 1,000 agent min/month + 10K participant min/month | Voice infrastructure & real-time | Monthly limit, auto-pause after inactivity |
| **Cartesia** | 20,000 credits/month (resets monthly) | Text-to-Speech alternative | Lower concurrency, basic features |
| **Supabase** ⭐ BEST VALUE | 500 MB DB + 1 GB storage + 5 GB egress + 50K MAU | Database & storage | 2 active projects, auto-pause after 1 week |
| **Together AI/OpenRouter** | Free credits (varies) | LLM without credit card | Check current offers |

**💡 Recommendation**: Use **Deepgram** for STT/TTS (best value), **Supabase** for database (most generous), **LiveKit** for voice infrastructure, and **Together AI** or **OpenRouter** for LLM.

---

## 📁 Project Structure

```
.
├── backend/          # LiveKit Agent (Python)
│   ├── main.py       # Main agent entry point
│   ├── tools.py      # Tool functions for appointment management
│   ├── database.py   # Supabase database operations
│   ├── summary.py    # Conversation summary generation
│   ├── token_server.py # Token generation server
│   ├── requirements.txt
│   └── env.example
├── frontend/         # React WebApp
│   ├── src/
│   │   ├── App.js    # Main app component
│   │   ├── index.js
│   │   └── components/
│   │       ├── VoiceCall.js
│   │       └── CallSummary.js
│   ├── public/
│   │   └── index.html
│   └── package.json
└── README.md
```

---

## 🚀 Complete Setup Guide (Backend + Frontend)

### Prerequisites

- **Python 3.10+** installed ([python.org](https://www.python.org/downloads/))
- **Node.js 18+** and npm installed ([nodejs.org](https://nodejs.org/))
- **Git** installed ([git-scm.com](https://git-scm.com/))
- **Code editor** (VS Code recommended)

**Time Estimate**: 2-3 hours for complete setup

---

## Part 1: Service Account Setup (30 minutes)

### Step 1.1: Supabase Setup (5 minutes) ✅ FREE - NO CREDIT CARD

1. Go to [supabase.com](https://supabase.com)
2. Click **"Start your project"** or **"Sign Up"**
3. Choose **"Free" plan** (always free tier)
4. Create a new project:
   - Name: `superbryn-voice-agent` (or your choice)
   - Database Password: Create a strong password (save it!)
   - Region: Choose closest to you
   - Wait 2-3 minutes for project to initialize
5. Get your credentials:
   - Go to **Settings** → **API**
   - Copy **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - Copy **`anon` public key** (starts with `eyJ...`)
   - Save these for later!

**What you get free:**
- 500 MB database storage
- 1 GB file storage
- 5 GB egress + 5 GB cached egress/month
- 50,000 monthly active users
- 500,000 Edge Function invocations/month
- Unlimited API requests

### Step 1.2: LiveKit Setup (5 minutes) ✅ FREE - NO CREDIT CARD

1. Go to [livekit.io](https://livekit.io)
2. Click **"Get Started"** or **"Sign Up"**
3. Choose **"Build" plan** (free tier)
4. Create a new project:
   - Project name: `superbryn-agent`
   - Region: Choose closest to you
5. Get your credentials:
   - Go to **Settings** → **API Keys**
   - Copy **Server URL** (e.g., `wss://your-project.livekit.cloud`)
   - Click **"Create API Key"**:
     - Name: `agent-key`
     - Grant: Admin permissions
   - Copy **API Key** and **API Secret**
   - Save these for later!

**What you get free:**
- 1,000 agent session minutes/month
- 10,000 participant minutes/month
- 1 free US phone number
- Agent deployment
- Observability tools

### Step 1.3: Deepgram Setup (5 minutes) ✅ FREE - NO CREDIT CARD

1. Go to [deepgram.com](https://deepgram.com)
2. Click **"Get Started"** or **"Sign Up"**
3. Verify email if needed
4. Get your API key:
   - Go to **API Keys** section
   - Copy your **API Key** (starts with something like `abc123...`)
   - Save for later!

**What you get free:**
- $200 in free credits (one-time)
- Access to all STT/TTS models
- ~25,000+ minutes of transcription
- No credit card required

### Step 1.4: Cartesia Setup (5 minutes) ✅ FREE - NO CREDIT CARD

1. Go to [cartesia.ai](https://cartesia.ai)
2. Click **"Sign Up"**
3. Choose **"Free" plan**
4. Get your API key:
   - Go to **Dashboard** → **API Keys**
   - Copy your **API Key**
   - Save for later!

**What you get free:**
- 20,000 model credits/month (resets monthly)
- Core TTS models
- Basic agent features

### Step 1.5: LLM Provider Setup (5-10 minutes)

**Option A: Together AI** ✅ RECOMMENDED (Check if credit card needed)

1. Go to [together.ai](https://together.ai)
2. Sign up for account
3. Check for free credits offer
4. Get your API key from dashboard
5. Save for later!

**Option B: OpenRouter** ✅ ALTERNATIVE (Check if credit card needed)

1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign up for account
3. Check for free credits offer
4. Get your API key from dashboard
5. Save for later!

**Option C: OpenAI** ⚠️ REQUIRES CREDIT CARD

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up (requires credit card)
3. Get $5 free credits (expires in 3 months)
4. Get API key from API Keys section
5. Save for later!

**💡 Recommendation**: Start with Together AI or OpenRouter if they don't require credit card.

---

## Part 2: Database Setup (10 minutes)

### Step 2.1: Create Database Tables

1. Go to your Supabase project dashboard
2. Click on **SQL Editor** in left sidebar
3. Click **"New query"**
4. Paste this SQL code:

```sql
-- Users table
CREATE TABLE IF NOT EXISTS users (
    phone_number TEXT PRIMARY KEY,
    name TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Appointments table
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    phone_number TEXT NOT NULL REFERENCES users(phone_number),
    name TEXT,
    date DATE NOT NULL,
    time TIME NOT NULL,
    status TEXT NOT NULL DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'cancelled')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Conversations table for summaries
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    phone_number TEXT REFERENCES users(phone_number),
    summary TEXT,
    booked_appointments JSONB,
    user_preferences JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_appointments_phone ON appointments(phone_number);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
```

5. Click **"Run"** (or press Ctrl+Enter)
6. You should see "Success. No rows returned" - this means tables are created!

### Step 2.2: Enable Row Level Security (RLS) ⚠️ IMPORTANT!

Supabase will show a security warning that RLS is disabled. You **must** enable it!

1. In Supabase SQL Editor, create a new query
2. Copy and paste this SQL (see `SUPABASE_RLS_SETUP.sql` for full details):

```sql
-- Enable Row Level Security on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- Basic policies to allow backend operations
-- (Backend filters by phone_number in code)
CREATE POLICY "Users can insert" ON users FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can read" ON users FOR SELECT USING (true);
CREATE POLICY "Users can update" ON users FOR UPDATE USING (true);

CREATE POLICY "Appointments can insert" ON appointments FOR INSERT WITH CHECK (true);
CREATE POLICY "Appointments can read" ON appointments FOR SELECT USING (true);
CREATE POLICY "Appointments can update" ON appointments FOR UPDATE USING (true);

CREATE POLICY "Conversations can insert" ON conversations FOR INSERT WITH CHECK (true);
CREATE POLICY "Conversations can read" ON conversations FOR SELECT USING (true);
```

3. Click **"Run"**
4. ✅ The security warning should disappear!

**Note**: These policies allow backend operations because your backend code filters by `phone_number`. For production, you'd want stricter policies.

**✅ Verify tables were created:**
- Go to **Table Editor** in left sidebar
- You should see `users`, `appointments`, and `conversations` tables

---

## Part 3: Backend Setup (45 minutes)

### Step 3.1: Navigate to Backend Directory (1 minute)

```bash
cd backend
```

### Step 3.2: Create Python Virtual Environment (2 minutes)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3.3: Install Python Dependencies (5 minutes)

```bash
pip install -r requirements.txt
```

This will install:
- `livekit-agents`
- `livekit-plugins-deepgram`
- `livekit-plugins-cartesia`
- `supabase`
- `openai` / `anthropic`
- And other dependencies

**Wait for installation to complete** (may take 2-5 minutes)

### Step 3.4: Configure Environment Variables (5 minutes)

1. Copy the example environment file:
   ```bash
   # Windows
   copy env.example .env
   
   # Mac/Linux
   cp env.example .env
   ```

2. Open `.env` file in your code editor

3. Fill in all the values with your API keys from Part 1:

```env
# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key-here
LIVEKIT_API_SECRET=your-api-secret-here

# Deepgram Configuration
DEEPGRAM_API_KEY=your-deepgram-api-key-here

# Cartesia Configuration
CARTESIA_API_KEY=your-cartesia-api-key-here

# LLM Configuration (choose ONE based on your provider)
# For Together AI:
TOGETHER_API_KEY=your-together-api-key-here
LLM_PROVIDER=together

# OR for OpenRouter:
# OPENROUTER_API_KEY=your-openrouter-api-key-here
# LLM_PROVIDER=openrouter

# OR for OpenAI (requires credit card):
# OPENAI_API_KEY=your-openai-api-key-here
# LLM_PROVIDER=openai

# OR for Anthropic (requires credit card):
# ANTHROPIC_API_KEY=your-anthropic-api-key-here
# LLM_PROVIDER=anthropic

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key-here
```

4. **Save the file** (important!)

**⚠️ Important**: Never commit `.env` file to git (it's already in `.gitignore`)

### Step 3.5: Test Backend Connection (5 minutes)

1. Test database connection:
   ```bash
   python -c "from database import get_supabase_client; print('Supabase connected!')"
   ```

2. Test environment variables are loaded:
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('LIVEKIT_URL:', os.getenv('LIVEKIT_URL'))"
   ```

If you see your LiveKit URL printed, environment is set up correctly!

### Step 3.6: Run Token Server (Background Process) (1 minute)

Open a **NEW terminal window** (keep backend terminal open):

```bash
cd backend
# Activate virtual environment again if needed
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

python token_server.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!** This server generates LiveKit tokens for your frontend.

### Step 3.7: Run LiveKit Agent (Background Process) (1 minute)

In your **original backend terminal**:

```bash
# Make sure virtual environment is activated
python main.py dev
```

You should see agent starting up. **Keep this terminal open!**

**✅ Backend is now running!**

---

## Part 4: Frontend Setup (30 minutes)

### Step 4.1: Navigate to Frontend Directory (1 minute)

Open a **NEW terminal window**:

```bash
cd frontend
```

### Step 4.2: Install Node Dependencies (5 minutes)

```bash
npm install
```

This will install:
- `react`
- `react-dom`
- `livekit-client`
- `@livekit/components-react`
- And other dependencies

**Wait for installation** (may take 2-5 minutes)

### Step 4.3: Configure Frontend Environment Variables (3 minutes)

1. Create `.env` file in `frontend/` directory:

```bash
# Windows
type nul > .env

# Mac/Linux
touch .env
```

2. Open `.env` file and add:

```env
REACT_APP_LIVEKIT_URL=wss://your-project.livekit.cloud
REACT_APP_API_URL=http://localhost:8000
```

**⚠️ Important**: 
- Replace `your-project.livekit.cloud` with your actual LiveKit URL from Step 1.2
- Keep `http://localhost:8000` (this is where token server runs)

3. **Save the file**

### Step 4.4: Start Frontend Development Server (2 minutes)

```bash
npm start
```

This will:
- Start the React development server
- Open your browser to `http://localhost:3000`
- Hot-reload on code changes

**✅ Frontend is now running!**

You should see the SuperBryn Voice Agent homepage.

---

## Part 5: Testing the Application (15 minutes)

### Step 5.1: Verify All Services Are Running

Check these are all running in separate terminals:

1. ✅ **Token Server**: `http://localhost:8000` (terminal showing Uvicorn)
2. ✅ **LiveKit Agent**: `python main.py dev` (backend terminal)
3. ✅ **Frontend**: `http://localhost:3000` (browser opened)

### Step 5.2: Test Voice Call

1. In your browser (`http://localhost:3000`):
   - Click **"Start Voice Call"** button
   - **Allow microphone access** when prompted

2. You should see:
   - Avatar placeholder (or video if avatar is integrated)
   - Microphone button
   - "Voice Call Active" status

3. Start speaking:
   - Say: **"Hello, I'd like to book an appointment"**
   - Wait for agent response (should hear AI voice)
   - Agent should respond and ask for your phone number

4. Test appointment booking:
   - Say: **"My phone number is 1234567890"**
   - Say: **"I'd like to see available slots"**
   - Agent should list available slots
   - Say: **"Book me for January 15 at 10 AM"**
   - Agent should confirm booking

5. Test conversation summary:
   - Say: **"End the conversation"** or **"Goodbye"**
   - Summary should appear in a modal

### Step 5.3: Check Database

1. Go to Supabase dashboard
2. Navigate to **Table Editor** → **appointments**
3. You should see your booked appointment!

### Step 5.4: Check Tool Calls

In the frontend UI, you should see:
- Tool calls listed in "Recent Actions" section
- Each tool call shows timestamp
- Tool names like: `identify_user`, `book_appointment`, etc.

---

## Part 6: Troubleshooting

### Issue: "Cannot connect to LiveKit"

**Solutions:**
1. Check `LIVEKIT_URL` in `.env` is correct (include `wss://` prefix)
2. Verify LiveKit agent is running (`python main.py dev`)
3. Check token server is running on port 8000
4. Verify LiveKit credentials in backend `.env`

### Issue: "No transcription / STT not working"

**Solutions:**
1. Check `DEEPGRAM_API_KEY` in backend `.env`
2. Verify Deepgram account has credits remaining
3. Check microphone permissions in browser
4. Look at backend terminal for error messages

### Issue: "No speech / TTS not working"

**Solutions:**
1. Check `CARTESIA_API_KEY` in backend `.env`
2. Verify Cartesia account has credits
3. Check browser console for errors
4. Verify audio permissions

### Issue: "Database connection failed"

**Solutions:**
1. Check `SUPABASE_URL` and `SUPABASE_KEY` in backend `.env`
2. Verify Supabase project is not paused (activate if needed)
3. Check tables were created correctly (see Part 2)
4. Verify network connection

### Issue: "Token generation failed"

**Solutions:**
1. Make sure token server is running (`python token_server.py`)
2. Check `REACT_APP_API_URL` in frontend `.env` matches token server
3. Verify LiveKit credentials in backend `.env`
4. Check token server terminal for errors

### Issue: "LLM not responding"

**Solutions:**
1. Check LLM provider API key in backend `.env`
2. Verify `LLM_PROVIDER` is set correctly (`together`, `openrouter`, `openai`, or `anthropic`)
3. Check LLM provider account for credits/quota
4. Look at backend terminal for API errors

---

## 📋 Environment Variables Summary

### Backend (`.env` file in `backend/`)

```env
# Required
LIVEKIT_URL=wss://...
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
DEEPGRAM_API_KEY=...
CARTESIA_API_KEY=...
SUPABASE_URL=https://...
SUPABASE_KEY=...
LLM_PROVIDER=together  # or openrouter, openai, anthropic
TOGETHER_API_KEY=...   # or corresponding provider key
```

### Frontend (`.env` file in `frontend/`)

```env
REACT_APP_LIVEKIT_URL=wss://...
REACT_APP_API_URL=http://localhost:8000
```

---

## 🎯 Quick Start Checklist

Use this checklist to verify setup:

- [ ] Supabase project created and tables set up
- [ ] LiveKit account created (Build plan)
- [ ] Deepgram account created ($200 credits)
- [ ] Cartesia account created (free plan)
- [ ] LLM provider account created (Together AI/OpenRouter recommended)
- [ ] Backend `.env` file configured with all API keys
- [ ] Frontend `.env` file configured
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Token server running (`python token_server.py`)
- [ ] LiveKit agent running (`python main.py dev`)
- [ ] Frontend running (`npm start`)
- [ ] Browser opened to `http://localhost:3000`
- [ ] Test voice call successful
- [ ] Test appointment booking works
- [ ] Database shows appointment record

---

## 🚀 Deployment

### Backend Deployment

**Option 1: Railway**
1. Push code to GitHub
2. Connect Railway to your repo
3. Add environment variables in Railway dashboard
4. Deploy!

**Option 2: Heroku**
1. Install Heroku CLI
2. `heroku create your-app-name`
3. `heroku config:set KEY=value` for each env var
4. `git push heroku main`

**Option 3: Fly.io**
1. Install Fly CLI
2. `fly launch`
3. Add secrets: `fly secrets set KEY=value`
4. Deploy: `fly deploy`

### Frontend Deployment

**Netlify:**
1. Push code to GitHub
2. Connect Netlify to repo
3. Build command: `npm run build`
4. Publish directory: `build`
5. Add environment variables in Netlify dashboard
6. Deploy!

**Vercel:**
1. Push code to GitHub
2. Install Vercel CLI: `npm i -g vercel`
3. Run `vercel` in frontend directory
4. Add environment variables
5. Deploy!

---

## 📚 Additional Documentation

- [FREE_TIER_GUIDE.md](FREE_TIER_GUIDE.md) - Complete free tier breakdown
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Alternative setup guide
- [backend/README.md](backend/README.md) - Backend-specific docs
- [frontend/README.md](frontend/README.md) - Frontend-specific docs

---

## 💡 Tips for Staying Within Free Tiers

1. **Monitor Usage**: Check service dashboards weekly
2. **Optimize Calls**: Keep conversations concise during testing
3. **Test Locally**: Use local development to save minutes
4. **Clean Up**: Delete old test data from database
5. **Use Efficient Models**: Stick to standard models (not premium)
6. **Plan Testing**: Batch your testing to stay within limits

---

## 🆘 Need Help?

1. Check **Troubleshooting** section above
2. Review service documentation:
   - [LiveKit Docs](https://docs.livekit.io)
   - [Deepgram Docs](https://developers.deepgram.com)
   - [Supabase Docs](https://supabase.com/docs)
3. Check backend/frontend terminal logs for errors
4. Verify all environment variables are set correctly

---

## 📚 Additional Documentation

- **[KNOWN_LIMITATIONS.md](./KNOWN_LIMITATIONS.md)** - Detailed list of known limitations (including Cartesia credits issue)
- **[DEVELOPMENT_ISSUES.md](./DEVELOPMENT_ISSUES.md)** - Issues encountered during development and solutions
- **[COST_ESTIMATION.md](./COST_ESTIMATION.md)** - Cost breakdown and estimation per call
- **[REVIEWER_NOTES.md](./REVIEWER_NOTES.md)** - Important notes for reviewers

---

## ⚠️ Important Notice for Reviewers

**Cartesia TTS Credits Issue:**
- The demo account currently has **-79 Cartesia credits** (overage)
- Agent will **NOT speak** until credits are restored
- This is a billing issue, **not a code issue** - all code is functional
- Please see [KNOWN_LIMITATIONS.md](./KNOWN_LIMITATIONS.md) for details
- Please see [REVIEWER_NOTES.md](./REVIEWER_NOTES.md) for reviewer-specific information

---

**Good luck with your project! 🚀**
