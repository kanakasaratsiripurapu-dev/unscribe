# 🔧 Fix Vercel Deployment - Step by Step

## The Problem
Vercel is getting a 404 error because it's trying to build from the root directory instead of the `frontend/` directory where your Next.js app is located.

## The Solution
Set Vercel's root directory to `frontend` so it knows to build the Next.js app.

---

## Fix Steps (Do This in Vercel Dashboard):

### Step 1: Open Your Project Settings
1. Go to: https://vercel.com
2. Click on your project (should be `unscribe` or similar)
3. Click **"Settings"** tab (top navigation)

### Step 2: Set Root Directory
1. In Settings, click **"General"** (left sidebar)
2. Scroll down to **"Root Directory"** section
3. Click **"Edit"** button
4. Enter: `frontend`
5. Click **"Save"**

### Step 3: Verify Build Settings
1. Still in **"General"** settings
2. Verify **"Framework Preset"** is set to **"Next.js"**
3. Verify **"Build Command"** is `npm run build` (should be auto-detected)
4. Verify **"Output Directory"** is `.next` (should be auto-detected)

### Step 4: Add Environment Variable
1. Click **"Environment Variables"** in left sidebar
2. Click **"Add New"**
3. Add:
   - **Key:** `NEXT_PUBLIC_API_URL`
   - **Value:** Your Railway backend URL (e.g., `https://web-production-XXXXX.up.railway.app`)
   - **Environment:** Select all (Production, Preview, Development)
4. Click **"Save"**

### Step 5: Redeploy
1. Go to **"Deployments"** tab (top navigation)
2. Click the **"..."** menu on the latest deployment
3. Click **"Redeploy"**
4. OR push a new commit to GitHub to trigger deployment
5. Wait for deployment (2-3 minutes)

### Step 6: Verify Success
1. Check deployment logs - should show Next.js build
2. Your frontend URL should work: `https://unscribe.vercel.app` (or your custom domain)
3. No more 404 errors!

---

## What to Expect:

✅ Build logs showing: `npm install` and `npm run build`
✅ Next.js compilation success
✅ Deployment success message
✅ Frontend accessible at your Vercel URL

---

## After Vercel Works:

1. ✅ Copy your Vercel frontend URL
2. ✅ Update Railway `GOOGLE_REDIRECT_URI` with Vercel URL
3. ✅ Update Google Cloud Console redirect URI
4. ✅ Test OAuth login
5. ✅ Your app should be fully functional!

---

## Troubleshooting:

**Still getting 404?**
- Make sure root directory is exactly `frontend` (lowercase, no trailing slash)
- Check that `frontend/package.json` exists
- Verify Next.js files are in `frontend/` directory

**Build fails?**
- Check build logs for specific errors
- Make sure all dependencies are in `frontend/package.json`
- Verify Node.js version (should be auto-detected)

