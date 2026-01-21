# Free Tier Guide - Complete Breakdown

This guide clarifies which services have **truly free tiers** (no credit card required) vs those that require payment or credit card verification.

## ✅ Services with Free Tiers (No Credit Card Required)

### 1. **LiveKit Cloud** ✅ FREE TIER
- **Free Plan**: "Build" plan - $0/month
- **What's Included**:
  - 1,000 agent session minutes/month
  - 10,000 participant minutes/month
  - 1 free phone number
  - Agent deployment
  - Observability tools
- **No Credit Card Required**: Yes ✅
- **Limitations**: Once you exceed monthly limits, you need to upgrade to paid plan (~$50/month)
- **Good For**: Development, testing, and small-scale usage

### 2. **Deepgram** ✅ FREE TIER
- **Free Credits**: $200 in free credits when you sign up
- **What's Included**:
  - Speech-to-Text (STT)
  - Text-to-Speech (TTS)
  - Voice Agent API
  - All public models
- **No Credit Card Required**: Yes ✅
- **Limitations**: 
  - One-time credit (not recurring monthly)
  - Concurrency limits
  - After $200 is used, pay-as-you-go pricing (~$0.0077/min)
- **Good For**: ~25,000+ minutes of STT (based on pricing)

### 3. **Cartesia** ✅ FREE TIER
- **Free Plan**: $0/month
- **What's Included**:
  - 20,000 model credits
  - Core TTS models
  - Basic agent features
- **No Credit Card Required**: Yes ✅
- **Limitations**:
  - Lower concurrency
  - No voice cloning
  - Basic features only
- **Good For**: Basic TTS needs, development

### 4. **Supabase** ✅ FREE TIER
- **Free Plan**: "Free" tier - $0/month
- **What's Included**:
  - 500 MB database storage
  - 2 GB bandwidth
  - 50,000 monthly active users
  - PostgreSQL database
  - Real-time subscriptions
- **No Credit Card Required**: Yes ✅
- **Limitations**:
  - Storage and bandwidth limits
  - After limits, need to upgrade
- **Good For**: Development and small-scale apps (perfect for this project!)

### 5. **Together AI** ✅ FREE CREDITS
- **Free Credits**: Yes, often offers free credits for new users
- **No Credit Card Required**: May vary (check current offers)
- **What's Included**: Access to various open-source LLMs
- **Good For**: LLM needs without OpenAI/Anthropic

### 6. **OpenRouter** ✅ FREE CREDITS
- **Free Credits**: Yes, often offers free credits
- **No Credit Card Required**: May vary
- **What's Included**: Access to multiple LLM providers
- **Good For**: LLM needs with multiple model options

## ⚠️ Services Requiring Credit Card / Payment

### 1. **OpenAI API** ❌ REQUIRES CREDIT CARD
- **Free Credits**: $5 free credits when you first sign up
- **Credit Card Required**: Yes ⚠️ (for API access)
- **Note**: Free credits expire after 3 months
- **After Free Credits**: Pay-as-you-go (~$0.006/min for Whisper, $15/1M chars for TTS)
- **Alternative**: Use Together AI or OpenRouter instead

### 2. **Anthropic (Claude API)** ❌ REQUIRES CREDIT CARD
- **Free Tier**: Limited (mainly web/mobile app access)
- **API Access**: Requires credit card
- **Alternative**: Use Together AI or OpenRouter instead

### 3. **Beyond Presence / Tavus** ⚠️ UNKNOWN
- **Check their current free tier offerings**
- **Recommendation**: Use placeholder avatar for now, integrate later if needed

## 🎯 Recommended Free-Only Stack

For **100% free** (no credit card), use this combination:

| Component | Service | Free Tier Details |
|-----------|---------|-------------------|
| **Voice Infrastructure** | LiveKit | 1,000 agent min/month, 10K participant min/month |
| **Speech-to-Text** | Deepgram | $200 free credits (one-time) |
| **Text-to-Speech** | Cartesia | 20,000 credits/month |
| **Database** | Supabase | 500 MB storage, 2 GB bandwidth |
| **LLM** | Together AI or OpenRouter | Free credits available |

## 💰 Cost Estimation (Staying Within Free Tiers)

### Scenario: 1 hour of conversation per day

**Monthly Usage:**
- LiveKit: ~30 hours = 1,800 agent minutes ✅ (under 1,000 limit - might need to monitor)
- Deepgram: ~1,800 minutes = ~$14 ✅ (within $200 credits - will last ~14 months)
- Cartesia: ~1,800 minutes = depends on characters ✅ (likely within 20K credits)
- Supabase: Database calls ✅ (well within free tier)
- LLM: API calls ✅ (depends on provider, but Together/OpenRouter usually generous)

**Note**: For more usage, you'd need paid plans, but for development and demo purposes, free tiers are sufficient.

## 📋 Setup Checklist (Free Tier Only)

- [ ] LiveKit: Sign up for free "Build" plan (no credit card)
- [ ] Deepgram: Sign up for $200 free credits (no credit card)
- [ ] Cartesia: Sign up for free plan (no credit card)
- [ ] Supabase: Sign up for free tier (no credit card)
- [ ] Together AI or OpenRouter: Sign up for free credits (check if credit card needed)
- [ ] **AVOID**: OpenAI API and Anthropic API (require credit cards)

## ⚠️ Important Notes

1. **LiveKit Limits**: Monitor your usage - 1,000 agent minutes/month means ~33 minutes/day
2. **Deepgram Credits**: One-time only, not monthly - use wisely
3. **Cartesia Credits**: Monthly reset, but monitor usage
4. **Supabase**: Very generous for this use case
5. **LLM Alternatives**: Together AI or OpenRouter are better free options than OpenAI/Anthropic

## 🔄 Alternative: Fully Self-Hosted (100% Free Forever)

If you want to avoid all cloud services:

- **STT**: Use Whisper (OpenAI's open-source model) - self-hosted
- **TTS**: Use Coqui TTS or similar - self-hosted  
- **LLM**: Use Llama 2/3 or Mistral - self-hosted
- **Voice Infrastructure**: Self-host LiveKit server
- **Database**: Self-host PostgreSQL

This requires more setup but is completely free.

## 📞 Recommendation

**For this assignment, use the recommended free stack above** - it will:
- ✅ Work for development and demo
- ✅ Require no credit cards (except possibly LLM provider)
- ✅ Be sufficient for testing and submission
- ✅ Allow you to demonstrate all required features

If you need more usage, you can always upgrade later.

