# 🚀 Deployment Guide

Complete guide for deploying the PDDL RLHF system to Vercel (frontend) and Railway (backend).

---

## 📋 Prerequisites

- GitHub account
- Vercel account (free tier is fine)
- Railway account (free tier is fine)
- Your code pushed to GitHub repository

---

## 🚂 Part 1: Deploy Backend to Railway

### Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository

### Step 2: Configure Project

1. **Set Root Directory:**
   - Go to Settings
   - Set "Root Directory" to `backend`

2. **Add Environment Variables:**
   - Click "Variables" tab
   - Add variable:
     - Name: `FIREWORKS_API_KEY`
     - Value: `fw_3ZHFp8ZR5WeoadXcFcjEKY4z` (or your API key)

3. **Deployment Settings:**
   - Railway will auto-detect Python
   - It will use the `railway.json` config
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3: Deploy

1. Click "Deploy"
2. Wait for build to complete (2-3 minutes)
3. Once deployed, you'll see a URL like: `https://pddl-rlhf-production.up.railway.app`

### Step 4: Test Backend

```bash
curl https://your-backend-url.railway.app/
```

You should see:
```json
{"status":"online","service":"PDDL RLHF API","version":"1.0.0"}
```

### Step 5: Copy Backend URL

**Important:** Copy your Railway backend URL. You'll need it for frontend deployment.

Example: `https://pddl-rlhf-production.up.railway.app`

---

## 🔷 Part 2: Deploy Frontend to Vercel

### Step 1: Create Vercel Project

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click "Add New..." → "Project"
4. Import your GitHub repository
5. Click "Import"

### Step 2: Configure Project

1. **Framework Preset:**
   - Vercel should auto-detect "Vite"

2. **Root Directory:**
   - Click "Edit" next to Root Directory
   - Set to `frontend`

3. **Build Settings:**
   - Build Command: `npm run build` (already set)
   - Output Directory: `dist` (already set)
   - Install Command: `npm install` (already set)

4. **Environment Variables:**
   - Click "Environment Variables"
   - Add variable:
     - Name: `VITE_API_URL`
     - Value: Your Railway backend URL (e.g., `https://your-app.railway.app`)
     - Select: Production, Preview, Development

### Step 3: Deploy

1. Click "Deploy"
2. Wait for build to complete (1-2 minutes)
3. Once deployed, you'll see a URL like: `https://your-app.vercel.app`

### Step 4: Test Frontend

1. Open your Vercel URL in a browser
2. You should see the PDDL RLHF interface
3. Try generating a plan to test the full flow

---

## ✅ Verification Checklist

### Backend (Railway)
- [ ] Backend URL is accessible
- [ ] Health check endpoint (`/`) returns JSON
- [ ] Environment variable `FIREWORKS_API_KEY` is set
- [ ] Logs show "Application startup complete"

### Frontend (Vercel)
- [ ] Frontend URL loads the interface
- [ ] Environment variable `VITE_API_URL` is set correctly
- [ ] No console errors in browser DevTools
- [ ] Can submit a prompt and generate a plan
- [ ] Can rate steps and submit feedback
- [ ] Dataset is generated and displayed

---

## 🔧 Troubleshooting

### Backend Issues

**Problem:** Railway build fails
- **Solution:** Check `requirements.txt` is correct
- **Solution:** Ensure `railway.json` exists in backend folder

**Problem:** API returns 500 error
- **Solution:** Check Railway logs for errors
- **Solution:** Verify `FIREWORKS_API_KEY` is set correctly

**Problem:** API is slow
- **Solution:** Normal for first request (cold start)
- **Solution:** Upgrade Railway plan for better performance

### Frontend Issues

**Problem:** Cannot connect to backend
- **Solution:** Check `VITE_API_URL` in Vercel environment variables
- **Solution:** Ensure Railway backend is running
- **Solution:** Check CORS settings in backend `main.py`

**Problem:** Build fails on Vercel
- **Solution:** Ensure root directory is set to `frontend`
- **Solution:** Check `package.json` has correct scripts
- **Solution:** Verify Node.js version compatibility

**Problem:** Environment variable not working
- **Solution:** Redeploy after adding environment variables
- **Solution:** Ensure variable name starts with `VITE_`

---

## 🔄 Updating Your Deployment

### Update Backend

1. Push changes to GitHub
2. Railway will auto-deploy (if enabled)
3. Or manually redeploy from Railway dashboard

### Update Frontend

1. Push changes to GitHub
2. Vercel will auto-deploy
3. Or manually redeploy from Vercel dashboard

### Update Environment Variables

**Railway:**
1. Go to project → Variables
2. Edit or add variables
3. Save (triggers automatic redeploy)

**Vercel:**
1. Go to project → Settings → Environment Variables
2. Edit or add variables
3. Save and redeploy

---

## 🌐 Custom Domains (Optional)

### Railway Custom Domain

1. Go to project → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed

### Vercel Custom Domain

1. Go to project → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Update `VITE_API_URL` to use Railway custom domain

---

## 📊 Monitoring

### Railway Monitoring

- View logs: Project → Deployments → Logs
- View metrics: Project → Metrics
- Set up alerts: Project → Settings → Notifications

### Vercel Monitoring

- View deployments: Project → Deployments
- View analytics: Project → Analytics
- View logs: Deployment → Function Logs

---

## 💰 Cost Estimation

### Railway Free Tier
- $5 credit per month
- ~500 hours of usage
- Perfect for development/testing
- Upgrade to Hobby ($5/month) for production

### Vercel Free Tier
- 100 GB bandwidth per month
- Unlimited deployments
- Perfect for most use cases
- Upgrade to Pro ($20/month) for team features

**Estimated Monthly Cost:**
- Development: $0 (free tiers)
- Production (light usage): $5-10
- Production (heavy usage): $20-50

---

## 🔐 Security Best Practices

1. **API Keys:**
   - Never commit API keys to GitHub
   - Use environment variables
   - Rotate keys periodically

2. **CORS:**
   - Update `allow_origins` in `backend/main.py` to only allow your Vercel domain
   - Remove wildcard `*` in production

3. **Rate Limiting:**
   - Consider adding rate limiting to API endpoints
   - Use Railway's built-in protections

4. **HTTPS:**
   - Both Railway and Vercel provide HTTPS by default
   - Always use HTTPS URLs

---

## 📞 Support

### Railway
- [Documentation](https://docs.railway.app)
- [Discord Community](https://discord.gg/railway)
- [Status Page](https://status.railway.app)

### Vercel
- [Documentation](https://vercel.com/docs)
- [Discord Community](https://vercel.com/discord)
- [Status Page](https://vercel-status.com)

---

## 🎉 Success!

Your PDDL RLHF system is now live! 

**Next steps:**
1. Share the URL with team members
2. Collect feedback on various planning problems
3. Download training datasets
4. Use datasets to improve your PDDL model
5. Iterate and improve!

---

**Need help?** Check the main README or open an issue on GitHub.

