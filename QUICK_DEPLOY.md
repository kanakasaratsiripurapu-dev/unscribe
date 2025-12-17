# 🚀 Quick Deploy to Get Permanent URL

## Step 1: Deploy Backend to Railway (5 minutes)

1. **Go to Railway:** https://railway.app
2. **Sign up** with GitHub (free)
3. **Click "New Project"** → "Deploy from GitHub repo"
4. **Connect your repository** (or create one and push your code)
5. **Railway will auto-detect** Python project

6. **Add PostgreSQL:**
   - Click "+ New" → "Database" → "Add PostgreSQL"
   - Railway will provide DATABASE_URL automatically

7. **Add Redis:**
   - Click "+ New" → "Database" → "Add Redis"
   - Railway will provide REDIS_URL automatically

8. **Set Environment Variables:**
   Click on your service → "Variables" tab → Add these:

```
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=https://your-app.railway.app/auth/callback
JWT_SECRET_KEY=generate-random-secret
OPENAI_API_KEY=your-openai-key
ENCRYPTION_KEY=generate-with-python-command-below
ENVIRONMENT=production
```

**Generate ENCRYPTION_KEY:**
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Generate JWT_SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

9. **Deploy!** Railway will build and deploy automatically
10. **Get your URL:** Click "Settings" → "Generate Domain" → Copy the URL

## Step 2: Deploy Frontend to Vercel (5 minutes)

1. **Go to Vercel:** https://vercel.com
2. **Sign up** with GitHub (free)
3. **Click "Add New"** → "Project"
4. **Import your repository**
5. **Configure:**
   - Root Directory: `frontend`
   - Framework Preset: Next.js (auto-detected)

6. **Environment Variables:**
   Add: `NEXT_PUBLIC_API_URL=https://your-backend.railway.app`

7. **Deploy!** Vercel will deploy automatically
8. **Get your URL:** You'll get `https://your-app.vercel.app`

## Step 3: Update Google Cloud Console

1. Go to: https://console.cloud.google.com/apis/credentials
2. Edit your OAuth client
3. Add redirect URI: `https://your-frontend.vercel.app/auth/callback`
4. Save

## Step 4: Update Railway Environment Variable

1. Go back to Railway
2. Update `GOOGLE_REDIRECT_URI` to: `https://your-frontend.vercel.app/auth/callback`
3. Redeploy

## ✅ Done!

Your permanent URLs:
- **Frontend:** https://your-app.vercel.app
- **Backend:** https://your-app.railway.app

Share the frontend URL with friends! 🎉
