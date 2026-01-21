# Production Deployment - Cartesia API Key Removal

## 🎯 Goal
Prevent Cartesia API key from consuming credits in production deployment.

---

## Option 1: Remove from Production Environment Variables (Recommended)

### For Netlify:

1. **Go to Netlify Dashboard**
   - https://app.netlify.com
   - Select your site

2. **Navigate to Environment Variables**
   - Click **Site settings**
   - Click **Environment variables** (left sidebar)
   - Or go to: **Site settings** → **Build & deploy** → **Environment**

3. **Remove Cartesia API Key**
   - Find `CARTESIA_API_KEY` in the list
   - Click the **3 dots** (⋮) next to it
   - Click **Edit** or **Delete**
   - If editing, clear the value and save
   - If deleting, confirm deletion

4. **Redeploy**
   - Go to **Deploys** tab
   - Click **Trigger deploy** → **Clear cache and deploy site**

---

### For Vercel:

1. **Go to Vercel Dashboard**
   - https://vercel.com/dashboard
   - Select your project

2. **Navigate to Environment Variables**
   - Click **Settings** tab
   - Click **Environment Variables** (left sidebar)

3. **Remove Cartesia API Key**
   - Find `CARTESIA_API_KEY` in the list
   - Click **Edit** (pencil icon) or **Delete** (trash icon)
   - If editing, clear the value completely
   - Save changes

4. **Redeploy**
   - Go to **Deployments** tab
   - Click **⋮** (3 dots) on latest deployment
   - Click **Redeploy**
   - Or push a new commit

---

### For Heroku:

**Via Dashboard:**
1. Go to https://dashboard.heroku.com
2. Select your app
3. Click **Settings** tab
4. Click **Reveal Config Vars**
5. Find `CARTESIA_API_KEY`
6. Click **Delete** (X icon)
7. Click **Save** (if visible)

**Via CLI:**
```bash
heroku config:unset CARTESIA_API_KEY
```

Then redeploy:
```bash
git push heroku main
```

---

### For Railway:

1. **Go to Railway Dashboard**
   - https://railway.app/dashboard
   - Select your project

2. **Navigate to Variables**
   - Click your service
   - Click **Variables** tab

3. **Remove Cartesia API Key**
   - Find `CARTESIA_API_KEY`
   - Click **Delete** (trash icon)
   - Confirm deletion

4. **Redeploy**
   - Service will auto-redeploy on variable change
   - Or manually trigger redeploy

---

### For Render:

1. **Go to Render Dashboard**
   - https://dashboard.render.com
   - Select your service

2. **Navigate to Environment**
   - Click **Environment** tab (left sidebar)

3. **Remove Cartesia API Key**
   - Find `CARTESIA_API_KEY` in the list
   - Click **Delete** (trash icon)
   - Confirm deletion

4. **Redeploy**
   - Click **Manual Deploy** → **Deploy latest commit**
   - Or push a new commit

---

### For DigitalOcean App Platform:

1. **Go to DigitalOcean Dashboard**
   - https://cloud.digitalocean.com/apps
   - Select your app

2. **Navigate to Settings**
   - Click **Settings** tab
   - Scroll to **App-Level Environment Variables**

3. **Remove Cartesia API Key**
   - Find `CARTESIA_API_KEY`
   - Click **Edit** or **Delete**
   - Save changes

4. **Redeploy**
   - Go to **Actions** tab
   - Click **Create Deploy**
   - Or trigger via new commit

---

## Option 2: Code-Level Check (Optional - More Robust)

If you want to handle missing Cartesia API key gracefully in code:

### Step 1: Modify `backend/main.py`

**Find this line (around line 242-243):**
```python
# Initialize TTS (Cartesia)
tts = cartesia.TTS()
```

