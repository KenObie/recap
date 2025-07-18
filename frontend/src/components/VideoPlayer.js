import React from 'react';

const VideoPlayer = ({ src, type }) => {
  const handlePlay = () => {
    const video = document.querySelector(`#${type}-video`);
    if (video) video.play();
  };

  const handlePause = () => {
    const video = document.querySelector(`#${type}-video`);
    if (video) video.pause();
  };

  const handleRestart = () => {
    const video = document.querySelector(`#${type}-video`);
    if (video) video.currentTime = 0;
  };

  if (type === 'scrubber') {
    return (
      <div className="video-player">
        <video id="scrubber-video" controls autoPlay>
          <source src={src} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
        <div className="controls">
          <button className="btn" onClick={handlePlay}>Play</button>
          <button className="btn" onClick={handlePause}>Pause</button>
          <button className="btn" onClick={handleRestart}>Restart</button>
        </div>
        <div className="stream-link">
          <p>Direct video file: <a href={src} target="_blank" rel="noopener noreferrer">{src}</a></p>
        </div>
      </div>
    );
  }

  return (
    <div className="video-player">
      <img 
        id="stream-video"
        src={src} 
        alt="Live Stream"
        style={{ width: '100%', maxWidth: '800px', display: 'block', margin: '0 auto', borderRadius: '8px' }}
      />
      <div className="controls">
        <p><em>Simulated Live Stream</em></p>
      </div>
      <div className="stream-link">
        <p>Direct stream link: <a href={src} target="_blank" rel="noopener noreferrer">{src}</a></p>
      </div>
    </div>
  );
};

export default VideoPlayer; 