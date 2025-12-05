# 🚀 Deployment Guide: Render + Streamlit Cloud

## Prerequisites
- ✅ Code pushed to GitHub: `https://github.com/sourabhsp2004/social-media-app`
- ✅ GitHub account
- ✅ ImageKit account (for image/video uploads)

---

## Part 1: Deploy Backend to Render

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Click **"Get Started"** → Sign up with GitHub
3. Authorize Render to access your GitHub repositories

### Step 2: Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your repository: `sourabhsp2004/social-media-app`
3. Click **"Connect"**

### Step 3: Configure Service
Fill in the following settings:

| Field | Value |
|-------|-------|
| **Name** | `social-media-backend` (or any name you prefer) |
| **Region** | Choose closest to you |
| **Branch** | `main` |
| **Root Directory** | Leave blank |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.app:app --host 0.0.0.0 --port $PORT` |

### Step 4: Set Environment Variables
Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./test.db` |
| `IMAGEKIT_PRIVATE_KEY` | Your ImageKit private key |
| `IMAGEKIT_PUBLIC_KEY` | Your ImageKit public key |
| `IMAGEKIT_URL_ENDPOINT` | Your ImageKit URL endpoint |

> **Note:** Get your ImageKit credentials from [imagekit.io](https://imagekit.io) dashboard

### Step 5: Deploy
1. Select **"Free"** plan
2. Click **"Create Web Service"**
3. Wait for deployment (takes 2-5 minutes)
4. **📋 COPY THE URL** - You'll see something like:
   ```
   https://social-media-backend.onrender.com
   ```
   **Save this URL!** You'll need it for the frontend.

---

## Part 2: Deploy Frontend to Streamlit Cloud

### Step 1: Create Streamlit Cloud Account
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign in"** → **"Continue with GitHub"**
3. Authorize Streamlit

### Step 2: Deploy New App
1. Click **"New app"**
2. Fill in:
   - **Repository:** `sourabhsp2004/social-media-app`
   - **Branch:** `main`
   - **Main file path:** `frontend.py`
   - **App URL:** Choose a custom URL (e.g., `social-media-app`)

### Step 3: Configure Environment Variables
1. Click **"Advanced settings"**
2. In the **"Secrets"** section, add:
   ```toml
   API_URL = "https://social-media-backend.onrender.com"
   ```
   > ⚠️ **Replace with YOUR actual Render backend URL from Part 1, Step 5**

### Step 4: Deploy
1. Click **"Deploy!"**
2. Wait for deployment (takes 1-3 minutes)
3. Your app will be live at: `https://your-app-name.streamlit.app`

---

## ✅ Verification

### Test Your Deployment
1. Open your Streamlit app URL
2. Try to **Sign Up** with a new account
3. **Log In** with your credentials
4. Try **uploading** an image or video
5. Test **likes** and **comments**

### Common Issues & Fixes

**❌ "Connection error" on login**
- Check that `API_URL` in Streamlit secrets matches your Render URL exactly
- Ensure Render backend is running (check Render dashboard)

**❌ "Upload failed"**
- Verify ImageKit environment variables are set correctly in Render
- Check ImageKit dashboard for API key validity

**❌ Backend shows "Application failed to respond"**
- Check Render logs for errors
- Verify `requirements.txt` includes all dependencies

---

## 🎉 You're Done!

Your app is now live with:
- **Backend:** Running on Render (handles API, database, uploads)
- **Frontend:** Running on Streamlit Cloud (user interface)

### Next Steps
- Share your Streamlit app URL with friends!
- Monitor usage in Render and Streamlit dashboards
- Consider upgrading to paid plans for better performance

---

## 📊 Free Tier Limits

**Render Free Tier:**
- Spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- 750 hours/month

**Streamlit Cloud Free Tier:**
- 1 GB RAM
- Unlimited apps
- Community support