**Replace with:**
```python
# Initialize TTS (Cartesia) - Only if API key exists
cartesia_api_key = os.getenv("CARTESIA_API_KEY", "").strip()
if cartesia_api_key:
    tts = cartesia.TTS()
    print("[DEBUG] Cartesia TTS initialized with API key")
else:
    tts = None
    print("[WARNING] Cartesia TTS not initialized - CARTESIA_API_KEY not set")
```

### Step 2: Modify `say_text` function

**Find the `say_text` function (around line 295):**

**Add check at the beginning:**
```python
async def say_text(text: str):
    """Synthesize text to speech and publish to room"""
    if not text.strip():
        return
    
    # Skip TTS if Cartesia API key is not set
    if tts is None:
        print(f"[WARNING] TTS disabled - CARTESIA_API_KEY not set. Would have said: '{text[:50]}...'")
        return
    
    # ... rest of the function stays the same
```

---

## Option 3: Set Empty Value in Production

Instead of deleting, you can set it to empty:

**For any platform:**
1. Go to environment variables
2. Find `CARTESIA_API_KEY`
3. Edit it
4. Set value to empty string: `""`
5. Save and redeploy

**This has the same effect as removing it.**

---

## ✅ Verification After Removal

### Check 1: Verify TTS is Disabled
1. Start a voice call in production
2. Speak something
3. **Expected:** Agent processes your speech (STT works)
4. **Expected:** Agent responds (LLM works)
5. **Expected:** Agent does NOT speak (TTS disabled)
6. Check backend logs - should see warning about TTS being disabled

### Check 2: Check Cartesia Dashboard
1. Go to https://console.cartesia.ai
2. Check your usage/credits
3. **Expected:** No new usage after deployment
4. Credits should stay at -79 (or current value)

### Check 3: Check Backend Logs
Look for messages like:
- `[WARNING] Cartesia TTS not initialized - CARTESIA_API_KEY not set`
- `[WARNING] TTS disabled - CARTESIA_API_KEY not set`

---

## 📝 What Happens After Removal

✅ **Works:**
- Speech-to-Text (STT) - Uses Deepgram
- LLM responses - Uses OpenRouter/other LLM
- Database operations - Uses Supabase
- Tool calling - All 7 tools work
- Conversation flow - Full functionality

❌ **Won't Work:**
- Agent voice output (TTS disabled)
- Agent greeting won't be spoken
- Agent responses won't be spoken

**User Experience:**
- Users can speak and be understood
- Agent processes and responds (in logs)
- Users see tool calls in UI
- Users get call summary
- **But:** Users won't hear agent's voice

---

## 🔄 Re-Enabling TTS Later

When you want to re-enable TTS (after credits are restored):

1. **Wait for Cartesia monthly credit reset**
   - Check your Cartesia dashboard
   - Credits should reset automatically

2. **Add Cartesia API Key back**
   - Go to your deployment platform
   - Add `CARTESIA_API_KEY` environment variable
   - Set value to your Cartesia API key
   - Save and redeploy

3. **Or use Option 2 (Code Check)**
   - If you implemented the code-level check
   - Just add the API key - code will automatically enable TTS

---

## 🎯 Recommendation

**Best Approach:**
1. **Use Option 1** (Remove from environment variables) - Simplest
2. **For production:** Remove `CARTESIA_API_KEY` completely
3. **For local development:** Keep it in your local `.env` file
4. **Re-enable later:** Add it back after credits are restored

**This way:**
- ✅ Production won't consume credits
- ✅ Local development still works
- ✅ Easy to re-enable later

---

## 📋 Quick Checklist

- [ ] Identify your deployment platform (Netlify/Vercel/Heroku/etc.)
- [ ] Remove `CARTESIA_API_KEY` from production environment variables
- [ ] Redeploy your application
- [ ] Test to verify TTS is disabled (agent won't speak)
- [ ] Verify no new Cartesia credits are consumed
- [ ] Document the TTS disabled status in your README

---

**Done! 🎉** Your production deployment won't consume Cartesia credits anymore.

