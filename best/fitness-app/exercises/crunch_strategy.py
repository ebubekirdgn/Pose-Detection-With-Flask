from exercises.exercise_strategy import ExerciseStrategy
import cv2
import mediapipe as mp
import numpy as np

class CrunchStrategy(ExerciseStrategy):

    def __init__(self):
        self.counter = 0  # Egzersiz sayısı
        self.is_exercising = False  # Egzersiz durumu (başladı mı, bitti mi?)
        self.cap = None  # VideoCapture nesnesi, kamerayı başlatıp kontrol etmek için
 
    def perform_exercise(self):
        # Pose algılama ve çizim araçları
        self.is_exercising = True
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)  # Kamerayı aç
        self.stage = None

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

                # Renk dönüşümü
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                # Pose algılama
                results = pose.process(image)

                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                try:
                    landmarks = results.pose_landmarks.landmark

                    # Landmarkları al (Crunch hareketi için omuz, diz ve kalça)
                    right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x * frame.shape[1],
                                landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y * frame.shape[0]]
                    right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x * frame.shape[1],
                                landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y * frame.shape[0]]
                    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * frame.shape[1],
                                    landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * frame.shape[0]]

                    # Açıyı hesapla (Hip-Knee-Shoulder açısı)
                    angle = self.calculate_angle(right_hip, right_knee, right_shoulder)

                    # Açı kontrolü: Crunch yukarıda mı, aşağıda mı?
                    if angle > 170:
                        self.stage = "down"
                    if angle < 60 and self.stage == 'down':
                        self.stage = "up"
                        self.counter += 1  # Sayaç artır

                    # Ekrana yazdırma
                    cv2.putText(image, f'Counter: {self.counter}', (50, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(image, f'Angle: {int(angle)}', (int(right_knee[0]), int(right_knee[1] - 20)),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                except Exception as e:
                    pass

                # Pozları çiz
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                # Görüntüyü yayına hazır hale getirme
                ret, buffer = cv2.imencode('.jpg', image)  # JPEG formatına çevir
                frame = buffer.tobytes()

                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    def calculate_angle(self, a, b, c):
        a = np.array(a)  # İlk nokta
        b = np.array(b)  # Orta nokta
        c = np.array(c)  # Son nokta

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

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
    