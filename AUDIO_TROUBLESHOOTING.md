# Audio Troubleshooting Guide - Can't Hear Agent Voice

## Quick Checks

### 1. Browser Volume & Permissions
- ✅ **Check browser volume**: Make sure your browser/system volume isn't muted
- ✅ **Check browser tab**: Click on the tab - some browsers mute tabs by default
- ✅ **Audio permissions**: Browser should have asked for audio permissions - make sure you allowed it

### 2. Check Backend Terminal (Agent)
Look at the terminal where you're running `python main.py dev`:

**What you should see:**
- Agent starting up
- No errors about Cartesia
- Messages about transcription/audio

**If you see errors:**
- `Cartesia API key not found` → Check `CARTESIA_API_KEY` in backend `.env`
- `Error generating TTS` → Cartesia API issue

### 3. Check Browser Console (F12)
Open browser DevTools (F12) → Console tab, click "Start Voice Call":

**What you should see:**
- `Connected to room`
- `Participant connected: agent` (or similar)
- `Audio track attached and playing`
- `Track subscribed: audio`

**If you see errors:**
- `Failed to subscribe to track` → Subscription issue
- `Error playing audio` → Browser audio issue
- No `Participant connected` → Agent not joining room

### 4. Check Audio Element
In browser DevTools (F12):
1. Go to **Elements** tab
2. Search for `<audio>` element
3. Check if it has a `src` or if tracks are attached

## Common Issues & Fixes

### Issue 1: Cartesia Not Working

**Symptom**: No errors, but no audio

**Fix**:
1. Check `CARTESIA_API_KEY` in `backend/.env`
2. Verify Cartesia API key is valid
3. Check Cartesia dashboard for credits remaining
4. Restart the agent after fixing

### Issue 2: Frontend Not Subscribing to Audio

**Symptom**: Connected but no audio tracks

**Fix**: 
- The code I just updated should fix this
- Make sure frontend is restarted (Ctrl+C, then `npm start` again)

### Issue 3: Browser Audio Muted

**Symptom**: Everything looks fine but no sound

**Fix**:
1. Check system volume
2. Check browser volume (right-click tab → Unmute site)
3. Check audio element isn't muted in DevTools
4. Try a different browser (Chrome recommended)

### Issue 4: Agent Not Joining Room

**Symptom**: Only you in the room, no agent participant

**Fix**:
1. Check LiveKit agent is running (`python main.py dev`)
2. Check for errors in agent terminal
3. Verify LiveKit credentials in backend `.env`
4. Make sure agent connected successfully

### Issue 5: Audio Track Not Attaching

**Symptom**: Participant connected but no audio

**Fix**:
1. Check browser console for track subscription messages
2. Manually check audio element in DevTools
3. Verify audio element has `autoPlay` attribute
4. Try refreshing the page

## Debugging Steps

### Step 1: Verify Agent is Speaking

In the backend terminal (where `python main.py dev` is running), you should see:
- Messages about transcription
- No TTS errors
- Agent responding to speech

### Step 2: Check Room Participants

1. Open browser console (F12)
2. Click "Start Voice Call"
3. Type in console:
   ```javascript
   room.remoteParticipants.forEach(p => console.log(p.identity, p.audioTracks.size))
   ```
4. Should see the agent participant with audio tracks

### Step 3: Check Audio Element

In browser console:
```javascript
const audio = document.querySelector('audio');
console.log('Audio element:', audio);
console.log('Playing:', !audio.paused);
console.log('Volume:', audio.volume);
console.log('Muted:', audio.muted);
console.log('Src:', audio.src);
```

**Expected:**
- `Playing: true`
- `Volume: 1`
- `Muted: false`
- `Src:` (should have a blob URL or MediaStream)

### Step 4: Test Cartesia API

Test if Cartesia is working:
```bash
cd backend
python -c "from livekit.plugins import cartesia; import os; from dotenv import load_dotenv; load_dotenv(); print('Cartesia key:', 'SET' if os.getenv('CARTESIA_API_KEY') else 'NOT SET')"
```

## Still Not Working?

### Try This:
1. **Stop everything** (Ctrl+C in all terminals)
2. **Check all .env files** have correct API keys
3. **Restart in order**:
   - Terminal 1: `python token_server.py`
   - Terminal 2: `python main.py dev` (wait for it to fully start)
   - Terminal 3: `npm start` (frontend)
4. **Open browser** to `http://localhost:3000`
5. **Check browser console** (F12) for errors
6. **Click "Start Voice Call"**
7. **Check all 3 terminals** for errors
8. **Say something** and wait for response

### Expected Behavior:
1. ✅ Connection successful
2. ✅ Agent participant appears
3. ✅ You hear greeting: "Hello! I'm your AI assistant..."
4. ✅ You speak
5. ✅ Agent responds with voice

### If Still No Audio:
- Check backend terminal for TTS errors
- Check browser console for audio errors
- Verify Cartesia API key is correct
- Try speaking and see if agent responds (even if you don't hear it)

Let me know what you see in the browser console and backend terminal!

