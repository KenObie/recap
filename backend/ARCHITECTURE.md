# Backend Architecture: Real-Time Sports Highlight Detection

## Overview
- Flask backend streams video frames to the frontend as MJPEG.
- Every N seconds, the backend extracts an audio chunk and enqueues it for highlight detection.
- A background thread runs Whisper on each chunk, checks for highlights, and extracts clips if needed.
- Server-Sent Events (SSE) are used to notify the frontend of new transcripts and highlights in real time.

## Architecture Diagram

```mermaid
graph TD
    A[Video File (MP4)] -->|Frames| B[Flask Backend]
    B -->|MJPEG| C[React Frontend]
    B -->|API: /highlight_clips| D[Highlights Grid]
    B -->|SSE: /notifications| E[Transcript Feed & Notifications]
    B -->|Audio Chunks| F[Whisper AI]
    F -->|Transcripts & Highlights| B
```

## Real-Time Flow
1. User opens the React app and requests the live video feed.
2. Flask streams video frames to the browser.
3. Every N seconds, Flask extracts an audio chunk and puts it in a queue.
4. A background thread processes the chunk with Whisper, checks for highlights, and extracts clips if needed.
5. SSE events are sent to the frontend with the latest transcript and highlight info.
6. The frontend updates the UI in real time. 