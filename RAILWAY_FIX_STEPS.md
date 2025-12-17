# 🔧 Fix Railway Deployment - Step by Step

## The Problem
Railway is trying to build from the root directory which has both `backend/` and `frontend/` folders. It doesn't know which one to build.

## The Solution
Set Railway's root directory to `backend` so it knows to build the Python backend.

---

## Fix Steps (Do This in Railway Dashboard):

### Step 1: Open Your Service Settings
1. Go to: https://railway.app
2. Click on your project: **"accomplished-success"**
3. Click on the **"web"** service (the one that failed)

### Step 2: Set Root Directory
1. Click the **"Settings"** tab (top navigation)
2. Scroll down to find **"Source"** section
3. Look for **"Root Directory"** field
4. Click **"Edit"** or change the value
5. Enter: `backend`
6. Click **"Save"** or **"Update"**

### Step 3: Verify Build Settings
1. Still in **"Settings"** tab
2. Go to **"Build"** section
3. Verify:
   - **Build Command:** `pip install -r requirements.txt` (should auto-detect)
   - If not, set it manually
4. Go to **"Deploy"** section
5. Verify:
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - If not set, add it manually

### Step 4: Redeploy
1. Go to **"Deployments"** tab
2. Click **"Redeploy"** on the latest deployment
3. OR make a small change and push to GitHub to trigger new deployment
4. Wait for build to complete (2-3 minutes)

### Step 5: Verify Success
1. Check **"Build Logs"** - should show Python build
2. Check **"Deploy Logs"** - should show uvicorn starting
3. Your backend URL should work: `https://web-production-XXXXX.up.railway.app`

---

## What We've Added to Help:

✅ **nixpacks.toml** - Helps Railway detect Python project
✅ **backend/Procfile** - Defines start command
✅ **backend/runtime.txt** - Specifies Python version

But you still need to set **Root Directory** to `backend` in Railway settings!

---

## If Root Directory Option Doesn't Appear:

Railway might use "Service Root" or it might be in a different location:

1. Look for **"Config-as-code"** section in Settings
2. Or check **"Deploy"** section
3. Or Railway might auto-detect from `nixpacks.toml`

If you can't find it, try:
- Deleting the service and recreating it
- When creating, make sure to set root directory during setup

---

## After Railway Works:

Once Railway backend is working:
1. Get your backend URL
2. Deploy frontend to Vercel (set root directory to `frontend`)
3. Update OAuth redirect URIs
4. Test your app!

