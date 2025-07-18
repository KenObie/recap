import React from 'react';

const StatusIndicator = ({ status }) => {
  const isRunning = status.running;
  
  return (
    <span className={`status-indicator ${isRunning ? 'status-running' : 'status-stopped'}`}>
      {isRunning ? 'Processing...' : 'Complete'}
    </span>
  );
};

export default StatusIndicator; 