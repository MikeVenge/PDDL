# 🚀 Quick Start - Local Development

This guide will get you up and running locally in 5 minutes.

## 📋 Prerequisites

- Python 3.8+ installed
- Node.js 16+ installed
- npm or yarn installed

---

## ⚡ Quick Start (2 Terminals)

### Terminal 1: Backend

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

**Backend will run on:** `http://localhost:8000`

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### Terminal 2: Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

**Frontend will run on:** `http://localhost:5173`

You should see:
```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

## 🌐 Open in Browser

1. Open `http://localhost:5173` in your browser
2. You should see the PDDL RLHF interface

---

## 🧪 Test the Full Flow

### 1. Enter a Planning Problem

Example prompt:
```
I need to plan a 7-day trip to Japan. I want to visit Tokyo, Kyoto, 
and Osaka. I have a budget of $3000 and prefer cultural experiences 
over shopping. Create a detailed itinerary.
```

### 2. Click "Generate Plan"

- Wait 10-30 seconds for the AI model to respond
- Steps will be automatically parsed and displayed

### 3. Rate Each Step

- Click 👍 (Good) or 👎 (Bad) for each step
- For 👎, provide a reason (minimum 10 characters)

### 4. Submit Feedback

- Once all steps are rated, click "Submit Feedback"
- Training dataset will be generated and displayed

### 5. View Dataset

- See the formatted JSON dataset
- Copy to clipboard or download as file
- Dataset is saved in `backend/training_data/`

---

## 🔍 Verify Everything Works

### Check Backend Health

```bash
curl http://localhost:8000/
```

Expected response:
```json
{"status":"online","service":"PDDL RLHF API","version":"1.0.0"}
```

### Check Training Data Directory

```bash
ls -la backend/training_data/
```

After submitting feedback, you should see files like:
```
rlhf_session_20241005_123456_abcd1234.json
```

### Check Browser Console

1. Open browser DevTools (F12)
2. Go to Console tab
3. Should see no errors
4. Network tab should show successful API calls

---

## 🛑 Stopping the Servers

### Stop Backend
- Press `Ctrl+C` in Terminal 1

### Stop Frontend
- Press `Ctrl+C` in Terminal 2

---

## 🔧 Configuration

### Backend Configuration

Edit `backend/main.py` to change:
- API_KEY: Your Fireworks AI API key
- MODEL: The PDDL model to use
- SYSTEM_PROMPT: The system prompt for the model

### Frontend Configuration

Create `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

Change the URL if your backend runs on a different port.

---

## 🐛 Common Issues

### Port Already in Use

**Backend (Port 8000):**
```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 $(lsof -ti:8000)
```

**Frontend (Port 5173):**
```bash
# Find process using port 5173
lsof -ti:5173

# Kill the process
kill -9 $(lsof -ti:5173)
```

### Module Not Found (Backend)

```bash
cd backend
pip install -r requirements.txt
```

### Dependencies Error (Frontend)

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### API Connection Refused

1. Make sure backend is running on port 8000
2. Check `VITE_API_URL` in frontend `.env`
3. Check CORS settings in backend `main.py`

### API Key Invalid

1. Check `FIREWORKS_API_KEY` is set correctly
2. Try the original key: `fw_3ZHFp8ZR5WeoadXcFcjEKY4z`
3. Or get a new key from Fireworks AI

---

## 📝 Development Tips

### Backend Hot Reload

Use `uvicorn` with `--reload` flag for auto-restart on code changes:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Frontend Hot Reload

Vite has hot module replacement (HMR) by default. Just save your files and changes appear instantly.

### View API Documentation

FastAPI provides interactive API docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Debug Mode

**Backend:**
Add print statements or use Python debugger:
```python
import pdb; pdb.set_trace()
```

**Frontend:**
Use browser DevTools and `console.log()`:
```javascript
console.log('Debug:', data);
```

---

## 📚 Next Steps

1. ✅ System is running locally
2. ✅ Generated your first training dataset
3. 📖 Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) to deploy to production
4. 📖 Read [README_RLHF.md](README_RLHF.md) for full documentation
5. 🎨 Customize the UI in `frontend/src/`
6. 🔧 Modify step parsing in `backend/main.py`

---

## 🎉 Success!

You now have a working RLHF system for PDDL planning!

**Enjoy collecting human feedback and improving your AI models! 🚀**

