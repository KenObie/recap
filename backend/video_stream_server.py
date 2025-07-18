from flask import Flask, Response, send_file, jsonify, stream_with_context
import cv2
import time
import os
import glob
import subprocess
import sys
from datetime import datetime
import threading
import whisper
from pydub import AudioSegment
import queue
import re

app = Flask(__name__)

# Track the last clip count for notifications
last_clip_count = 0

VIDEO_PATH = 'training_data/super_bowl_51_demo.mp4'
AUDIO_PATH = 'training_data/super_bowl_51_demo.wav'
CHUNKS_DIR = 'audio_chunks'
HIGHLIGHT_CLIPS_DIR = 'whisper_highlight_clips'
CHUNK_LENGTH = 10  # seconds
KEYWORDS = [
    "touchdown", "interception", "sack", "fumble", "caught", "makes the catch", "field goal", "kickoff",
    "amazing play", "unbelievable", "incredible", "what a catch", "what a play",
    "big hit", "he's gone", "no way", "can't believe", "game changer", "huge gain",
    "breakaway", "down the sideline", "for the win", "walk-off", "clutch", "wow",
    "goes all the way", "pick six", "pick 6", "pick-six", "pick-6", "touchdown!", "strike", "intercepted!",
    "he's in!", "he's outta here", "are you kidding me", "miracle", "stunned", "explodes", "fires", "scores!,"
]

HYPE_PATTERNS = [
    r"what a [\w\s]+!", r"unbelievable", r"incredible", r"no way", r"wow", r"clutch", r"for the win",
    r"are you kidding", r"miracle", r"stunned", r"explodes", r"scores!", r"touchdown!", r"intercepted!",
    r"no sign yet"
]

# Add a thread-safe queue for SSE events
sse_event_queue = queue.Queue()

chunk_queue = queue.Queue()

def get_clip_count():
    clips_dir = HIGHLIGHT_CLIPS_DIR
    if not os.path.exists(clips_dir):
        return 0
    return len(glob.glob(os.path.join(clips_dir, 'highlight_*.mp4')))

# Update is_highlight to return (True, reason) or (False, None)
def is_highlight(text):
    text = text.lower()
    for kw in KEYWORDS:
        if kw in text:
            return True, kw
    for pat in HYPE_PATTERNS:
        match = re.search(pat, text)
        if match:
            return True, match.group(0)
    return False, None

# Update HighlightDetectorThread to send SSE events
def send_sse_event(text, is_highlight, reason):
    sse_event_queue.put({
        'text': text,
        'is_highlight': is_highlight,
        'reason': reason
    })

# Start the background highlight detector
class HighlightDetectorThread(threading.Thread):
    def __init__(self, chunk_queue):
        super().__init__(daemon=True)
        self.chunk_queue = chunk_queue
        self.model = whisper.load_model('medium.en')
        self.highlight_count = get_clip_count()

    def run(self):
        while True:
            item = self.chunk_queue.get()
            if item is None:
                break  # Allow for clean shutdown if needed
            chunk_start_sec, chunk_end_sec = item
            chunk_path = os.path.join(CHUNKS_DIR, f'chunk_{int(chunk_start_sec):04d}.wav')
            if extract_audio_chunk(chunk_start_sec, chunk_end_sec, chunk_path):
                safe_print(f'Processing audio chunk: {chunk_path}')
                result = self.model.transcribe(chunk_path)
                text = result.get('text', '')
                if isinstance(text, str):
                    text = text.lower()
                else:
                    text = str(text).lower()
                safe_print(f'   Transcript: "{text}"')
                highlight, reason = is_highlight(text)
                send_sse_event(text, highlight, reason)
                if highlight:
                    self.highlight_count += 1
                    safe_print(f'Highlight detected! Extracting clip #{self.highlight_count}...')
                    extract_highlight_clip(chunk_start_sec, chunk_end_sec, text, self.highlight_count)
            self.chunk_queue.task_done()

# Start the background highlight detector
highlight_detector = HighlightDetectorThread(chunk_queue)
highlight_detector.start()

# Safe print for Windows console
def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        print(*(str(arg).encode('ascii', errors='replace').decode('ascii') for arg in args), **kwargs)

def clear_existing_highlights():
    clips_dir = HIGHLIGHT_CLIPS_DIR
    if os.path.exists(clips_dir):
        safe_print("Clearing existing highlight clips...")
        for clip_file in glob.glob(os.path.join(clips_dir, 'highlight_*.mp4')):
            try:
                os.remove(clip_file)
                safe_print(f"Removed: {clip_file}")
            except Exception as e:
                safe_print(f"Error removing {clip_file}: {e}")
        safe_print("Existing highlights cleared.")
    else:
        safe_print("No existing highlights directory found.")

