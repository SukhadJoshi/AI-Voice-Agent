# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### 1. Backend Setup (2 min)
```bash
cd backend
pip install -r requirements.txt
cp env.example .env
# Edit .env with your API keys
python main.py dev
```

### 2. Token Server (1 min)
```bash
# In another terminal
cd backend
python token_server.py
```

### 3. Frontend Setup (2 min)
```bash
cd frontend
npm install
# Create .env with REACT_APP_LIVEKIT_URL and REACT_APP_API_URL
npm start
```

### 4. Test
1. Open http://localhost:3000
2. Click "Start Voice Call"
3. Say: "Hello, I want to book an appointment"

## 📋 Required API Keys

Get these free tier accounts:
- ✅ LiveKit: https://livekit.io
- ✅ Deepgram: https://deepgram.com (200hrs/month free)
- ✅ Cartesia: https://cartesia.ai
- ✅ Supabase: https://supabase.com
- ✅ LLM: OpenAI/Anthropic/Together/OpenRouter

## 🗄️ Database Setup

Run this SQL in Supabase SQL Editor:
```sql
CREATE TABLE users (
    phone_number TEXT PRIMARY KEY,
    name TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    phone_number TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    status TEXT DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    phone_number TEXT,
    summary TEXT,
    booked_appointments JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## ⚠️ Common Issues

**"Module not found"** → Run `pip install -r requirements.txt`

**"Cannot connect"** → Check LiveKit URL and API keys in `.env`

**"No transcription"** → Verify Deepgram API key

**"Token error"** → Make sure token_server.py is running

## 📚 Full Documentation

- Complete setup: See `SETUP_GUIDE.md`
- Project details: See `PROJECT_SUMMARY.md`
- Backend docs: See `backend/README.md`
- Frontend docs: See `frontend/README.md`

