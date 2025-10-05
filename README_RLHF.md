# PDDL RLHF System

A complete Reinforcement Learning with Human Feedback (RLHF) system for PDDL planning models.

## 🎯 Overview

This system allows you to:
1. Generate PDDL plans from natural language prompts
2. Collect human feedback (thumbs up/down) on each step
3. Generate training datasets in RLHF format
4. Export and use the data to improve the model

## 🏗️ Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  React Frontend │◄───────►│  FastAPI Backend│◄───────►│ Fireworks AI    │
│  (Vercel)       │   API   │  (Railway)      │   API   │ PDDL Model      │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  Training Data  │
                            │  (JSON files)   │
                            └─────────────────┘
```

## 📁 Project Structure

```
PDDL/
├── backend/                 # FastAPI backend
│   ├── main.py             # API server
│   ├── requirements.txt    # Python dependencies
│   ├── railway.json        # Railway config
│   ├── training_data/      # Generated datasets
│   └── README.md
├── frontend/               # React frontend
│   ├── src/
│   │   ├── api/           # API service layer
│   │   ├── components/    # React components
│   │   ├── App.jsx        # Main app
│   │   └── ...
│   ├── vercel.json        # Vercel config
│   ├── package.json
│   └── README.md
├── pddl_planner.py        # Original CLI tool
├── FUNCTIONAL_REQUIREMENTS.md
└── README_RLHF.md         # This file
```

## 🚀 Quick Start

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend will run on `http://localhost:8000`

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:5173`

## 📋 User Workflow

1. **Enter Problem**: User enters a planning problem in the text area
2. **Generate Plan**: System calls PDDL model and parses output into steps
3. **Review Steps**: Each step is displayed as a card
4. **Rate Steps**: User provides Y (good) or N (bad) for each step
5. **Add Reasons**: For negative ratings, user explains why
6. **Submit Feedback**: System validates all steps are rated
7. **View Dataset**: RLHF training dataset is generated and displayed
8. **Export**: User can download or copy the dataset

## 📊 Dataset Format

Following **MIT PDDL BlocksWorld standards** from [llm-as-pddl-formalizer](https://github.com/CassieHuang22/llm-as-pddl-formalizer):

```json
{
  "session_id": "uuid",
  "timestamp": "ISO-8601",
  "dataset_format": "MIT_PDDL_BlocksWorld_RLHF",
  "reference": "https://github.com/CassieHuang22/llm-as-pddl-formalizer",
  "original_prompt": "user's planning problem",
  "model_output": "full PDDL plan text",
  "pddl_structure": {
    "domain_definition": "(define (domain ...)",
    "problem_definition": "(define (problem ...)",
    "plan_sequence": "0: (action1 ...) 1: (action2 ...)",
    "validation": {
      "is_valid_structure": true,
      "has_domain": true,
      "has_problem": true,
      "has_actions": true,
      "has_predicates": true,
      "errors": []
    }
  },
  "model_metadata": {
    "model": "pddl-gpt-oss-model",
    "temperature": 0.5,
    "max_tokens": 10000,
    "prompt_tokens": 160,
    "completion_tokens": 2613,
    "total_tokens": 2773
  },
  "human_feedback": [
    {
      "step_id": "step-1",
      "step_number": 1,
      "step_content": "...",
      "rating": "positive|negative",
      "reason": "optional explanation",
      "feedback_quality": "detailed|basic"
    }
  ],
  "aggregated_metrics": {
    "total_steps": 12,
    "positive_ratings": 10,
    "negative_ratings": 2,
    "overall_score": 0.833,
    "pddl_validity_score": 1.0
  },
  "training_metadata": {
    "pipeline_type": "llm-as-formalizer",
    "evaluation_method": "human_feedback",
    "domain_type": "general_planning",
    "can_use_for_training": true
  }
}
```

See **[MIT_PDDL_INTEGRATION.md](MIT_PDDL_INTEGRATION.md)** for detailed documentation.

## 🌐 Deployment

### Backend → Railway

1. Create a Railway account
2. Create new project
3. Connect GitHub repo
4. Set root directory to `backend`
5. Add environment variable:
   - `FIREWORKS_API_KEY`: Your API key
6. Deploy!

Railway will automatically detect Python and use the config from `railway.json`.

**Your backend URL**: `https://your-app.railway.app`

