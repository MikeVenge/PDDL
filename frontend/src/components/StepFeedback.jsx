import { useState, useEffect } from 'react';
import './StepFeedback.css';

function StepFeedback({ step, feedback, onChange }) {
  const [rating, setRating] = useState(feedback?.rating || null);
  const [reason, setReason] = useState(feedback?.reason || '');

  useEffect(() => {
    setRating(feedback?.rating || null);
    setReason(feedback?.reason || '');
  }, [feedback]);

  const handleRatingChange = (newRating) => {
    setRating(newRating);
    
    if (newRating === 'positive') {
      // Clear reason when switching to positive
      setReason('');
      onChange(step.step_id, newRating, null);
    } else {
      onChange(step.step_id, newRating, reason);
    }
  };

  const handleReasonChange = (e) => {
    const newReason = e.target.value;
    setReason(newReason);
    if (rating === 'negative') {
      onChange(step.step_id, rating, newReason);
    }
  };

  const isComplete = rating && (rating === 'positive' || (rating === 'negative' && reason.length >= 10));

  return (
    <div className={`step-card ${isComplete ? 'complete' : 'incomplete'}`}>
      <div className="step-header">
        <h3>
          {isComplete && <span className="check">✓</span>}
          Step {step.step_number}
          {step.section && <span className="section-tag">{step.section}</span>}
        </h3>
      </div>

      <div className="step-content">
        <pre>{step.step_content}</pre>
      </div>

      <div className="step-feedback">
        <div className="rating-buttons">
          <span className="label">Rate this step:</span>
          <button
            className={`btn-rating ${rating === 'positive' ? 'selected positive' : ''}`}
            onClick={() => handleRatingChange('positive')}
          >
            👍 Good
          </button>
          <button
            className={`btn-rating ${rating === 'negative' ? 'selected negative' : ''}`}
            onClick={() => handleRatingChange('negative')}
          >
            👎 Bad
          </button>
        </div>

        {rating === 'negative' && (
          <div className="reason-input">
            <label htmlFor={`reason-${step.step_id}`}>
              Why is this step bad? * (min 10 characters)
            </label>
            <textarea
              id={`reason-${step.step_id}`}
              value={reason}
              onChange={handleReasonChange}
              placeholder="Please explain what's wrong with this step..."
              rows={3}
              className={reason.length < 10 ? 'invalid' : 'valid'}
            />
            <small className={reason.length < 10 ? 'error' : ''}>
              {reason.length} / 10 characters minimum
            </small>
          </div>
        )}
      </div>
    </div>
  );
}

export default StepFeedback;

