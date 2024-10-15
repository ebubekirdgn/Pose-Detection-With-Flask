import cv2
import mediapipe as mp
import numpy as np
from exercises.exercise_strategy import ExerciseStrategy

class ShoulderPressStrategy(ExerciseStrategy):
    def __init__(self):
        self.counter = 0
        self.is_exercising = False
        self.cap = None
        self.stage = None  # Hareket durumu (up/down)

    def calculate_angle(self, a, b, c):
        """Üç nokta arasındaki açıyı hesapla."""
        a = np.array(a)  # Omuz
        b = np.array(b)  # Dirsek
        c = np.array(c)  # Bilek
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
        
        return angle

    def draw_arc(self, image, center, angle, max_angle=140, radius=30):
            """Belirli bir açıya göre yay çizer."""
            angle_fraction = angle / max_angle  # Açı oranı
            end_angle = int(360 * angle_fraction)  # Çizilecek dilimin son açısı
            
            # Dilimi çiz
            cv2.ellipse(image, center, (radius, radius), 0, 0, end_angle, (0, 255, 0), 3)
            
            # Açıyı ortada göster
            cv2.putText(image, f'{int(angle)}', 
                        (center[0] - 30, center[1] + 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            
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
        
        max_angle = 160  # Maksimum açı sınırı
        tolerance = 30  # Açı toleransı

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                
                # Renk dönüşümü
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                
                # Poz tahmini yap
                results = pose.process(image)
                
                # Renkleri tekrar RGB'den BGR'ye çevir
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                # İskeleti çiz
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                
                try:
                    # Koordinatları al
                    landmarks = results.pose_landmarks.landmark
                    
                    # Sağ ve sol omuz, dirsek ve bilek koordinatları
                    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * image.shape[1], 
                                      landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * image.shape[0]]
                    right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x * image.shape[1], 
                                   landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y * image.shape[0]]
                    right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x * image.shape[1], 
                                   landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y * image.shape[0]]
                    
                    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * image.shape[1], 
                                     landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * image.shape[0]]
                    left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * image.shape[1], 
                                  landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * image.shape[0]]
                    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x * image.shape[1], 
                                  landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y * image.shape[0]]
                    
                    # Sağ ve sol açıyı hesapla
                    right_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
                    left_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
                    
                    # Her iki omuz için dilim çizimi
                    right_shoulder_center = (int(right_shoulder[0]), int(right_shoulder[1]))
                    self.draw_arc(image, right_shoulder_center, right_angle, max_angle)
                    
                    left_shoulder_center = (int(left_shoulder[0]), int(left_shoulder[1]))
                    self.draw_arc(image, left_shoulder_center, left_angle, max_angle)
                    
                    # Açıların durumunu kontrol et
                    if (75 - tolerance < right_angle < 160 + tolerance) and (75 - tolerance < left_angle < 160 + tolerance):
                        if self.stage is None or self.stage == "down":  # Yukarıya hareket başladı
                            self.stage = "up"  # Yukarı duruma geç
                    else:
                        if self.stage == "up":  # Yukarıdan aşağıya hareket yapıldıysa
                            self.stage = "down"  # Aşağı duruma geç
                            self.counter += 1  # Sayaç artır
                            print(f"Counter: {self.counter}")
                        
                except Exception as e:
                    print(e)
                
                # Sayaç değerini ekrana yaz
                cv2.putText(image, f'Count: {self.counter}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                
                # Görüntüyü JPEG formatına çevir
                ret, buffer = cv2.imencode('.jpg', image)
                image = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')

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