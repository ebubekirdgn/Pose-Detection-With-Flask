from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np
import base64

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Hareket sayacı
counter = 0
stage = None

def calculate_angle(a, b, c):
    a = np.array(a)  
    b = np.array(b)  
    c = np.array(c)  

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

def generate_frames():
    cap = cv2.VideoCapture(0)

    global counter
    global stage

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Renk dönüşümü
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Pose algılama
        results = pose.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        try:
            landmarks = results.pose_landmarks.landmark

            # Landmarkları al (Sol kol için)
            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * frame.shape[1],
                             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * frame.shape[0]]
            left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * frame.shape[1],
                          landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * frame.shape[0]]
            left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x * frame.shape[1],
                           landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y * frame.shape[0]]

            # Açıları hesapla
            angle1 = calculate_angle(left_shoulder, left_elbow, left_wrist)

            # Açı kontrolü
            if angle1 > 160:
                stage = "down"
            if angle1 < 30 and stage == 'down':
                stage = "up"
                counter += 1  # Sayaç artır

            # Ekrana yazdırma
            cv2.putText(image, f'Counter: {counter}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)

            # Landmarkları çiz
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        except Exception as e:
            pass

        # Frame'i yeniden boyutlandır
        image = cv2.resize(image, (640, 480))  # 640x480 boyutuna küçült

        # Frame'i encode et
        _, buffer = cv2.imencode('.jpg', image)
        frame = base64.b64encode(buffer).decode('utf-8')
        yield frame

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_camera')
def start_camera():
    for frame in generate_frames():
        emit('camera_response', {'data': frame}, broadcast=True)

@socketio.on('finish')
def finish():
    global counter
    emit('finish_response', {'counter': counter}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
