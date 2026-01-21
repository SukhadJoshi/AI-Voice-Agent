# Cost Estimation & Breakdown

## 💰 Cost Per Call Estimation

### Current Implementation Status

**Note:** Cost estimation is **NOT yet implemented** in the codebase. This document outlines how it could be implemented and provides cost estimates based on typical usage.

---

## 📊 Service Costs

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

## 💵 Total Cost Per Call Estimate

### Using Free Tier Services:

**Typical 5-minute appointment booking call:**

| Service | Cost |
|---------|------|
| LiveKit | $0.00 (free tier) |
| Deepgram STT | $0.00 (free tier) |
| Cartesia TTS | $0.00 (free tier) |
| OpenRouter LLM | $0.00 (free tier) |
| Supabase | $0.00 (free tier) |
| **Total** | **$0.00** |

**Monthly Estimate (100 calls):**
- Within free tier limits: **$0.00**
- All services on free tier should handle 100 calls easily

---

### If Exceeding Free Tiers:

**Typical 5-minute call:**

| Service | Cost |
|---------|------|
| LiveKit | $0.25 (agent + participant minutes) |
| Deepgram STT | ~$0.002 (2 minutes of speech) |
| Cartesia TTS | ~$0.15 (1,500 characters) |
| LLM (GPT-4o-mini) | ~$0.02 (typical conversation) |
| Supabase | ~$0.00 (negligible) |
| **Total** | **~$0.42 per call** |

**Monthly Estimate (1,000 calls):**
- **~$420/month** if exceeding all free tiers

---

## 🎯 Cost Optimization Recommendations

### For Development/Testing:
1. **Use Free Tier Services** - All services offer generous free tiers
2. **Monitor Usage** - Keep track of credits/usage on each service
3. **Implement Cost Tracking** (Future Enhancement)

### For Production:
1. **Upgrade LiveKit Plan** if exceeding 1,000 agent minutes/month
2. **Monitor Deepgram Credits** - $200 one-time is generous but finite
3. **Cartesia Pro Plan** ($5/month) for 100,000 credits (more reliable)
4. **Consider Paid LLM** for better quality if needed
5. **Supabase Pro** only if exceeding free tier limits (unlikely for most use cases)

---

## 🔮 Future Enhancement: Cost Tracking

### Proposed Implementation:

**Backend (`main.py`):**
```python
# Track usage metrics
call_metrics = {
    "call_id": conversation_id,
    "duration_seconds": call_duration,
    "agent_minutes": agent_minutes,
    "participant_minutes": participant_minutes,
    "stt_seconds": total_stt_seconds,
    "tts_characters": total_tts_characters,
    "llm_tokens": {
        "input": total_input_tokens,
        "output": total_output_tokens
    }
}

# Calculate costs
costs = {
    "livekit": calculate_livekit_cost(agent_minutes, participant_minutes),
    "deepgram": calculate_deepgram_cost(stt_seconds),
    "cartesia": calculate_cartesia_cost(tts_characters),
    "llm": calculate_llm_cost(input_tokens, output_tokens),
    "supabase": calculate_supabase_cost(queries, storage),
    "total": sum_of_all_costs
}
```

**Frontend:**
- Display cost breakdown in `CallSummary` component
- Show total cost at end of call
- Include in conversation summary sent via data channel

**Status:** ⏳ Not yet implemented (optional bonus feature)

---

## 📝 Notes

- All cost estimates are approximate and may vary based on actual usage patterns
- Free tier limits may change - check current service documentation
- Costs assume typical conversation flows (booking appointments)
- Longer or more complex calls will incur higher costs
- Rate limiting on free services may cause retries, increasing costs slightly

---

## ⚠️ Current Limitation

**Cartesia Credits:**
- Account currently at -79 credits (service paused)
- **Recommendation:** Wait for monthly reset before running cost estimation tests
- Or upgrade to Pro plan ($5/month) for 100,000 credits

