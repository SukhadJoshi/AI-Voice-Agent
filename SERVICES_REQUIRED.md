# Services Required - Breakdown

## ✅ ABSOLUTELY REQUIRED (5 services)

### 1. **LiveKit** - REQUIRED ⚠️
**Why**: Core voice agent framework. The entire backend is built on LiveKit Agents.
**Can you skip?** ❌ No - everything depends on it.
**Free?** ✅ Yes - Free "Build" plan (1,000 agent min/month)

### 2. **Deepgram** - REQUIRED ⚠️
**Why**: Speech-to-Text (STT). Hardcoded in `backend/main.py` line 196.
**Can you skip?** ❌ No - code explicitly uses `deepgram.STT()`
**Free?** ✅ Yes - $200 free credits (one-time)
**Alternative**: Could theoretically replace with OpenAI Whisper, but would require code changes

### 3. **LLM Provider** - REQUIRED ⚠️
**Why**: Needed for conversation logic and tool calling. Used in `backend/main.py` lines 202-210.
**Can you skip?** ❌ No - agent won't understand or respond without LLM
**Free?** ✅ Together AI/OpenRouter offer free credits (check current offers)
**Options**: Choose ONE:
- Together AI ✅ (recommended - may not need credit card)
- OpenRouter ✅ (may not need credit card)
- OpenAI ⚠️ (requires credit card, but $5 free credits)
- Anthropic ⚠️ (requires credit card)

### 4. **Database (Supabase)** - REQUIRED ⚠️
**Why**: Stores appointments, users, conversation summaries. Hardcoded in `backend/database.py`.
**Can you skip?** ❌ No - appointments need to be stored somewhere
**Free?** ✅ Yes - Free tier (500 MB DB + 5 GB egress)
**Alternative**: Could use PostgreSQL/MySQL self-hosted, but requires more setup

### 5. **Text-to-Speech (TTS)** - REQUIRED ⚠️
**Currently**: Cartesia (hardcoded in `backend/main.py` line 199)
**Can you skip?** ❌ No - agent needs to speak responses
**Free?** ✅ Yes - Cartesia free plan (20K credits/month)

---

## 🤔 OPTIONAL (1 service)

### 6. **Avatar Service (Beyond Presence/Tavus)** - OPTIONAL ✅
**Why**: Task mentions it, but we already have a placeholder
**Can you skip?** ✅ **YES!** - The code already has a placeholder avatar that works
**Free?** ⚠️ Unknown - check their pricing
**Recommendation**: **Skip for now** - use the placeholder. You can add this later if needed.

---

## 💡 Can You Reduce to 4 Services?

**YES!** Here's how:

### Option 1: Use Deepgram for BOTH STT and TTS (Skip Cartesia)

**Changes needed:**
1. Modify `backend/main.py` to use Deepgram TTS instead of Cartesia
2. Deepgram supports both STT and TTS

**Services needed:**
1. ✅ LiveKit (required)
2. ✅ Deepgram (STT + TTS)
3. ✅ LLM Provider (required)
4. ✅ Supabase (required)

**Result**: 4 services instead of 5!

### Option 2: Use OpenAI for STT + TTS (Skip Deepgram + Cartesia)

**Changes needed:**
1. Replace Deepgram STT with OpenAI Whisper
2. Replace Cartesia TTS with OpenAI TTS
3. Requires code changes

**Services needed:**
1. ✅ LiveKit (required)
2. ✅ OpenAI (STT + TTS + LLM - all-in-one!)
3. ✅ Supabase (required)

**Result**: 3 services!
**⚠️ But**: OpenAI requires credit card

---

## 🎯 Recommended Minimum Setup

### For 100% Free (No Credit Card):

**Required:**
1. ✅ LiveKit (free Build plan)
2. ✅ Deepgram (STT - $200 free credits)
3. ✅ Cartesia (TTS - 20K credits/month) OR use Deepgram TTS instead
4. ✅ Supabase (free tier)
5. ✅ Together AI or OpenRouter (free credits - check if credit card needed)

**Optional:**
- ❌ Avatar service (skip - use placeholder)

**Total: 5 services (4 if you use Deepgram for both STT/TTS)**

---

## ⚠️ Important Notes

1. **The task specification mentions these specific services** (Deepgram, Cartesia), so using them might be what's expected.

2. **Cartesia can be replaced** - Deepgram does TTS too, so you could use just Deepgram for both STT and TTS.

3. **All services have free tiers** - so you won't pay anything if you stay within limits.

4. **Avatar is truly optional** - The code works perfectly fine with the placeholder avatar.

---

## 🚀 Simplest Setup (4 Services)

If you want the absolute minimum:

1. **LiveKit** - Voice infrastructure (free)
2. **Deepgram** - STT + TTS (both, $200 free credits)
3. **Supabase** - Database (free)
4. **Together AI** - LLM (free credits)

**Modification needed**: Change code to use Deepgram TTS instead of Cartesia.

Would you like me to show you how to modify the code to use Deepgram for both STT and TTS, eliminating the need for Cartesia?