def extract_highlight_clip(start, end, text, clip_number):
    padding = 2  # seconds before and after
    clip_start = max(0, start - padding)
    clip_end = end + padding
    min_duration = 3  # seconds
    if clip_end - clip_start < min_duration:
        clip_end = clip_start + min_duration
    output_path = os.path.join(HIGHLIGHT_CLIPS_DIR, f'highlight_{clip_number:03d}.mp4')
    duration = clip_end - clip_start
    safe_print(f'Extracting highlight #{clip_number}: {clip_start:.1f}s to {clip_end:.1f}s (duration: {duration:.1f}s)')
    safe_print(f'   Text: "{text}"')
    cmd = [
        'ffmpeg', '-y', '-ss', str(clip_start), '-i', VIDEO_PATH,
        '-t', str(duration), '-c', 'copy', output_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        safe_print(f'Successfully extracted: {output_path}')
        return True
    except subprocess.CalledProcessError as e:
        safe_print(f'Error extracting clip: {e}')
        safe_print(f'ffmpeg stderr: {e.stderr.decode()}')
        return False

def extract_audio_chunk(start_sec, end_sec, chunk_path):
    cmd = [
        'ffmpeg', '-y', '-ss', str(start_sec), '-to', str(end_sec), '-i', VIDEO_PATH,
        '-ar', '16000', '-ac', '1', '-f', 'wav', chunk_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError as e:
        safe_print(f'Error extracting audio chunk: {e}')
        safe_print(f'ffmpeg stderr: {e.stderr.decode()}')
        return False

def clear_audio_chunks():
    if os.path.exists(CHUNKS_DIR):
        safe_print("Clearing existing audio chunks...")
        for chunk_file in glob.glob(os.path.join(CHUNKS_DIR, '*.wav')):
            try:
                os.remove(chunk_file)
                safe_print(f"Removed: {chunk_file}")
            except Exception as e:
                safe_print(f"Error removing {chunk_file}: {e}")
        safe_print("Existing audio chunks cleared.")
    else:
        safe_print("No existing audio_chunks directory found.")

@app.route('/video_feed')
def video_feed():
    def generate():
        cap = cv2.VideoCapture(VIDEO_PATH)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps < 10 or fps > 60:
            fps = 30
        frame_delay = 1 / fps
        start_time = time.time()
        frame_count = 0
        chunk_start_sec = 0
        chunk_end_sec = CHUNK_LENGTH
        video_duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
        while cap.isOpened():
            frame_start = time.time()
            ret, frame = cap.read()
            if not ret:
                break
            current_time_sec = frame_count / fps
            # Stream frame
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            frame_count += 1
            # Every CHUNK_LENGTH seconds, enqueue audio chunk for highlight detection
            if current_time_sec >= chunk_end_sec or (frame_count == 1 and current_time_sec == 0):
                chunk_queue.put((chunk_start_sec, chunk_end_sec))
                chunk_start_sec = chunk_end_sec
                chunk_end_sec = min(chunk_end_sec + CHUNK_LENGTH, video_duration)
            frame_end = time.time()
            elapsed = frame_end - frame_start
            sleep_time = max(0, frame_delay - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
        cap.release()
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/highlight_clips')
def get_highlight_clips():
    clips_dir = HIGHLIGHT_CLIPS_DIR
    if not os.path.exists(clips_dir):
        return jsonify([])
    clips = []
    for clip_file in sorted(glob.glob(os.path.join(clips_dir, 'highlight_*.mp4'))):
        clip_name = os.path.basename(clip_file)
        clips.append({
            'name': clip_name,
            'path': f'/highlight_clip/{clip_name}',
            'filename': clip_file
        })
    return jsonify(clips)

@app.route('/highlight_clip/<filename>')
def serve_highlight_clip(filename):
    clip_path = os.path.join(HIGHLIGHT_CLIPS_DIR, filename)
    if os.path.exists(clip_path):
        return send_file(clip_path, mimetype='video/mp4')
    else:
        return "Clip not found", 404

@app.route('/status')
def get_status():
    return jsonify({
        'clips_count': get_clip_count()
    })

@app.route('/notifications')
def notifications():
    def generate():
        global last_clip_count
        last_clip_count = get_clip_count()
        while True:
            # Send highlight notifications as before
            current_clip_count = get_clip_count()
            if current_clip_count > last_clip_count:
                new_clips = current_clip_count - last_clip_count
                last_clip_count = current_clip_count
                yield f"data: {new_clips} new clips detected\n\n"
            # Send transcript/highlight info from the SSE event queue
            try:
                event = sse_event_queue.get_nowait()
                import json
                yield f"data: {json.dumps({'transcript': event['text'], 'is_highlight': event['is_highlight'], 'reason': event['reason']})}\n\n"
            except queue.Empty:
                pass
            time.sleep(1)
    response = Response(stream_with_context(generate()), mimetype='text/event-stream')
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Cache-Control'] = 'no-cache'
    return response

@app.route('/')
def index():
    return "Backend API Server - Use React frontend at http://localhost:3000"

if __name__ == '__main__':
    safe_print("Starting Video Server with Real-Time Highlight Detection...")
    safe_print("Web interface will be available at: http://localhost:5000")
    clear_existing_highlights()
    clear_audio_chunks()
    app.run(host='0.0.0.0', port=5000, debug=False) 