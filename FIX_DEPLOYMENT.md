# 🔧 Fix Deployment Issues - Railway & Vercel

## Issues Found:
1. **Railway:** Nixpacks can't detect build plan because root has both `backend/` and `frontend/`
2. **Vercel:** 404 error - root directory not configured

## Solutions Applied:
✅ Added `nixpacks.toml` for Railway build configuration
✅ Added `backend/Procfile` for Railway start command
✅ Added `backend/runtime.txt` for Python version
✅ Updated `railway.json` configuration

---

## Railway Configuration Steps:

### 1. Update Service Settings in Railway:
1. Go to Railway dashboard
2. Click on your **"web"** service
3. Go to **"Settings"** tab
4. Scroll to **"Build"** section
5. Set:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Save changes

**OR** use the config files (already pushed to GitHub):
- Railway will detect `nixpacks.toml` and `backend/Procfile`
- Make sure root directory is set to `backend` in Railway settings

### 2. Redeploy:
1. Go to **"Deployments"** tab
2. Click **"Redeploy"** or push a new commit
3. Railway should now build correctly from `backend/` directory

---

## Vercel Configuration Steps:

### 1. Update Project Settings in Vercel:
1. Go to Vercel dashboard
2. Click on your project
3. Go to **"Settings"** → **"General"**
4. Scroll to **"Root Directory"**
5. Click **"Edit"**
6. Set to: `frontend`
7. Click **"Save"**

### 2. Redeploy:
1. Go to **"Deployments"** tab
2. Click **"Redeploy"** on the latest deployment
3. Vercel will now build from `frontend/` directory

---

## Alternative: Delete and Recreate Services

If the above doesn't work:

### Railway:
1. Delete the current service
2. Create new service
3. **IMPORTANT:** Set root directory to `backend` before deploying
4. Add PostgreSQL and Redis
5. Add environment variables
6. Deploy

### Vercel:
1. Delete the current project
2. Import again from GitHub
3. **IMPORTANT:** Set root directory to `frontend` during import
4. Add environment variable: `NEXT_PUBLIC_API_URL`
5. Deploy

---

## Quick Fix Commands (If using Railway CLI):

```bash
# Set root directory
railway variables set RAILWAY_SERVICE_ROOT_DIRECTORY=backend

# Redeploy
railway up
```

---

## Verification:

After fixes:
- ✅ Railway should build successfully
- ✅ Backend API should be accessible
- ✅ Vercel should deploy successfully  
- ✅ Frontend should load without 404

