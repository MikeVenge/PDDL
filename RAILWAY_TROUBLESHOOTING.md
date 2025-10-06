# Railway Deployment Troubleshooting

## Issue: Railway Not Detecting Pushes

If Railway isn't automatically deploying when you push to GitHub, here's what to check:

### 1. Verify GitHub Integration

**In Railway Dashboard:**
1. Go to your project
2. Click **"Settings"** tab
3. Check **"Source"** section
4. Verify it shows your GitHub repository: `MikeVenge/PDDL`
5. If not connected, click **"Connect Repo"** and reconnect

### 2. Check Deployment Triggers

**In Railway Dashboard:**
1. Go to **"Settings"** → **"Triggers"**
2. Verify **"Auto Deploy"** is enabled
3. Check the branch is set to `main`

### 3. Manual Deployment

If auto-deploy isn't working, trigger manually:

**In Railway Dashboard:**
1. Go to **"Deployments"** tab
2. Click **"Deploy"** button (top right)
3. It will pull the latest code from GitHub

### 4. Verify GitHub Webhook

**In GitHub:**
1. Go to your repository: https://github.com/MikeVenge/PDDL
2. Click **"Settings"** → **"Webhooks"**
3. Look for a Railway webhook
4. If missing or showing errors, reconnect in Railway

### 5. Force Redeploy from Railway

You can also redeploy the current commit:

**In Railway Dashboard:**
1. Go to **"Deployments"** tab
2. Find the most recent deployment
3. Click the **"..."** menu
4. Select **"Redeploy"**

## Current Configuration Summary

### Files:
- `railway.json` (root) - Main Railway configuration
- `backend/railway.json` - Backend-specific settings
- `backend/nixpacks.toml` - Nixpacks build configuration
- `backend/requirements.txt` - Python dependencies
- `backend/runtime.txt` - Python 3.11
- `backend/Procfile` - Backup start command
- `.railwayignore` - Excludes frontend from build

### Key Settings Needed:

**Option A: Set Root Directory (Recommended)**
1. Railway Dashboard → Settings → **"Root Directory"**: `backend`
2. Railway will then use `backend/` as the project root
3. All paths in railway.json will be relative to `backend/`

**Option B: Use Current Setup (No Root Directory)**
1. Leave Root Directory empty
2. The `railway.json` commands handle `cd backend`
3. Build and start commands navigate to the right directory

## Expected Build Output

When it works, you should see:

```
[build]
✓ Detected Python application
✓ Installing dependencies from backend/requirements.txt
✓ Successfully installed:
  - fastapi==0.109.0
  - uvicorn==0.27.0
  - pydantic==2.5.3
  - requests==2.31.0
  - python-dotenv==1.0.0

[deploy]
✓ Starting: cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8080
✓ Uvicorn running on http://0.0.0.0:8080
✓ Healthcheck passed: GET / → 200 OK
```

## Quick Test After Deployment

```bash
# Replace with your Railway URL
curl https://your-app.railway.app/

# Expected response:
{"status":"online","service":"PDDL RLHF API","version":"1.0.0"}
```

## Still Having Issues?

### Check Railway Logs:
1. Railway Dashboard → Your service
2. Click **"View Logs"**
3. Look for error messages
4. Share them for specific debugging

### Alternative: Redeploy from Scratch

1. Delete the current Railway service
2. Create a new one
3. Connect to GitHub: `MikeVenge/PDDL`
4. Set **Root Directory**: `backend`
5. Add environment variable: `FIREWORKS_API_KEY`
6. Deploy!

## Latest Commit to Deploy

```
Commit: f1f55d2
Message: "Trigger Railway deployment"
Branch: main
```

Railway should be deploying this version.

