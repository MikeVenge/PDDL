# 🚀 Quick Reference Guide

## 📍 Important URLs

### Local Development
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### After Deployment
- **Frontend**: https://your-app.vercel.app
- **Backend**: https://your-app.railway.app

---

## 🎯 Quick Commands

### Start Backend
```bash
cd backend
python main.py
```

### Start Frontend
```bash
cd frontend
npm run dev
```

### Test Backend Health
```bash
curl http://localhost:8000/
```

### Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Install Frontend Dependencies
```bash
cd frontend
npm install
```

---

## 📂 Key Files

| File | Purpose |
|------|---------|
| `backend/main.py` | Backend API server |
| `frontend/src/App.jsx` | Main frontend component |
| `frontend/src/api/pddl.js` | API service layer |
| `backend/training_data/` | Generated datasets |
| `DEPLOYMENT_GUIDE.md` | How to deploy |
| `START_LOCAL.md` | How to run locally |
| `PROJECT_SUMMARY.md` | Complete overview |

---

## 🔑 Environment Variables

### Backend
```bash
FIREWORKS_API_KEY=fw_3ZHFp8ZR5WeoadXcFcjEKY4z
PORT=8000
```

### Frontend
```bash
VITE_API_URL=http://localhost:8000  # Local
VITE_API_URL=https://your-backend.railway.app  # Production
```

---

## 📡 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Health check |
| POST | `/api/generate-plan` | Generate PDDL plan |
| POST | `/api/submit-feedback` | Submit feedback |
| GET | `/api/export-dataset/{id}` | Export dataset |

---

## 🎨 Tech Stack Summary

**Frontend:**
- React 19.1.1
- Vite 7.1.7
- Axios 1.12.2
- Custom CSS

**Backend:**
- FastAPI 0.109.0
- Uvicorn 0.27.0
- Pydantic 2.5.3
- Requests 2.31.0

**Deployment:**
- Vercel (Frontend)
- Railway (Backend)

---

## 📊 User Workflow

```
1. Enter planning problem
2. Click "Generate Plan"
3. Review generated steps
4. Rate each step (👍 or 👎)
5. Provide reasons for 👎
6. Submit feedback
7. View generated dataset
8. Download/Copy dataset
```

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Port in use | `kill -9 $(lsof -ti:8000)` or `lsof -ti:5173` |
| Backend not connecting | Check CORS, verify backend is running |
| Module not found | `pip install -r requirements.txt` |
| npm errors | `rm -rf node_modules && npm install` |

---

## 📝 Documentation Index

1. **START_LOCAL.md** - Run locally in 5 minutes
2. **DEPLOYMENT_GUIDE.md** - Deploy to production
3. **README_RLHF.md** - Main documentation
4. **FUNCTIONAL_REQUIREMENTS.md** - Detailed requirements
5. **MIT_PDDL_INTEGRATION.md** - MIT BlocksWorld standards
6. **PROJECT_SUMMARY.md** - Complete project overview
7. **backend/README.md** - Backend specifics
8. **frontend/README.md** - Frontend specifics
9. **QUICK_REFERENCE.md** - This file

---

## ✅ Pre-Deployment Checklist

### Backend
- [ ] `requirements.txt` is complete
- [ ] `railway.json` is configured
- [ ] Environment variables documented
- [ ] API tested locally

### Frontend
- [ ] `package.json` is correct
- [ ] `vercel.json` is configured
- [ ] Environment variables documented
- [ ] Build tested locally (`npm run build`)

### Both
- [ ] Code pushed to GitHub
- [ ] README files complete
- [ ] No secrets in code
- [ ] CORS configured correctly

---

## 🎯 Next Steps

1. ✅ **Test Locally**
   - Follow `START_LOCAL.md`
   - Verify full workflow
   
2. ✅ **Deploy Backend**
   - Follow Railway section in `DEPLOYMENT_GUIDE.md`
   - Copy backend URL
   
3. ✅ **Deploy Frontend**
   - Follow Vercel section in `DEPLOYMENT_GUIDE.md`
   - Set `VITE_API_URL` environment variable
   
4. ✅ **Test Production**
   - Open Vercel URL
   - Generate a plan
   - Submit feedback
   - Verify dataset is created

5. ✅ **Use the System**
   - Collect feedback on various prompts
   - Download training datasets
   - Use datasets to improve model

---

## 📞 Quick Help

**Backend not responding?**
- Check logs: Railway dashboard or `python main.py` output
- Verify API key is set
- Test health endpoint

**Frontend can't connect?**
- Check `VITE_API_URL` environment variable
- Verify backend is running and accessible
- Check browser console for errors

**Steps not parsing?**
- Check backend logs for parsing errors
- Verify model output format
- May need to adjust regex in `parse_steps_from_plan()`

---

## 🎉 You're All Set!

Everything is ready to:
- ✅ Run locally
- ✅ Deploy to production
- ✅ Collect human feedback
- ✅ Generate training datasets
- ✅ Improve your PDDL models

**Happy coding! 🚀**

