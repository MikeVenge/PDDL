# 🔍 Deployment Verification Checklist

## ✅ Pre-Deployment Checks

### GitHub Repository
- [x] Latest code committed and pushed to GitHub
- [x] Recent commit: "Enhanced PDDL parser to properly extract action steps"
- [x] All files tracked in git

### Backend Configuration (Railway)
- [x] `railway.json` configured with correct start command
- [x] `nixpacks.toml` configured for Python 3.9
- [x] `requirements.txt` includes all dependencies
- [x] `main.py` has CORS configured for all origins (`"*"`)
- [x] Health check endpoint available at `/`
- [x] Environment variable: `FIREWORKS_API_KEY` needs to be set in Railway

### Frontend Configuration (Vercel)
- [x] `vercel.json` configured with Vite framework settings
- [x] Build command: `npm run build`
- [x] Output directory: `dist`
- [x] API URL configured via `VITE_API_URL` environment variable
- [x] Frontend uses dynamic API URL: `import.meta.env.VITE_API_URL || 'http://localhost:8000'`

## 🚀 Deployment Steps

### 1. Deploy Backend to Railway

1. **Push latest changes to GitHub:**
   ```bash
   git push origin main
   ```

2. **In Railway Dashboard:**
   - Your project should auto-deploy on push
   - Check deployment logs for any errors
   - Verify environment variables are set:
     - `FIREWORKS_API_KEY`: Your API key

3. **Test Backend Deployment:**
   ```bash
   # Replace with your Railway URL
   curl https://your-app.railway.app/
   ```

   Expected response:
   ```json
   {"status":"online","service":"PDDL RLHF API","version":"1.0.0"}
   ```

### 2. Deploy Frontend to Vercel

1. **In Vercel Dashboard:**
   - Project should auto-deploy on push
   - Verify environment variables are set:
     - `VITE_API_URL`: Your Railway backend URL (e.g., `https://your-app.railway.app`)

2. **Test Frontend Deployment:**
   - Visit your Vercel URL
   - Open browser console (F12)
   - Check for any API connection errors
   - Try generating a plan to test full integration

## 🔧 Common Deployment Issues & Fixes

### Railway Backend Issues

**Issue: Build fails**
- Check Python version in `nixpacks.toml` (should be python39)
- Verify all dependencies in `requirements.txt`
- Check Railway build logs for specific errors

**Issue: App crashes on start**
- Verify `FIREWORKS_API_KEY` is set correctly
- Check if PORT environment variable is being used
- Review application logs in Railway dashboard

**Issue: Health check fails**
- Ensure `/` endpoint returns proper JSON response
- Check `healthcheckTimeout` in `railway.json` (set to 100)

### Vercel Frontend Issues

**Issue: API calls fail**
- Verify `VITE_API_URL` is set to correct Railway URL
- Ensure Railway backend has CORS configured for Vercel domain
- Check browser console for CORS errors

**Issue: Build fails**
- Check Node version compatibility
- Verify all npm dependencies are installed
- Review Vercel build logs

## 📊 Post-Deployment Verification

### Backend API Tests

1. **Health Check:**
   ```bash
   curl https://your-backend.railway.app/
   ```

2. **API Documentation:**
   ```bash
   # Should redirect to docs
   curl https://your-backend.railway.app/docs
   ```

3. **Generate Plan Endpoint:**
   ```bash
   curl -X POST https://your-backend.railway.app/api/generate-plan \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Test prompt for PDDL planning",
       "temperature": 0.5,
       "max_tokens": 10000
     }'
   ```

### Frontend Tests

1. **Load Application:**
   - Visit: `https://your-app.vercel.app`
   - Should load without errors

2. **Test Plan Generation:**
   - Enter a test prompt
   - Click "Generate Plan"
   - Verify steps are parsed correctly (should show 5 steps for PDDL actions)

3. **Test Feedback Submission:**
   - Rate all steps
   - Submit feedback
   - Verify dataset is generated

## 📝 Environment Variables Summary

### Railway (Backend)
```
FIREWORKS_API_KEY=fw_3ZHFp8ZR5WeoadXcFcjEKY4z
```

### Vercel (Frontend)
```
VITE_API_URL=https://your-backend.railway.app
```

## 🎯 Success Criteria

- [ ] Backend responds to health checks
- [ ] Frontend loads without errors
- [ ] API calls from frontend to backend succeed
- [ ] PDDL plans are generated correctly
- [ ] Parser extracts 5 action steps from PDDL plans
- [ ] Feedback can be submitted and datasets generated
- [ ] No CORS errors in browser console

## 📞 Support Resources

- [Railway Documentation](https://docs.railway.app)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Production Build](https://vitejs.dev/guide/build.html)
