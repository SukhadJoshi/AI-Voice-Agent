# SuperBryn Voice Agent - Frontend

React web application for the AI voice agent interface.

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   Create a `.env` file in the frontend directory:
   ```
   REACT_APP_LIVEKIT_URL=wss://your-livekit-server.com
   REACT_APP_API_URL=http://localhost:8000
   ```

3. **Start development server:**
   ```bash
   npm start
   ```

   The app will open at `http://localhost:3000`

## Features

- **Voice Call Interface**: Connect to LiveKit room for voice conversation
- **Avatar Display**: Shows visual avatar (placeholder, integrate with Beyond Presence/Tavus)
- **Tool Call Visualization**: Displays tool calls in real-time
- **Call Summary**: Shows conversation summary at end of call
- **Mute/Unmute**: Control microphone

## Deployment

### Netlify

1. Build the app:
   ```bash
   npm run build
   ```

2. Deploy the `build` folder to Netlify

### Vercel

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy:
   ```bash
   vercel
   ```

## API Endpoint Required

You'll need to create a backend endpoint at `/api/token` that generates LiveKit access tokens. Example implementation:

```javascript
// Express.js example
app.post('/api/token', async (req, res) => {
  const { roomName, participantName } = req.body;
  const token = await generateLiveKitToken(roomName, participantName);
  res.json({ token, url: process.env.LIVEKIT_URL });
});
```

## Avatar Integration

To integrate with Beyond Presence or Tavus:

1. Install their SDK
2. Update `VoiceCall.js` to use their avatar streaming
3. Configure API keys in environment variables

## Known Limitations

⚠️ **IMPORTANT: Cartesia TTS Credits Issue**
- The demo account currently has **-79 Cartesia credits** (overage)
- Agent will **NOT speak** until credits are restored (monthly reset or upgrade)
- This is a billing issue, not a code issue - all code is functional
- See `../KNOWN_LIMITATIONS.md` for details

Other Limitations:
- Token generation endpoint needs to be implemented
- Avatar integration is placeholder (CSS animation, not full 3D/video avatar)
- Cost tracking UI not implemented (optional feature)

**For detailed information:**
- See `../KNOWN_LIMITATIONS.md` for full list of limitations
- See `../DEVELOPMENT_ISSUES.md` for issues encountered during development
- See `../COST_ESTIMATION.md` for cost breakdown information

