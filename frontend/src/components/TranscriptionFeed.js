import React from 'react';
import './TranscriptionFeed.css';

const TranscriptionFeed = ({ transcript, isHighlight, reason }) => {
  return (
    <div className={`transcription-feed${isHighlight ? ' highlight' : ''}`}>
      <div className="transcript-text">
        <strong>Transcript:</strong> {transcript || <em>Waiting for transcription...</em>}
      </div>
      {isHighlight && reason && (
        <div className="highlight-reason">
          <strong>Highlight Triggered By:</strong> <span className="reason">{reason}</span>
        </div>
      )}
    </div>
  );
};

export default TranscriptionFeed; 