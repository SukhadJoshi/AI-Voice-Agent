# Token Server Troubleshooting Guide

## Error: "Invalid response from token server: missing token or URL"

This error means the token server is responding, but it's not returning the expected token and URL.

### Common Causes & Fixes

#### 1. Missing LiveKit Credentials in Backend .env

**Problem**: The token server can't find LiveKit credentials.

**Fix**:
1. Check `backend/.env` file exists
2. Make sure it has these three lines (replace with your actual values):
   ```env
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=APKxxxxxxxxxxxxx
   LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxxxxx
   ```
3. **Restart the token server** after adding/updating .env:
   - Press `Ctrl+C` in the token server terminal
   - Run `python token_server.py` again

#### 2. Token Server Not Loading .env File

**Problem**: Token server isn't reading the .env file.

**Fix**: 
- Make sure `.env` is in the `backend/` folder (same folder as `token_server.py`)
- Make sure token server is running from the `backend/` folder:
  ```bash
  cd backend
  python token_server.py
  ```

#### 3. Wrong .env File Location

**Problem**: .env file is in wrong location.

**Fix**:
- `.env` should be in: `backend/.env`
- NOT in: `backend/venv/` or root folder

#### 4. Environment Variables Not Set

**Problem**: Values in .env are empty or wrong.

**Fix**:
1. Open `backend/.env` file
2. Check each line:
   - `LIVEKIT_URL` should start with `wss://`
   - `LIVEKIT_API_KEY` should start with `APK`
   - `LIVEKIT_API_SECRET` should be a long string
3. No spaces around the `=` sign
4. No quotes around values (unless they contain spaces)

### Verification Steps

#### Step 1: Check Token Server is Running

1. Open browser
2. Go to: `http://localhost:8000/docs`
3. You should see FastAPI documentation page
4. If not, token server isn't running

#### Step 2: Test Token Endpoint Manually

1. In browser, go to: `http://localhost:8000/docs`
2. Click on `/api/token` endpoint
3. Click "Try it out"
4. Enter:
   - `roomName`: `test-room`
   - `participantName`: `test-user`
5. Click "Execute"
6. Check response:
   - **Success**: Should return `token` and `url`
   - **Error**: Will show error message (likely missing credentials)

#### Step 3: Check Token Server Terminal

Look at the terminal where token server is running:
- **No errors**: Server is running fine
- **Error messages**: Will show what's wrong
- **"LiveKit credentials not configured"**: Means .env file is missing or credentials are missing

#### Step 4: Verify .env File

1. Open `backend/.env` file
2. Make sure these lines exist and have values:
   ```env
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=your-actual-api-key
   LIVEKIT_API_SECRET=your-actual-api-secret
   ```
3. Replace placeholder values with your actual LiveKit credentials

### Quick Test

Run this in a new terminal to test if token server can read credentials:

```bash
cd backend
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('LIVEKIT_URL:', os.getenv('LIVEKIT_URL')); print('LIVEKIT_API_KEY:', os.getenv('LIVEKIT_API_KEY')[:10] + '...' if os.getenv('LIVEKIT_API_KEY') else 'NOT SET')"
```

**Expected output**:
```
LIVEKIT_URL: wss://your-project.livekit.cloud
LIVEKIT_API_KEY: APKxxxxxx...
```

**If you see "NOT SET"**: Your .env file isn't being read or credentials are missing.

### Still Not Working?

1. **Check browser console** (F12 → Console tab) for detailed errors
2. **Check token server terminal** for error messages
3. **Verify all 3 services are running**:
   - Token server (port 8000)
   - LiveKit agent (main.py dev)
   - Frontend (port 3000)
4. **Restart everything**:
   - Stop all terminals (Ctrl+C)
   - Restart token server
   - Restart agent
   - Restart frontend

