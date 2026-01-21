# Service Comparison & Selection Guide

These services serve **different purposes** - most are NOT alternatives to each other!

---

## 📊 Service Roles (They Work Together!)

| Service | What It Does | Required? | Alternative To? |
|---------|--------------|-----------|-----------------|
| **LiveKit** | Voice infrastructure/real-time communication | ✅ REQUIRED | None - it's the core framework |
| **Deepgram** | Speech-to-Text (STT) - converts voice to text | ✅ REQUIRED | OpenAI Whisper, Google Speech-to-Text |
| **Cartesia** | Text-to-Speech (TTS) - converts text to voice | ✅ REQUIRED (or use Deepgram TTS) | Deepgram TTS, OpenAI TTS, ElevenLabs |
| **Together AI** | LLM - powers conversation logic | ⚠️ Choose ONE | OpenRouter, OpenAI, Anthropic |
| **OpenRouter** | LLM - powers conversation logic | ⚠️ Choose ONE | Together AI, OpenAI, Anthropic |

---

## 🤔 The Real Question: Which LLM Provider?

The only choice you need to make is between:

### Together AI vs OpenRouter (Choose ONE for LLM)

Both provide LLM access, but they're different:

#### Together AI ✅ RECOMMENDED
- **What**: Provides access to open-source LLMs (Llama, Mistral, etc.)
- **Free Credits**: Often offers free credits for new users
- **Models**: Access to multiple open-source models
- **Credit Card**: May not require (check current offers)
- **Best For**: Free tier, open-source models
- **Website**: [together.ai](https://together.ai)

#### OpenRouter ✅ ALTERNATIVE
- **What**: Aggregates multiple LLM providers (OpenAI, Anthropic, etc.)
- **Free Credits**: Often offers free credits
- **Models**: Access to models from multiple providers (OpenAI, Anthropic, etc.)
- **Credit Card**: May not require (check current offers)
- **Best For**: Want access to premium models (GPT-4, Claude) without direct account
- **Website**: [openrouter.ai](https://openrouter.ai)

#### Comparison Table

| Feature | Together AI | OpenRouter |
|---------|-------------|------------|
| **Free Credits** | ✅ Often available | ✅ Often available |
| **Credit Card Required** | ⚠️ Check current offers | ⚠️ Check current offers |
| **Model Types** | Open-source (Llama, Mistral) | Multiple (OpenAI, Anthropic, etc.) |
| **Pricing** | Usually cheaper | Varies by model |
| **Model Quality** | Good (open-source) | Excellent (premium models available) |

**💡 Recommendation**: 
- If you want **100% free and no credit card**: Check current Together AI offers
- If you want **access to GPT-4/Claude**: OpenRouter might be better
- Start with **Together AI** if they don't require credit card

---

## ✅ What You Actually Need

### You Need ALL of These:

1. ✅ **LiveKit** - Can't skip (it's the framework)
2. ✅ **Deepgram** - Can't skip (STT is hardcoded)
3. ✅ **Cartesia** - Required OR use Deepgram TTS instead
4. ✅ **One LLM Provider** - Choose Together AI OR OpenRouter

### The Only Choice:

**Together AI** vs **OpenRouter** - Choose ONE for LLM

Everything else is required!

---

## 🎯 Recommended Stack (Minimum)

**For 100% Free (No Credit Card):**

1. ✅ **LiveKit** - Free Build plan
2. ✅ **Deepgram** - $200 free credits (STT)
3. ✅ **Deepgram** - Also use for TTS (skip Cartesia if you want)
   - OR **Cartesia** - Free plan (20K credits/month)
4. ✅ **Together AI** - Free credits (choose as LLM)
   - OR **OpenRouter** - Free credits (alternative LLM)
5. ✅ **Supabase** - Free tier (database)

**Total: 5 services (or 4 if using Deepgram for both STT/TTS)**

---

## 🔄 Quick Decision Guide

### Q: Should I use Together AI or OpenRouter?

**Use Together AI if:**
- ✅ Want free tier without credit card
- ✅ Don't need GPT-4 or Claude specifically
- ✅ Want open-source models
- ✅ Want potentially cheaper pricing

**Use OpenRouter if:**
- ✅ Want access to GPT-4, Claude, or other premium models
- ✅ Want to switch between different providers easily
- ✅ Don't mind checking if credit card is required

### Q: Should I use Cartesia or Deepgram TTS?

**Use Cartesia if:**
- ✅ Want separate service (as specified in task)
- ✅ Free 20K credits/month is enough
- ✅ Task specifically mentions Cartesia

**Use Deepgram TTS if:**
- ✅ Want to minimize services (one less account)
- ✅ Already using Deepgram for STT
- ✅ $200 credits cover both STT and TTS needs

---

## 💡 My Recommendation

**For this assignment:**

1. ✅ **LiveKit** - Required, free
2. ✅ **Deepgram** - Required, free ($200 credits)
3. ✅ **Cartesia** - Use it (task mentions it, free tier available)
4. ✅ **Together AI** - Start here (check for free credits)
   - If Together AI requires credit card, try OpenRouter
5. ✅ **Supabase** - Required, free

**Skip:**
- ❌ Avatar service (Beyond Presence/Tavus) - Use placeholder

This gives you everything needed while staying on free tiers!

