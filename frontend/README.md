# PDDL RLHF Frontend

React + Vite frontend for the PDDL RLHF system.

## Local Development

1. **Install dependencies:**
```bash
npm install
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Update VITE_API_URL if backend is running on a different port
```

3. **Run the development server:**
```bash
npm run dev
```

4. **Open in browser:**
```
http://localhost:5173
```

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Deployment to Vercel

### Method 1: Vercel CLI

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
vercel
```

3. Set environment variable in Vercel dashboard:
   - `VITE_API_URL`: Your Railway backend URL (e.g., `https://your-app.railway.app`)

### Method 2: Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your Git repository
4. Set root directory to `frontend`
5. Add environment variable:
   - Name: `VITE_API_URL`
   - Value: Your Railway backend URL
6. Deploy!

### Method 3: GitHub Integration

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Vercel will auto-detect Vite and deploy
4. Set environment variables in project settings

## Environment Variables

- `VITE_API_URL`: Backend API URL
  - Development: `http://localhost:8000`
  - Production: Your Railway backend URL (e.g., `https://pddl-rlhf.railway.app`)

## Features

- ✅ User-friendly interface for entering planning problems
- ✅ Real-time plan generation
- ✅ Step-by-step feedback collection (Y/N ratings)
- ✅ Reason input for negative feedback
- ✅ Progress tracking
- ✅ RLHF training dataset display
- ✅ Download dataset as JSON
- ✅ Copy to clipboard functionality
- ✅ Responsive design
- ✅ Error handling

## Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Custom CSS
- **HTTP Client**: Axios
- **Deployment**: Vercel

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── pddl.js           # API service
│   ├── components/
│   │   ├── StepFeedback.jsx  # Step feedback component
│   │   ├── StepFeedback.css
│   │   ├── DatasetDisplay.jsx # Dataset display component
│   │   └── DatasetDisplay.css
│   ├── App.jsx               # Main app component
│   ├── App.css
│   ├── main.jsx              # Entry point
│   └── index.css
├── public/
├── index.html
├── package.json
├── vite.config.js
├── vercel.json               # Vercel configuration
└── README.md
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
