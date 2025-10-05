# PDDL RLHF Backend

FastAPI backend for the PDDL RLHF system.

## Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your API key if different
```

3. **Run the server:**
```bash
python main.py
# or
uvicorn main:app --reload --port 8000
```

4. **Test the API:**
```bash
curl http://localhost:8000/
```

## API Endpoints

### `GET /`
Health check endpoint.

### `POST /api/generate-plan`
Generate a PDDL plan from a prompt.

**Request:**
```json
{
  "prompt": "Your planning problem...",
  "temperature": 0.5,
  "max_tokens": 10000
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "prompt": "...",
  "plan_text": "...",
  "steps": [...],
  "metadata": {...}
}
```

### `POST /api/submit-feedback`
Submit human feedback and generate training dataset.

**Request:**
```json
{
  "session_id": "uuid",
  "prompt": "...",
  "plan_text": "...",
  "feedback": [...],
  "metadata": {...}
}
```

**Response:**
```json
{
  "success": true,
  "dataset": {...},
  "file_path": "..."
}
```

### `GET /api/export-dataset/{session_id}?format=json`
Export a specific dataset.

## Deployment to Railway

1. Create a new project on Railway
2. Connect your GitHub repository
3. Set the root directory to `/backend`
4. Add environment variables:
   - `FIREWORKS_API_KEY`
5. Deploy!

Railway will automatically:
- Detect Python and install dependencies
- Set the `PORT` environment variable
- Run the start command from `railway.json`

## Environment Variables

- `FIREWORKS_API_KEY`: Your Fireworks AI API key (required)
- `PORT`: Server port (default: 8000, Railway sets this automatically)

## Directory Structure

```
backend/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
├── railway.json         # Railway deployment config
├── training_data/       # Stored feedback sessions
└── README.md           # This file
```

