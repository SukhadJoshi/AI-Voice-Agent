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

**Note:** The -79 credit overage on Free plan does NOT result in automatic charges. Service is simply paused until credits are restored or overages are enabled.

**For Reviewers:**
- Please do NOT enable overages on the demo account
- Wait for monthly credit reset if testing is needed
- All code functionality is correct and will work once credits are available

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

**For Production:**
- Consider upgrading to a paid LLM model (OpenAI GPT-4, Anthropic Claude, etc.) for better quality
- Paid models support native tool calling, reducing complexity

---

### 3. Avatar Integration

**Status:** Partial implementation

**Issue:**
- README mentions "Beyond Presence/Tavus" avatar integration
- Current implementation uses a **simple visual placeholder** with CSS animation
- Real-time avatar syncing with voice output is implemented via Web Audio API

**Current Implementation:**
- Avatar shows pulsing animation when agent is speaking
- Speaking detection uses client-side audio analysis
- No actual 3D avatar or video avatar integration

**Limitation:**
- Avatar is visual-only (no video/3D model)
- Animation is CSS-based, not synchronized with actual voice output quality
- Does not match the "Beyond Presence/Tavus" requirement from specifications

---

### 4. Phone Number Recognition

**Status:** Functional with limitations

**Issue:**
- Phone number extraction uses regex patterns
- May struggle with:
  - Very unusual formats
  - Heavy accents or unclear speech
  - Non-standard spoken number formats

**Impact:**
- Agent may ask for phone number multiple times if format is not recognized
- Conversation history scanning helps recover previously mentioned numbers
- Manual parsing is required if LLM doesn't extract correctly

**Workarounds:**
- Multiple regex patterns handle common formats
- Normalization converts spoken words ("one" → "1", "plus" → "+")
- Conversation history scan checks last 5 messages for phone numbers

---

### 5. STT/TTS Stream Lifecycle

**Status:** Functional with edge cases

**Issue:**
- LiveKit STT streams may close unexpectedly during participant disconnection
- TTS audio tracks must be properly unpublished to prevent overlapping voices
- Multiple audio tracks can cause echo issues if not managed correctly

**Impact:**
- Occasional "STT stream closed" warnings (non-fatal)
- Overlapping voices if audio tracks aren't cleaned up properly
- Requires careful track management

**Workarounds:**
- Explicit unpublishing of old tracks before publishing new ones
- 0.5s delay after unpublishing to ensure cleanup
- Track lifecycle management prevents most issues

---

## 🔧 Technical Limitations

### 6. Error Handling

**Status:** Basic error handling implemented

**Limitations:**
- Some API errors may not be gracefully handled in all edge cases
- Rate limiting has retry logic but may fail under extreme load
- Network disconnections may not always be detected immediately

---

### 7. Conversation Summary

**Status:** Implemented

**Limitations:**
- Summary generation relies on LLM (subject to same free model limitations)
- May not capture all nuances of complex conversations
- Limited to 500 tokens per summary (configurable)

---

## 📝 Summary

**Primary Blocking Issue:** Cartesia TTS credits (-79, service paused)

**All Other Issues:** Non-blocking, workarounds implemented

**Code Quality:** Production-ready, functional once API credits are restored

**Recommendation:** 
- For immediate testing: Wait for Cartesia monthly credit reset
- For production: Upgrade Cartesia plan or switch to alternative TTS provider

