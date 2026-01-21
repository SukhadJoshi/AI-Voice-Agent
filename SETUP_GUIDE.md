# SuperBryn Voice Agent - Complete Setup Guide

This guide will walk you through setting up the entire voice agent system from scratch.

## Prerequisites

- Python 3.9+ installed
- Node.js 16+ and npm installed
- Accounts for the following services (all have free tiers):
  - LiveKit Cloud (or self-hosted)
  - Deepgram
  - Cartesia
  - Supabase
  - LLM provider (OpenAI, Anthropic, Together AI, or OpenRouter)

## Step 1: Get API Keys

> 💡 **All services below have free tiers!** See [FREE_TIER_GUIDE.md](FREE_TIER_GUIDE.md) for details on which require credit cards.

### 1.1 LiveKit ✅ FREE (No Credit Card)
1. Sign up at [livekit.io](https://livekit.io)
2. Create a new project (use "Build" free plan)
3. Copy your:
   - Server URL (e.g., `wss://your-project.livekit.cloud`)
   - API Key
   - API Secret
4. **Free Tier**: 1,000 agent session minutes/month, 10,000 participant minutes/month

### 1.2 Deepgram ✅ FREE (No Credit Card)
1. Sign up at [deepgram.com](https://deepgram.com)
2. Create a new project
3. Copy your API Key
4. **Free Tier**: $200 in free credits (one-time, not monthly) - no credit card required

### 1.3 Cartesia ✅ FREE (No Credit Card)
1. Sign up at [cartesia.ai](https://cartesia.ai)
2. Get your API key from the dashboard
3. **Free Tier**: 20,000 model credits/month - no credit card required

### 1.4 Supabase ✅ FREE (No Credit Card)
1. Sign up at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Settings > API
4. Copy:
   - Project URL
   - `anon` public key
5. **Free Tier**: 500 MB database, 2 GB bandwidth - no credit card required

### 1.5 LLM Provider
Choose one (⚠️ = requires credit card):

**Option A: OpenAI** ⚠️ **REQUIRES CREDIT CARD**
- Sign up at [openai.com](https://openai.com)
- Get API key from dashboard
- **Free Credits**: $5 free credits (one-time), expires in 3 months
- **Note**: Credit card required for API access

**Option B: Anthropic** ⚠️ **REQUIRES CREDIT CARD**
- Sign up at [anthropic.com](https://anthropic.com)
- Get API key
- **Note**: Credit card required for API access

**Option C: Together AI** ✅ **RECOMMENDED (Free credits, check if credit card needed)**
- Sign up at [together.ai](https://together.ai)
- Get API key
- **Free Credits**: Often offers free credits for new users

**Option D: OpenRouter** ✅ **RECOMMENDED (Free credits, check if credit card needed)**
- Sign up at [openrouter.ai](https://openrouter.ai)
- Get API key
- **Free Credits**: Often offers free credits for new users

**💡 Recommendation**: Use **Together AI** or **OpenRouter** for truly free LLM access (check current offers for credit card requirements)

## Step 2: Set Up Backend

### 2.1 Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2.2 Configure Environment
```bash
cp env.example .env
```

Edit `.env` with your API keys:
```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

DEEPGRAM_API_KEY=your-deepgram-key
CARTESIA_API_KEY=your-cartesia-key

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

OPENAI_API_KEY=your-openai-key
# OR use one of these instead:
# ANTHROPIC_API_KEY=your-anthropic-key
# TOGETHER_API_KEY=your-together-key
# OPENROUTER_API_KEY=your-openrouter-key

LLM_PROVIDER=openai
```

### 2.3 Set Up Database
1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Run this SQL:

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

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_appointments_phone ON appointments(phone_number);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
```

### 2.4 Test Backend
```bash
# Run the agent (in development mode)
python main.py dev

# In another terminal, run the token server
python token_server.py
```

## Step 3: Set Up Frontend

### 3.1 Install Dependencies
```bash
cd frontend
npm install
```

### 3.2 Configure Environment
Create `.env` file in `frontend/`:
```env
REACT_APP_LIVEKIT_URL=wss://your-project.livekit.cloud
REACT_APP_API_URL=http://localhost:8000
```

### 3.3 Start Development Server
```bash
npm start
```

The app should open at `http://localhost:3000`

## Step 4: Test the System

1. Open the frontend in your browser
2. Click "Start Voice Call"
3. Allow microphone access
4. Try saying: "Hello, I'd like to book an appointment"
5. The agent should respond and guide you through booking

## Step 5: Deploy (Optional)

### Backend Deployment
- Deploy to Heroku, Railway, or similar
- Set environment variables in your hosting platform
- For LiveKit Cloud, you can deploy agents directly

### Frontend Deployment
- **Netlify**: 
  ```bash
  npm run build
  # Deploy the build folder
  ```
- **Vercel**:
  ```bash
  npm i -g vercel
  vercel
  ```

## Troubleshooting

### Backend Issues
- **Import errors**: Make sure all dependencies are installed
- **Database errors**: Verify Supabase connection and table creation
- **API key errors**: Double-check all keys in `.env`

### Frontend Issues
- **Connection errors**: Verify `REACT_APP_LIVEKIT_URL` is correct
- **Token errors**: Make sure token server is running
- **Microphone not working**: Check browser permissions

### Common Issues
- **Agent not responding**: Check LiveKit agent logs
- **No transcription**: Verify Deepgram API key
- **No speech**: Verify Cartesia API key
- **Tool calls not working**: Check LLM API key and provider setting

## Next Steps

1. **Integrate Avatar**: Set up Beyond Presence or Tavus for visual avatar
2. **Add Cost Tracking**: Implement optional cost tracking feature
3. **Improve Error Handling**: Add more robust error handling
4. **Add Tests**: Write unit and integration tests

## Support

For issues, check:
- LiveKit docs: https://docs.livekit.io
- Deepgram docs: https://developers.deepgram.com
- Supabase docs: https://supabase.com/docs


Reference Guide to start the service on my cmd :-

# Terminal 1 - Backend folder
cd "C:\SuperBryn_Task Challenge\backend"
venv\Scripts\activate
python token_server.py

# Terminal 2 - Backend folder  
cd "C:\SuperBryn_Task Challenge\backend"
venv\Scripts\activate
python main.py dev

# Terminal 3 - Frontend folder
cd "C:\SuperBryn_Task Challenge\frontend"
npm start
