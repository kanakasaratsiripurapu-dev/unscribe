# Deploy SubScout to Railway (Permanent Public URL)

Railway provides a permanent URL that won't change, perfect for sharing with friends!

## 🚀 Quick Deployment Steps

### 1. Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub (easiest option)
3. Get $5 free credit monthly

### 2. Deploy Backend
1. Click "New Project"
2. Select "Deploy from GitHub repo" (or upload your code)
3. Select your repository
4. Railway will detect it's a Python project
5. Add environment variables (see below)
6. Add PostgreSQL database service
7. Add Redis service

### 3. Deploy Frontend to Vercel (Recommended for Next.js)
1. Go to https://vercel.com
2. Sign up with GitHub
3. Import your repository
4. Set root directory to `frontend`
5. Add environment variables
6. Deploy!

### 4. Configure Environment Variables

**Backend (Railway):**
```
DATABASE_URL=<railway-provided-postgres-url>
REDIS_URL=<railway-provided-redis-url>
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=https://your-frontend-url.vercel.app/auth/callback
JWT_SECRET_KEY=generate-a-random-secret
OPENAI_API_KEY=your-openai-key
ENCRYPTION_KEY=generate-with-python
ENVIRONMENT=production
```

**Frontend (Vercel):**
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

### 5. Update Google Cloud Console
1. Add redirect URI: `https://your-frontend-url.vercel.app/auth/callback`
2. Save changes

## 🎯 Your Permanent URLs
- **Frontend:** `https://your-app.vercel.app` (or custom domain)
- **Backend:** `https://your-app.railway.app`

## 💡 Alternative: Full Deployment on Railway

You can also deploy both frontend and backend on Railway:
1. Create separate services for frontend and backend
2. Use Railway's static site hosting for frontend
3. Or use Railway's Dockerfile support

## 📝 Notes
- Railway free tier: $5 credit/month
- Vercel free tier: Unlimited for personal projects
- URLs are permanent and won't change
- Automatic deployments on git push

