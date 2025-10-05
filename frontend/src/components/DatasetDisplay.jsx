import { useState } from 'react';
import './DatasetDisplay.css';

function DatasetDisplay({ dataset }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(dataset, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(dataset, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rlhf_dataset_${dataset.session_id.slice(0, 8)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const metrics = dataset.aggregated_metrics;
  const scorePercentage = Math.round(metrics.overall_score * 100);

  return (
    <section id="dataset-display" className="dataset-section">
      <h2>3️⃣ Generated Training Dataset</h2>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-value">{metrics.total_steps}</div>
          <div className="metric-label">Total Steps</div>
        </div>
        <div className="metric-card positive">
          <div className="metric-value">{metrics.positive_ratings}</div>
          <div className="metric-label">👍 Positive</div>
        </div>
        <div className="metric-card negative">
          <div className="metric-value">{metrics.negative_ratings}</div>
          <div className="metric-label">👎 Negative</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{scorePercentage}%</div>
          <div className="metric-label">Overall Score</div>
        </div>
      </div>

      <div className="dataset-actions">
        <button onClick={handleCopy} className="btn btn-secondary">
          {copied ? '✅ Copied!' : '📋 Copy to Clipboard'}
        </button>
        <button onClick={handleDownload} className="btn btn-secondary">
          💾 Download JSON
        </button>
      </div>

      <div className="dataset-container">
        <div className="dataset-header">
          <h3>Dataset JSON</h3>
          <span className="session-id">Session: {dataset.session_id.slice(0, 8)}</span>
        </div>
        <pre className="dataset-json">
          {JSON.stringify(dataset, null, 2)}
        </pre>
      </div>

      <div className="feedback-summary">
        <h3>Feedback Summary</h3>
        <div className="feedback-list">
          {(dataset.human_feedback || dataset.feedback || []).map((item, index) => (
            <div key={index} className={`feedback-item ${item.rating}`}>
              <div className="feedback-header">
                <span className="step-number">Step {item.step_number}</span>
                <span className={`rating-badge ${item.rating}`}>
                  {item.rating === 'positive' ? '👍' : '👎'} {item.rating}
                </span>
              </div>
              {item.reason && (
                <div className="feedback-reason">
                  <strong>Reason:</strong> {item.reason}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default DatasetDisplay;

