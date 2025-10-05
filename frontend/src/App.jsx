import { useState } from 'react';
import './App.css';
import { generatePlan, submitFeedback } from './api/pddl';
import StepFeedback from './components/StepFeedback';
import DatasetDisplay from './components/DatasetDisplay';

function App() {
  // State management
  const [prompt, setPrompt] = useState('');
  const [temperature, setTemperature] = useState(0.5);
  const [maxTokens, setMaxTokens] = useState(10000);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Plan data
  const [sessionId, setSessionId] = useState(null);
  const [planText, setPlanText] = useState('');
  const [steps, setSteps] = useState([]);
  const [metadata, setMetadata] = useState({});
  
  // Feedback data
  const [feedback, setFeedback] = useState({});
  const [dataset, setDataset] = useState(null);

  const handleGeneratePlan = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setDataset(null);
    
    if (prompt.length < 10) {
      setError('Prompt must be at least 10 characters long.');
      return;
    }
    
    try {
      setLoading(true);
      const result = await generatePlan(prompt, temperature, maxTokens);
      
      setSessionId(result.session_id);
      setPlanText(result.plan_text);
      setSteps(result.steps);
      setMetadata(result.metadata);
      setFeedback({});
      
      setSuccess(`Plan generated successfully! ${result.steps.length} steps parsed.`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedbackChange = (stepId, rating, reason) => {
    setFeedback(prev => ({
      ...prev,
      [stepId]: { rating, reason }
    }));
  };

  const validateFeedback = () => {
    const errors = [];
    
    // Check if all steps have feedback
    for (const step of steps) {
      if (!feedback[step.step_id]) {
        errors.push(`Step ${step.step_number} has no rating.`);
      } else if (feedback[step.step_id].rating === 'negative' && 
                 (!feedback[step.step_id].reason || feedback[step.step_id].reason.length < 10)) {
        errors.push(`Step ${step.step_number} needs a reason (at least 10 characters).`);
      }
    }
    
    return errors;
  };

  const handleSubmitFeedback = async () => {
    setError(null);
    setSuccess(null);
    
    const validationErrors = validateFeedback();
    if (validationErrors.length > 0) {
      setError(validationErrors.join(' '));
      return;
    }
    
    try {
      setLoading(true);
      
      // Format feedback for API
      const feedbackArray = steps.map(step => ({
        step_id: step.step_id,
        step_number: step.step_number,
        step_content: step.step_content,
        rating: feedback[step.step_id].rating,
        reason: feedback[step.step_id].reason || null
      }));
      
      const result = await submitFeedback(
        sessionId,
        prompt,
        planText,
        feedbackArray,
        metadata
      );
      
      setDataset(result.dataset);
      setSuccess(`Feedback submitted! Training dataset saved to: ${result.file_path}`);
      
      // Scroll to dataset display
      setTimeout(() => {
        document.getElementById('dataset-display')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getFeedbackProgress = () => {
    const total = steps.length;
    const completed = Object.keys(feedback).length;
    return { completed, total };
  };

  const progress = getFeedbackProgress();

  return (
    <div className="App">
      <header>
        <h1>🤖 PDDL RLHF System</h1>
        <p>Reinforcement Learning with Human Feedback for PDDL Planning</p>
      </header>

      <main>
        {/* Step 1: Input Form */}
        <section className="input-section">
          <h2>1️⃣ Enter Your Planning Problem</h2>
          
          <form onSubmit={handleGeneratePlan}>
            <div className="form-group">
              <label htmlFor="prompt">Planning Problem *</label>
              <textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe your planning problem here... (min 10 characters)"
                rows={6}
                disabled={loading}
                required
              />
              <small>{prompt.length} / 5000 characters</small>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="temperature">Temperature</label>
                <input
                  type="number"
                  id="temperature"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  min="0"
                  max="1"
                  step="0.1"
                  disabled={loading}
                />
                <small>0.0 = focused, 1.0 = creative</small>
              </div>

              <div className="form-group">
                <label htmlFor="maxTokens">Max Tokens</label>
                <input
                  type="number"
                  id="maxTokens"
                  value={maxTokens}
                  onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                  min="1000"
                  max="20000"
                  step="1000"
                  disabled={loading}
                />
                <small>1,000 - 20,000</small>
              </div>
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? '⏳ Generating Plan...' : '🚀 Generate Plan'}
            </button>
          </form>
        </section>

        {/* Notifications */}
        {error && (
          <div className="notification error">
            ❌ {error}
          </div>
        )}
        
        {success && (
          <div className="notification success">
            ✅ {success}
          </div>
        )}

        {/* Step 2: Display Plan & Collect Feedback */}
        {steps.length > 0 && (
          <section className="feedback-section">
            <h2>2️⃣ Review and Rate Each Step</h2>
            
            <div className="progress-bar">
              <div className="progress-info">
                <span>Progress: {progress.completed} / {progress.total} steps rated</span>
                <span>{Math.round((progress.completed / progress.total) * 100)}%</span>
              </div>
              <div className="progress-track">
                <div 
                  className="progress-fill" 
                  style={{ width: `${(progress.completed / progress.total) * 100}%` }}
                />
              </div>
            </div>

            <div className="steps-container">
              {steps.map(step => (
                <StepFeedback
                  key={step.step_id}
                  step={step}
                  feedback={feedback[step.step_id]}
                  onChange={handleFeedbackChange}
                />
              ))}
            </div>

            <div className="submit-container">
              <button
                onClick={handleSubmitFeedback}
                className="btn btn-success"
                disabled={loading || progress.completed !== progress.total}
              >
                {loading ? '⏳ Submitting...' : '✅ Submit Feedback & Generate Dataset'}
              </button>
              
              {progress.completed !== progress.total && (
                <p className="warning">
                  Please rate all {progress.total} steps before submitting.
                </p>
              )}
            </div>
          </section>
        )}

        {/* Step 3: Display Generated Dataset */}
        {dataset && (
          <DatasetDisplay dataset={dataset} />
        )}
      </main>

      <footer>
        <p>Built with React + FastAPI | Deploy to Vercel + Railway</p>
      </footer>
    </div>
  );
}

export default App;
