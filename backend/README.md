# SuperBryn Voice Agent - Backend

LiveKit Agent implementation for the AI voice agent with appointment management capabilities.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Copy `env.example` to `.env` and fill in your API keys:
   ```bash
   cp env.example .env
   ```

   Required environment variables:
   - `LIVEKIT_URL`: Your LiveKit server URL
   - `LIVEKIT_API_KEY`: LiveKit API key
   - `LIVEKIT_API_SECRET`: LiveKit API secret
   - `DEEPGRAM_API_KEY`: Deepgram API key for speech-to-text
   - `CARTESIA_API_KEY`: Cartesia API key for text-to-speech
   - `SUPABASE_URL`: Supabase project URL
   - `SUPABASE_KEY`: Supabase anon key
   - `LLM_PROVIDER`: Choose from `openai`, `anthropic`, `together`, `openrouter`
   - LLM API key based on provider (e.g., `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`)

3. **Set up Supabase database:**
   Run the following SQL in your Supabase SQL editor:
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

4. **Run the agent:**
   ```bash
   python main.py dev
   ```

## Features

- **Speech-to-Text**: Deepgram integration
- **Text-to-Speech**: Cartesia integration
- **LLM**: Supports OpenAI, Anthropic, Together AI, or OpenRouter
- **Tool Calling**: 7 tools for appointment management
- **Database**: Supabase for data persistence
- **Conversation Summary**: Automatic summary generation at end of call

## Tool Functions

1. `identify_user` - Store user phone number
2. `fetch_slots` - Get available appointment slots
3. `book_appointment` - Book a new appointment
4. `retrieve_appointments` - Get user's appointments
5. `cancel_appointment` - Cancel an appointment
6. `modify_appointment` - Change appointment date/time
7. `end_conversation` - End call and generate summary

## Deployment

The agent can be deployed to any platform that supports Python. For LiveKit Cloud, you can use their agent deployment service.

## Known Limitations

⚠️ **IMPORTANT: Cartesia TTS Credits Issue**
- The demo account currently has **-79 Cartesia credits** (overage)
- Agent will **NOT speak** until credits are restored (monthly reset or upgrade)
- This is a billing issue, not a code issue - all code is functional
- See `../KNOWN_LIMITATIONS.md` for details

Other Limitations:
- Avatar integration (Beyond Presence/Tavus) needs to be configured separately
- Cost tracking is optional and not implemented by default
- Free LLM models have limitations (rate limits, no tool calling support)

**For detailed information:**
- See `../KNOWN_LIMITATIONS.md` for full list of limitations
- See `../DEVELOPMENT_ISSUES.md` for issues encountered during development
- See `../COST_ESTIMATION.md` for cost breakdown information

