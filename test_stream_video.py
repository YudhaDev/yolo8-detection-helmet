import cv2
import base64
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    return render_template('index.html')

def send_frame(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    socketio.emit('frame', jpg_as_text)

def video_stream():
    # Replace '0' with the video source (e.g., video file path or camera index)
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if ret:
            send_frame(frame)

if __name__ == '__main__':
    socketio.start_background_task(video_stream)
    socketio.run(app)
