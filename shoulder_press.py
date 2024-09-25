import cv2
import mediapipe as mp
import numpy as np

# MediaPipe kurulumu
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Dirsek açısını hesaplamak için fonksiyon
def calculate_angle(a, b, c):
    a = np.array(a)  # Omuz
    b = np.array(b)  # Dirsek
    c = np.array(c)  # Bilek
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
    
    return angle

# Dilim (yay) çizen fonksiyon
def draw_arc(image, center, angle, max_angle=140, radius=30):
    angle_fraction = angle / max_angle  # Açı oranı
    end_angle = int(360 * angle_fraction)  # Çizilecek dilimin son açısı
    
    # Dilimi çiz
    cv2.ellipse(image, center, (radius, radius), 0, 0, end_angle, (0, 255, 0), 3)
    
    # Açıyı ortada göster
    cv2.putText(image, f'{int(angle)} deg', 
                (center[0] - 30, center[1] + 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

# Video yakalama
cap = cv2.VideoCapture(0)

# Pose algılama için MediaPipe Pose modeli
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    
    counter = 0
    stage = None  # Hareket durumu (up/down)
    
    while cap.isOpened():
        ret, frame = cap.read()
        
        # Renkleri BGR'den RGB'ye çevir
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
            right_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
            left_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
            
            # Her iki omuz için dilim çizimi
            max_angle = 160  # Maksimum açı sınırı
            
            right_shoulder_center = (int(right_shoulder[0]), int(right_shoulder[1]))
            draw_arc(image, right_shoulder_center, right_angle, max_angle)
            
            left_shoulder_center = (int(left_shoulder[0]), int(left_shoulder[1]))
            draw_arc(image, left_shoulder_center, left_angle, max_angle)
            
            # Açı kontrolü
            tolerance = 30  # Tolerans açısı
            
            # Açıların durumunu kontrol et
            if (75 - tolerance < right_angle < 160 + tolerance) and (75 - tolerance < left_angle < 160 + tolerance):
                if stage is None or stage == "down":  # Yukarıya hareket başladı
                    stage = "up"  # Yukarı duruma geç
            else:
                if stage == "up":  # Yukarıdan aşağıya hareket yapıldıysa
                    stage = "down"  # Aşağı duruma geç
                    counter += 1  # Sayaç artır
                    print(f"Counter: {counter}")
                
        except Exception as e:
            print(e)
        
        # Sayaç değerini ekrana yaz
        cv2.putText(image, f'Count: {counter}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Görüntüyü göster
        cv2.imshow('Shoulder Press Angle Detection with Arcs and Counter', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
