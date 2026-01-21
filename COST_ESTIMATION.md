# Cost Estimation & Breakdown

## Cost Per Call Estimation

### Current Implementation Status

**Note:** Cost estimation is **NOT yet implemented** in the codebase. This document outlines how it could be implemented and provides cost estimates based on typical usage.

---

## Service Costs

### 1. LiveKit (Voice Infrastructure)

**Free Tier:**
- 1,000 agent minutes/month (free)
- 10,000 participant minutes/month (free)
- Auto-pause after 7 days of inactivity

**Cost per Call (estimated):**
- Agent minutes: $0.06/minute (if exceeding free tier)
- Participant minutes: $0.014/minute (if exceeding free tier)
- **Typical 5-minute call:** ~$0.25 (if exceeding free tier)

**For This Project:**
- Using free tier - no cost expected for testing/demo

---

### 2. Deepgram (Speech-to-Text)

**Free Tier:**
- $200 one-time credits
- 1 credit ≈ 1 second of audio

**Cost per Call (estimated):**
- ~1 credit per second of user speech
- **Typical 5-minute call with 2 minutes of user speech:** ~120 credits ≈ $0.00 (within free tier)

**For This Project:**
- Using free tier credits - no cost expected

---

### 3. Cartesia (Text-to-Speech)

**Free Tier:**
- 20,000 model credits/month (resets monthly)
- 1 credit per character for TTS

**Cost per Call (estimated):**
- Average agent response: ~150 characters ≈ 150 credits
- **Typical 5-minute call with 10 agent responses:** ~1,500 credits
- If exceeding free tier: ~$0.0015 per character (varies by model)

**Current Status:**
- ⚠️ Account at -79 credits (service paused)
- **Recommendation:** Wait for monthly reset or upgrade to Pro ($5/month)

---

### 4. LLM (OpenRouter - Meta Llama 3.2 3B Free)

**Free Tier:**
- `meta-llama/llama-3.2-3b-instruct:free` - Completely free
- Rate limited but no cost

**Cost per Call (estimated):**
- **$0.00** (using free model)
- If upgrading to paid models:
  - GPT-4o-mini: ~$0.15 per 1M input tokens, $0.60 per 1M output tokens
  - Typical call: ~$0.01-0.05

---

### 5. Supabase (Database)

**Free Tier:**
- 500 MB database
- 1 GB file storage
- 5 GB bandwidth
- 50,000 monthly active users

**Cost per Call (estimated):**
- **$0.00** (within free tier limits)
- Database queries: Negligible cost
- Storage: ~1 KB per appointment record

---