### Frontend → Vercel

1. Create a Vercel account
2. Import GitHub repo
3. Set root directory to `frontend`
4. Add environment variable:
   - `VITE_API_URL`: Your Railway backend URL
5. Deploy!

Vercel will auto-detect Vite and deploy.

**Your frontend URL**: `https://your-app.vercel.app`

## 🔑 Environment Variables

### Backend (.env)
```
FIREWORKS_API_KEY=fw_xxxxx
PORT=8000  # Railway sets this automatically
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000  # Dev
VITE_API_URL=https://your-app.railway.app  # Prod
```

## 📡 API Endpoints

### `GET /`
Health check

### `POST /api/generate-plan`
Generate PDDL plan
- Body: `{ prompt, temperature, max_tokens }`
- Returns: `{ session_id, prompt, plan_text, steps[], metadata }`

### `POST /api/submit-feedback`
Submit feedback and generate dataset
- Body: `{ session_id, prompt, plan_text, feedback[], metadata }`
- Returns: `{ success, dataset, file_path }`

### `GET /api/export-dataset/{session_id}?format=json`
Export specific dataset

## ✨ Features

### Frontend
- ✅ Beautiful, responsive UI
- ✅ Real-time validation
- ✅ Progress tracking
- ✅ Error handling
- ✅ Copy to clipboard
- ✅ Download JSON
- ✅ Feedback summary

### Backend
- ✅ FastAPI with async support
- ✅ Intelligent step parsing
- ✅ RLHF dataset generation
- ✅ File persistence
- ✅ CORS support
- ✅ Input validation
- ✅ Error handling

## 🧪 Testing Locally

### 1. Start Backend
```bash
cd backend
python main.py
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Open Browser
Navigate to `http://localhost:5173`

### 4. Test Flow
1. Enter a planning problem
2. Click "Generate Plan"
3. Rate each step
4. Submit feedback
5. View generated dataset

## 📝 Example Use Case

**Input Prompt:**
```
I need to analyze the warrants issued by a US listed company. The company 
I am analyzing is Occidental Petroleum. I need you to plan the analysis 
where the company is first fully understood from financials, business, 
profitability, political headwind, and any other considerations, then 
evaluate the warrants in terms of its impact on share dilution and 
premium and expected returns.
```

**Output:**
- 12 parsed steps from domain definition to final analysis
- User rates each step
- RLHF dataset generated with feedback
- Dataset saved to `training_data/`

## 🔧 Customization

### Change Model
Edit `backend/main.py`:
```python
MODEL = "accounts/your-account/models/your-model"
```

### Change Parsing Logic
Edit the `parse_steps_from_plan()` function in `backend/main.py`

### Change UI Colors
Edit CSS files in `frontend/src/` and `frontend/src/components/`

## 🐛 Troubleshooting

### Backend won't start
- Check Python version (3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Check API key is set

### Frontend won't connect to backend
- Check `VITE_API_URL` in `.env`
- Check backend is running
- Check CORS settings in `backend/main.py`

### Steps not parsing correctly
- Check the `parse_steps_from_plan()` function
- The parser looks for numbered lists and action sequences
- Adjust regex patterns as needed

## 📚 Documentation

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)
- [Functional Requirements](FUNCTIONAL_REQUIREMENTS.md)
- [MIT PDDL Integration](MIT_PDDL_INTEGRATION.md) - BlocksWorld standards
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Quick Start](START_LOCAL.md)

## 🎓 Next Steps

1. **Collect More Data**: Use the system to collect feedback on various planning problems
2. **Train Model**: Use the generated datasets to fine-tune your PDDL model
3. **Iterate**: Deploy updated model and collect more feedback
4. **Analytics**: Build dashboard to visualize feedback trends

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open issues or PRs.

---

**Built with ❤️ using React, FastAPI, and Fireworks AI**

