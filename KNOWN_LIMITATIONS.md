# Known Limitations

This document outlines known limitations and issues with the SuperBryn AI Voice Agent.

## ⚠️ Critical Limitations

### 1. Cartesia TTS Credits Issue

**Status:** Active limitation as of January 2025

**Issue:**
- The application uses **Cartesia** for Text-to-Speech (TTS) synthesis
- Cartesia Free plan provides ~20,000 model credits per month
- **IMPORTANT:** During development, the Cartesia account reached -79 credits (overage)
- TTS requests are currently failing with `Payment Required (status_code=402)` error

**Impact:**
- Agent greeting and responses cannot be synthesized
- Users will not hear the agent's voice until Cartesia credits are restored
- The code is functional - the limitation is purely due to API credits exhaustion

**Workarounds:**
1. **Wait for monthly credit reset** (recommended for testing)
   - Free plan credits typically reset at the start of each billing cycle
   - No action required, just wait for automatic reset

2. **Enable overages** (if immediate use is required)
   - Go to Cartesia dashboard → Enable overages
   - You will be charged for usage going forward
   - Recommended only if you need the service immediately

3. **Upgrade to paid plan**
   - Upgrade to Pro plan ($5/month) for 100,000 credits
   - Provides more reliable usage for development/testing


**⚠️ CRITICAL FOR DEPLOYMENT:**
- **DO NOT deploy with Cartesia API key** - Any usage will consume credits and increase debt (from -79 to -100+)
- Remove `CARTESIA_API_KEY` from production environment variables or set it to empty
- The agent won't speak in production, but won't consume credits
- Wait for monthly credit reset before enabling TTS in production

---

### 2. Free LLM Model Limitations

**Status:** Active limitation

**Issue:**
- The application uses `meta-llama/llama-3.2-3b-instruct:free` (OpenRouter) as the primary LLM
- Free models have limitations:
  - **No tool calling support** - Must use manual intent parsing and function calling
  - **Rate limiting** - May encounter 429 errors during high usage
  - **Lower quality responses** - May produce less coherent or repetitive responses

**Impact:**
- Agent may sometimes ask repetitive questions
- Responses may occasionally echo user input instead of providing proper guidance
- Tool calling is implemented via manual intent parsing as a workaround

**Workarounds:**
- Code includes fallback logic to parse user intent and call functions directly
- Rate limit handling with exponential backoff
- Echo detection and replacement logic to improve responses


---

## 📝 Summary

**Primary Blocking Issue:** Cartesia TTS credits (-79, service paused)

**All Other Issues:** Non-blocking, workarounds implemented

**Code Quality:** Production-ready, functional once API credits are restored


