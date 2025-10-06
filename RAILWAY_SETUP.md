# Railway Setup Instructions

## ⚠️ CRITICAL: Root Directory Setting

Railway needs to be configured to use the `backend` directory as the root for the build.

### In Railway Dashboard:

1. Go to your project settings
2. Find **"Root Directory"** setting
3. Set it to: `backend`
4. Click **"Save"**
5. Trigger a **"Redeploy"**

## Why This Matters

Your repository has this structure:
```
PDDL/
├── backend/           <- This is where the FastAPI app lives
│   ├── main.py
│   ├── requirements.txt  <- Has FastAPI, uvicorn, pydantic
│   └── ...
├── frontend/
└── requirements.txt   <- Only has 'requests' (wrong file!)
```

**Problem:** Railway was finding the root `requirements.txt` (which only has `requests`) instead of `backend/requirements.txt` (which has FastAPI and uvicorn).

**Solution:** Set Root Directory = `backend` in Railway settings.

## Alternative: Delete Root requirements.txt

If you don't want to set the root directory, you can:

```bash
rm /Users/michaelkim/code/PDDL/requirements.txt
git add requirements.txt
git commit -m "Remove root requirements.txt to avoid Railway confusion"
git push
```

But setting the root directory is cleaner and more explicit.

## Verify After Deployment

Once Railway redeploys with `backend` as root directory:

```bash
curl https://your-app.railway.app/
```

Should return:
```json
{"status":"online","service":"PDDL RLHF API","version":"1.0.0"}
```

## Build Should Show:

```
Installing dependencies from backend/requirements.txt
Successfully installed:
  - fastapi==0.109.0
  - uvicorn==0.27.0
  - pydantic==2.5.3
  - requests==2.31.0
  - python-dotenv==1.0.0
```

Not just:
```
Successfully installed requests-2.31.0  <- WRONG!
```

