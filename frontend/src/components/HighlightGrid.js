import React from 'react';

const HighlightGrid = ({ highlights }) => {
  if (highlights.length === 0) {
    return (
      <div className="highlights-grid">
        <div className="no-highlights">
          No highlights detected yet. Processing in background...
        </div>
      </div>
    );
  }

  return (
    <div className="highlights-grid">
      {highlights.map((clip, index) => (
        <div key={clip.name} className="highlight-item">
          <h4>{clip.name}</h4>
          <video controls>
            <source src={clip.path} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>
      ))}
    </div>
  );
};

export default HighlightGrid; 