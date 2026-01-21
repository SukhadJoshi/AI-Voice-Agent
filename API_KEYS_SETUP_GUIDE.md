# Complete API Keys Setup Guide

This guide walks you through getting API keys from each service step-by-step.

---

## 📋 Services Checklist

- [ ] LiveKit
- [ ] Deepgram  
- [ ] Cartesia
- [ ] Supabase
- [ ] OpenRouter (LLM)

---

## 1. LiveKit API Keys 🎙️

### Step 1.1: Get Server URL and API Keys

1. **Go to**: [cloud.livekit.io](https://cloud.livekit.io) and log in
2. **Select your project** (the one you created - "Voice Agent")
3. **Click on "Settings"** in the left sidebar
4. **Click on "API Keys"** tab
5. **You'll see**:
   - **Server URL**: Something like `wss://your-project.livekit.cloud` (at the top)
   - **API Keys section**: List of existing keys or option to create new

### Step 1.2: Create API Key (if needed)

1. **Click "Create API Key"** button
2. **Fill in**:
   - **Name**: `agent-key` (or any name)
   - **Permissions**: Select **"Admin"** (for full access)
3. **Click "Create"**
4. **IMPORTANT**: Copy both:
   - **API Key** (starts with something like `APK...`)
   - **API Secret** (starts with something like `xxx...`)
   - ⚠️ **Copy the secret NOW** - you can only see it once!

### Step 1.3: Add to .env

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APKxxxxxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxxxxx
```

---

## 2. Deepgram API Key 🎤

### Step 2.1: Get API Key

1. **Go to**: [deepgram.com](https://deepgram.com) and log in
2. **Click on your profile** (top right)
3. **Click "API Keys"** from dropdown
4. **You'll see**: Your API Key (starts with something like `abc123...`)
5. **Click "Copy"** button next to the key

### Alternative: From Dashboard

1. **Go to**: [console.deepgram.com](https://console.deepgram.com)
2. **Click "API Keys"** in left sidebar
3. **Copy** your API key

### Step 2.2: Add to .env

```env
DEEPGRAM_API_KEY=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

---

## 3. Cartesia API Key 🔊

### Step 3.1: Sign Up (if not done)

1. **Go to**: [cartesia.ai](https://cartesia.ai)
2. **Click "Sign Up"** (top right)
3. **Choose**: Free plan
4. **Complete signup** (verify email if needed)

### Step 3.2: Get API Key

1. **Log in** to [cartesia.ai](https://cartesia.ai)
2. **Go to Dashboard** (click your profile → Dashboard)
3. **Click on "API Keys"** or "Settings" → "API Keys"
4. **Click "Create API Key"** or "Generate Key"
5. **Copy the key** (starts with something like `cartesia_...`)

### Step 3.3: Add to .env

```env
CARTESIA_API_KEY=cartesia_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 4. Supabase API Keys 💾

### Step 4.1: Get Project URL and Anon Key

1. **Go to**: [supabase.com](https://supabase.com) and log in
2. **Select your project** (the one you created)
3. **Click "Settings"** (gear icon) in left sidebar
4. **Click "API"** under Project Settings
5. **You'll see two sections**:

   **Project URL:**
   - Copy the URL (looks like: `https://xxxxxxxxxxxxx.supabase.co`)

   **Project API keys:**
   - **`anon` public key**: This is what you need! (long string starting with `eyJ...`)
   - **`service_role` secret key**: Don't use this for now (only for server-side, never expose)

### Step 4.2: Add to .env

```env
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh4eHh4eHh4eHh4eHh4eHh4eCIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNjQxNzY5MjIwLCJleHAiOjE5NTczNDUyMjB9.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**⚠️ Note**: Your actual key will be much longer and different!

---

## 5. OpenRouter API Key (LLM) 🤖

### Step 5.1: Sign Up

1. **Go to**: [openrouter.ai](https://openrouter.ai)
2. **Click "Sign In"** (top right)
3. **Choose**: "Sign up" or "Create account"
4. **Complete signup** (can use Google/GitHub for quick signup)

### Step 5.2: Get API Key

1. **After logging in**, go to [openrouter.ai/keys](https://openrouter.ai/keys)
2. **You'll see**: "API Keys" page
3. **Click "Create Key"** button
4. **Optional**: Name it (e.g., "voice-agent")
5. **Copy the key** (starts with `sk-or-v1-...`)

### Step 5.3: Add to .env

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_PROVIDER=openrouter
```

**OR if using Together AI instead:**

```env
TOGETHER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_PROVIDER=together
```

---

## 📝 Complete .env File Template

Here's your complete `backend/.env` file structure:

```env
# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APKxxxxxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxxxxx

# Deepgram Configuration
DEEPGRAM_API_KEY=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz

# Cartesia Configuration
CARTESIA_API_KEY=cartesia_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# LLM Configuration (choose ONE)
# Option 1: OpenRouter (Recommended - Free tier)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_PROVIDER=openrouter

# Option 2: Together AI (Alternative)
# TOGETHER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# LLM_PROVIDER=together

# Option 3: OpenAI (Requires credit card)
# OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# LLM_PROVIDER=openai

# Option 4: Anthropic (Requires credit card)
# ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# LLM_PROVIDER=anthropic
```

---

## ✅ Verification Checklist

After adding all keys, verify:

- [ ] LiveKit URL starts with `wss://`
- [ ] LiveKit API Key starts with `APK`
- [ ] LiveKit API Secret is copied (long string)
- [ ] Deepgram API Key is copied
- [ ] Cartesia API Key starts with `cartesia_`
- [ ] Supabase URL starts with `https://` and ends with `.supabase.co`
- [ ] Supabase Key starts with `eyJ`
- [ ] LLM Provider key is set (OpenRouter recommended)
- [ ] `LLM_PROVIDER` matches your chosen service (`openrouter`, `together`, `openai`, or `anthropic`)

---

## 🔒 Security Tips

1. **Never commit `.env` file** to git (it's already in `.gitignore`)
2. **Don't share** your API keys publicly
3. **Use different keys** for development vs production
4. **Rotate keys** if accidentally exposed
5. **Keep service_role keys** (Supabase) secret - only use on backend

---

## 🆘 Troubleshooting

### "API Key not found" errors
- Check for extra spaces before/after the key
- Make sure you copied the entire key
- Verify you're using the right key (not the secret where key is needed)

### "Invalid API key" errors
- Re-copy the key from the service dashboard
- Check if key has expired (some services expire keys)
- Verify you're using the right format (no extra characters)

### "Permission denied" errors
- Check LiveKit API key has Admin permissions
- Verify Supabase anon key (not service_role) is used
- Make sure you're using the correct key type

---

## 📞 Quick Links

- **LiveKit**: [cloud.livekit.io/settings](https://cloud.livekit.io/settings)
- **Deepgram**: [console.deepgram.com](https://console.deepgram.com)
- **Cartesia**: [cartesia.ai/dashboard](https://cartesia.ai/dashboard)
- **Supabase**: [supabase.com/dashboard](https://supabase.com/dashboard) → Your Project → Settings → API
- **OpenRouter**: [openrouter.ai/keys](https://openrouter.ai/keys)

---

Good luck! Once all keys are in your `.env` file, you're ready to run the backend! 🚀

