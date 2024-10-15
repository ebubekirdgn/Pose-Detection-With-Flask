import cv2
import mediapipe as mp
import numpy as np
from exercises.exercise_strategy import ExerciseStrategy
class SquatStrategy(ExerciseStrategy):

    def __init__(self):
        self.counter = 0
        self.is_exercising = False
        self.cap = None
        self.stage = None  # 'up' veya 'down' durumu
    
    def calculate_angle(self, a, b, c):
        """Üç nokta arasındaki açıyı hesapla."""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        angle = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(angle * 180.0 / np.pi)
        if angle > 180.0:
            angle = 360 - angle
        return angle

    def perform_exercise(self):
        # MediaPipe bileşenlerini ayarla
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
        self.is_exercising = True
        self.cap = cv2.VideoCapture(0)
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Kare hızını artır
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        # Parlaklık ve kontrast ayarları
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 150)
        self.cap.set(cv2.CAP_PROP_CONTRAST, 50)
        self.cap.set(cv2.CAP_PROP_EXPOSURE, -5)
        
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    break

                # Görüntüyü ayna etkisi için ters çevir
                frame = cv2.flip(frame, 1)

                # BGR'den RGB'ye çevir
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(image_rgb)

                # Landmark'ları gizle ve sadece belirli noktaları çiz
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark

                    # Landmarkları al
                    left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x * frame.shape[1],
                                landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y * frame.shape[0]]
                    left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x * frame.shape[1],
                                 landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y * frame.shape[0]]
                    left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x * frame.shape[1],
                                   landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y * frame.shape[0]]

                    right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x * frame.shape[1],
                                 landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y * frame.shape[0]]
                    right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x * frame.shape[1],
                                   landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y * frame.shape[0]]
                    right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x * frame.shape[1],
                                    landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y * frame.shape[0]]

                    # Açıları hesapla
                    angle1 = self.calculate_angle(left_hip, left_knee, left_ankle)  # Sol bacak açısı
                    angle2 = self.calculate_angle(right_hip, right_knee, right_ankle)  # Sağ bacak açısı

                    # Açı kontrolü
                    if angle1 < 90 and angle2 < 90:
                        self.stage = "down"  # Aşağı
                    if angle1 > 90 and angle2 > 90 and self.stage == 'down':
                        self.stage = "up"  # Yukarı
                        self.counter += 1  # Sayaç artır

                    # Sayıcıyı ve açıları göster
                    cv2.putText(frame, f'Counter: {self.counter}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, f'Angle1: {int(angle1)}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    cv2.putText(frame, f'Angle2: {int(angle2)}', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                # Görüntüyü JPEG formatına çevir
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        self.cap.release()
        cv2.destroyAllWindows()

    def stop_exercise(self):
        self.is_exercising = False
        if self.cap:
            self.cap.release()  # Kamerayı serbest bırak
        cv2.destroyAllWindows()  # Tüm pencereleri kapat

    def reset_counter(self):
        self.counter = 0
        
    def get_counter(self):
        return self.counter  # Sayaç değerini döndüren fonksiyon
    
    def get_totals(self, user):
        return self.get_total_exercises(user)  # Ortak metodu kullan
