import cv2
import mediapipe as mp
import numpy as np

# MediaPipe için gerekli bileşenleri ayarla
mp_pose = mp.solutions.pose

# Hedef işaretli noktalar (Lateral Raise için)
landmarks_to_highlight = [23, 11, 13, 24, 12, 14, 16, 14, 12, 15, 13, 11]

# Bağlantılı noktalar (indexler)
lines_to_draw = [
    (23, 11), (11, 13), 
    (24, 12), (12, 14), 
    (16, 14), (14, 12), 
    (15, 13), (13, 11),
    (23, 24)  # İki omuz arasındaki bağlantı
]

# Video yakalama
cap = cv2.VideoCapture(0)

def calculate_angle(a, b, c):
    """Üç nokta arasındaki açıyı hesapla."""
    ba = a - b
    bc = c - b
    angle = np.arctan2(bc[1], bc[0]) - np.arctan2(ba[1], ba[0])
    angle = np.abs(angle * 180.0 / np.pi)  # Radyan cinsinden dereceye çevir
    if angle > 180.0:
        angle = 360 - angle
    return angle

# Sayıcı
counter = 0
state = None  # 'up' veya 'down' durumu
threshold_up_angle1 = 90  # Açı eşiği yukarı hareket için
threshold_down_angle1 = 100  # Açı eşiği aşağı hareket için
threshold_up_angle2 = 20  # Açı eşiği aşağı hareket için
threshold_down_angle2 = 160  # Açı eşiği yukarı hareket için

with mp_pose.Pose(static_image_mode=False, model_complexity=2, enable_segmentation=False) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Görüntüyü ayna etkisi için ters çevir
        frame = cv2.flip(frame, 1)
        
        # BGR'den RGB'ye çevir
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(image_rgb)

        # Landmark'ları gizle ve sadece belirli noktaları çiz
        if result.pose_landmarks:
            # İşaretli noktaları çiz
            points = []
            for idx in landmarks_to_highlight:
                landmark = result.pose_landmarks.landmark[idx]
                height, width, _ = frame.shape
                x, y = int(landmark.x * width), int(landmark.y * height)

                # İşaretli noktayı daire ile vurgula
                cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)
                points.append((x, y))

            # Belirli noktaları birleştir
            for start_idx, end_idx in lines_to_draw:
                start_point = points[landmarks_to_highlight.index(start_idx)]
                end_point = points[landmarks_to_highlight.index(end_idx)]
                cv2.line(frame, start_point, end_point, (255, 0, 0), 2)  # Mavi çizgi

            # Açıları hesapla
            point_a = np.array(points[landmarks_to_highlight.index(23)])  # 23
            point_b = np.array(points[landmarks_to_highlight.index(11)])  # 11
            point_c = np.array(points[landmarks_to_highlight.index(13)])  # 13
            angle1 = calculate_angle(point_a, point_b, point_c)

            point_d = np.array(points[landmarks_to_highlight.index(24)])  # 24
            point_e = np.array(points[landmarks_to_highlight.index(12)])  # 12
            point_f = np.array(points[landmarks_to_highlight.index(14)])  # 14
            angle2 = calculate_angle(point_d, point_e, point_f)

            # Açı kontrolü ve durum belirleme
            if (threshold_up_angle1 <= angle1 <= threshold_down_angle1) and (threshold_up_angle2 <= angle2 <= threshold_down_angle2) and (state != 'up'):
                counter += 1  # Doğru hareket yapıldığında sayacı artır
                state = 'up'
            elif angle1 < threshold_up_angle1 and angle2 < threshold_up_angle2 and (state == 'up'):
                state = 'down'

            # Sayıcıyı ve açıları göster
            cv2.putText(frame, f'Reps: {counter}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(frame, f'Angle 1: {angle1:.2f}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(frame, f'Angle 2: {angle2:.2f}', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Sonucu göster
        cv2.imshow('MediaPipe Pose', frame)
        if cv2.waitKey(5) & 0xFF == 27:  # 'Esc' tuşuna basıldığında çık
            break

cap.release()
cv2.destroyAllWindows()
