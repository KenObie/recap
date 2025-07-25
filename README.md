# RecapAI

A real-time highlight detection system that uses audio analysis to automatically identify and extract exciting moments from sports videos.

## Project Structure

```
recap/
├── backend/                    # Flask backend with highlight detection
│   ├── video_stream_server.py  # Main Flask server
│   ├── highlight_ai/           # AI processing modules
│   │   └── whisper_realtime_highlights.py
│   ├── training_data/          # Video files
│   └── requirements.txt        # Python dependencies
├── frontend/                   # React frontend
│   ├── package.json           # Node.js dependencies
│   ├── public/                # Static files
│   └── src/                   # React components
└── README.md                  # This file
```

## Features

- **Real-time highlight detection** using OpenAI Whisper audio analysis
- **Automatic video clipping** of detected highlights
- **Modern React frontend** with real-time updates
- **Server-Sent Events** for instant notifications
- **Video scrubbing** and live streaming modes
- **Responsive design** for all screen sizes

## Quick Start

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python video_stream_server.py
```

The backend will:
- Start on `http://localhost:5000`
- Automatically clear existing highlights
- Begin highlight detection in the background
- Serve video files and highlight clips

### 2. Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend will:
- Start on `http://localhost:3000`
- Connect to the backend automatically
- Show real-time highlight updates
- Display notifications when new clips are detected

## How It Works

1. **Audio Extraction**: The system extracts audio from the video file
2. **Chunk Processing**: Audio is split into 10-second chunks
3. **Whisper Transcription**: Each chunk is transcribed using OpenAI Whisper
4. **Keyword Detection**: The system searches for sports-related keywords
5. **Video Clipping**: When keywords are found, video clips are automatically extracted
6. **Real-time Updates**: The frontend receives instant notifications via Server-Sent Events

## Configuration

### Highlight Keywords
Edit `backend/highlight_ai/whisper_realtime_highlights.py` to modify the keywords:
```python
KEYWORDS = ["touchdown", "interception", "sack", "pass", "run", "fumble", "field goal", "kickoff", "amazing play, catch"]
```

### Processing Settings
- `CHUNK_LENGTH = 10` - Seconds per audio chunk
- `MAX_PROCESSING_TIME = 120` - Maximum processing time (2 minutes)
- `PRE_ROLL = 2` - Seconds before highlight to include
- `POST_ROLL = 2` - Seconds after highlight to include

## Demo Workflow

1. **Start both servers** (backend + frontend)
2. **Open browser** to `http://localhost:3000`
3. **Watch highlights appear** in real-time as they're detected
4. **Click on highlight clips** to play them individually
5. **Use video scrubber** to navigate the main video

## Dependencies

### Backend
- Python 3.8+
- Flask
- OpenAI Whisper
- PyDub
- OpenCV
- FFmpeg (system dependency)

### Frontend
- Node.js 16+
- React 18
- Axios

## Troubleshooting

### No highlights detected
- Check that FFmpeg is installed and in your PATH
- Verify the video file exists in `backend/training_data/`
- Check the terminal output for error messages

### Frontend not connecting
- Ensure the backend is running on port 5000
- Check browser console for connection errors
- Verify the proxy setting in `frontend/package.json`

### Performance issues
- Reduce `MAX_PROCESSING_TIME` for faster processing
- Use a smaller Whisper model (e.g., 'tiny' instead of 'base')
- Process shorter video segments #   r e c a p 
 
 