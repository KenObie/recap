import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import VideoPlayer from './components/VideoPlayer';
import HighlightGrid from './components/HighlightGrid';
import StatusIndicator from './components/StatusIndicator';
import TranscriptionFeed from './components/TranscriptionFeed';

const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

function App() {
  const [highlights, setHighlights] = useState([]);
  const [status, setStatus] = useState({ running: false, clips_count: 0 });
  const [notifications, setNotifications] = useState([]);
  const [transcript, setTranscript] = useState('');
  const [isHighlight, setIsHighlight] = useState(false);
  const [reason, setReason] = useState('');
  const eventSourceRef = useRef(null);

  // Load highlights from server
  const loadHighlights = async () => {
    try {
      const response = await fetch('/highlight_clips');
      const clips = await response.json();
      setHighlights(clips);
    } catch (error) {
      console.error('Error loading highlights:', error);
    }
  };

  // Load status from server
  const loadStatus = async () => {
    try {
      const response = await fetch('/status');
      const statusData = await response.json();
      setStatus(statusData);
    } catch (error) {
      console.error('Error loading status:', error);
    }
  };

  // Show notification
  const showNotification = (message) => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 3000);
  };

  // Start SSE connection for real-time updates
  const startEventSource = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    eventSourceRef.current = new window.EventSource(`${backendUrl}/notifications`);
    eventSourceRef.current.onmessage = (event) => {
      const data = event.data;
      if (data.includes('new clips detected')) {
        const clipCount = parseInt(data.split(' ')[0]);
        showNotification(`${clipCount} new highlight${clipCount > 1 ? 's' : ''} detected!`);
        loadHighlights(); // Refresh highlights
        loadStatus(); // Refresh status
      } else {
        // Try to parse as JSON for transcript/highlight info
        try {
          const parsed = JSON.parse(data);
          if ('transcript' in parsed) {
            setTranscript(parsed.transcript);
            setIsHighlight(parsed.is_highlight);
            setReason(parsed.reason || '');
          }
        } catch (e) {
          // Not a JSON event, ignore
        }
      }
    };
    eventSourceRef.current.onerror = (event) => {
      setTimeout(() => {
        if (eventSourceRef.current?.readyState === window.EventSource.CLOSED) {
          startEventSource();
        }
      }, 5000);
    };
  };

  // Initialize on component mount
  useEffect(() => {
    loadHighlights();
    loadStatus();
    startEventSource();
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  // Fallback: update status every 10 seconds
  useEffect(() => {
    const interval = setInterval(loadStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <div className="container">
        <h1>Video Player with Real-Time Highlights</h1>
        {/* Transcription Feed Section */}
        <TranscriptionFeed transcript={transcript} isHighlight={isHighlight} reason={reason} />
        {/* Video Player Section */}
        <div className="video-container">
          <VideoPlayer 
            src="/video_feed" 
            type="stream"
          />
        </div>
        {/* Highlights Section */}
        <div className="highlights-container">
          <div className="highlights-header">
            <h2>Detected Highlights</h2>
            <StatusIndicator status={status} />
            <button className="refresh-btn" onClick={loadHighlights}>
              Refresh Highlights
            </button>
          </div>
          <HighlightGrid highlights={highlights} />
        </div>
      </div>
      {/* Notifications */}
      <div className="notifications">
        {notifications.map(notification => (
          <div key={notification.id} className="notification">
            {notification.message}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App; 