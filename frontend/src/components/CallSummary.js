import React from 'react';
import './CallSummary.css';

const CallSummary = ({ summary, onClose }) => {
  return (
    <div className="summary-overlay">
      <div className="summary-modal">
        <div className="summary-header">
          <h2>Conversation Summary</h2>
          <button onClick={onClose} className="close-button">
            ×
          </button>
        </div>
        <div className="summary-content">
          <pre className="summary-text">{summary}</pre>
        </div>
        <div className="summary-footer">
          <button onClick={onClose} className="close-summary-button">
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default CallSummary;

