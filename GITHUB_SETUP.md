# GitHub Repository Setup Guide

This guide helps you push the SuperBryn Voice Agent to GitHub repositories.

## 📋 Prerequisites

1. **Git installed** on your system
2. **GitHub account** with ability to create repositories
3. **All sensitive files excluded** (verified via `.gitignore`)

## 🔐 Security Checklist

Before pushing, ensure:

- [x] `.env` files are in `.gitignore`
- [x] `env.example` files exist (with placeholder values)
- [x] No API keys hardcoded in source code
- [x] No credentials in any files
- [x] Debug logs excluded (`.cursor/debug.log`)

**All sensitive files are already configured in `.gitignore` ✅**

---

## 🚀 Setup Instructions

### 1. Initialize Git Repository (if not already done)

**For Backend:**
```bash
cd backend
git init
git add .
git commit -m "Initial commit: SuperBryn Voice Agent Backend"
```

**For Frontend:**
```bash
cd frontend
git init
git add .
git commit -m "Initial commit: SuperBryn Voice Agent Frontend"
```

### 2. Create GitHub Repositories

1. Go to [GitHub](https://github.com)
2. Click "New repository"
3. Create two repositories:
   - `superbryn-voice-agent-backend` (or your preferred name)
   - `superbryn-voice-agent-frontend` (or your preferred name)
4. **Do NOT** initialize with README, .gitignore, or license (we already have these)

### 3. Push Backend Repository

```bash
cd backend
git remote add origin https://github.com/YOUR_USERNAME/superbryn-voice-agent-backend.git
git branch -M main
git push -u origin main
```

### 4. Push Frontend Repository

```bash
cd frontend
git remote add origin https://github.com/YOUR_USERNAME/superbryn-voice-agent-frontend.git
git branch -M main
git push -u origin main
```

---

## 📝 Repository Descriptions

### Backend Repository Description:
```
AI Voice Agent Backend - LiveKit Agent implementation for SuperBryn voice agent with appointment booking capabilities. Built with Python, Deepgram STT, Cartesia TTS, and Supabase.
```

### Frontend Repository Description:
```
AI Voice Agent Frontend - React web application for SuperBryn voice agent interface with real-time voice conversation and visual avatar.
```

---

## 🏷️ Recommended Topics/Tags

**Backend:**
- `livekit`
- `voice-agent`
- `python`
- `deepgram`
- `cartesia`
- `supabase`
- `appointment-booking`
- `ai-agent`
- `speech-to-text`
- `text-to-speech`

**Frontend:**
- `react`
- `livekit`
- `voice-agent`
- `real-time-communication`
- `web-app`
- `ai-interface`

---

## ⚠️ Important Notes for Public Repositories

### 1. Cartesia Credits Issue

**Add this notice in both repository READMEs:**

```markdown
⚠️ **IMPORTANT:** The demo account currently has -79 Cartesia credits (overage).
Agent will NOT speak until credits are restored. See `KNOWN_LIMITATIONS.md` for details.
```

### 2. Environment Variables

**Make sure:**
- ✅ `env.example` files are committed (with placeholder values)
- ✅ `.env` files are in `.gitignore` (not committed)
- ✅ All API keys use placeholders in example files

### 3. Sensitive Information

**Before pushing, verify:**
- No real API keys in code
- No credentials in comments
- No sensitive data in any files

### 4. Deployment Warning

**⚠️ IMPORTANT:** If deploying the application:
- **DO NOT deploy with Cartesia API key** - Any usage will consume credits and increase debt
- Remove `CARTESIA_API_KEY` from production environment or set it to empty
- The agent won't speak in production, but won't consume credits
- Wait for monthly credit reset before enabling TTS in production

---

## 📄 Files Included in Repository

### Backend:
- ✅ All Python source files (`main.py`, `tools.py`, `database.py`, etc.)
- ✅ `requirements.txt`
- ✅ `env.example` (no real keys)
- ✅ `README.md`
- ✅ Documentation files (`KNOWN_LIMITATIONS.md`, `DEVELOPMENT_ISSUES.md`, etc.)

**Excluded:**
- ❌ `.env` (contains real API keys)
- ❌ `venv/` (Python virtual environment)
- ❌ `__pycache__/` (Python cache)
- ❌ `.cursor/debug.log` (debug logs)

### Frontend:
- ✅ All React source files
- ✅ `package.json`, `package-lock.json`
- ✅ `public/` directory
- ✅ `src/` directory
- ✅ `README.md`

**Excluded:**
- ❌ `node_modules/` (dependencies)
- ❌ `build/` (build output)
- ❌ `.env.local` (environment variables)

---

## 🔍 Verification Steps

After pushing, verify:

1. **Check repository on GitHub:**
   - All source files are present
   - No `.env` files are visible
   - No `venv/` or `node_modules/` folders
   - Documentation files are included

2. **Clone and test (fresh machine):**
   ```bash
   git clone https://github.com/YOUR_USERNAME/superbryn-voice-agent-backend.git
   cd superbryn-voice-agent-backend
   cp env.example .env
   # Fill in API keys
   pip install -r requirements.txt
   python main.py dev
   ```

---

## 📚 Documentation Files Included

Both repositories include:

- `README.md` - Main setup and usage instructions
- `KNOWN_LIMITATIONS.md` - Known limitations and issues
- `DEVELOPMENT_ISSUES.md` - Issues encountered during development
- `COST_ESTIMATION.md` - Cost breakdown and estimation
- `REVIEWER_NOTES.md` - Important notes for reviewers

**All documentation is already created and ready to push ✅**

---

## 🎯 Next Steps

1. ✅ Create GitHub repositories
2. ✅ Push backend code
3. ✅ Push frontend code
4. ✅ Add repository descriptions and topics
5. ✅ Update README with deployed link (once deployed)

---

## 🚢 Deployment Links

After deployment, add to repository README:

**Backend:**
- Deployed agent URL (if applicable)

**Frontend:**
- Live demo link: `https://your-app.netlify.app` (or Vercel/other)

---

**Ready to push! 🚀**

