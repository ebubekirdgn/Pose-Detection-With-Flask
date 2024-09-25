import cv2
import mediapipe as mp
import numpy as np

# Mediapipe başlangıç ayarları
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Açıyı hesaplayan fonksiyon
def calculate_angle(a, b, c):
    a = np.array(a)  # İlk nokta
    b = np.array(b)  # Ortadaki nokta
    c = np.array(c)  # Son nokta

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

# Video aç
cap = cv2.VideoCapture(0)

# Sayaç ve aşama
counter = 0
stage = None  # Hareketin durumu (aşağıda mı, yukarıda mı)

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Görüntüyü ters çevir
        frame = cv2.flip(frame, 1)

        # BGR'den RGB'ye dönüşüm
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        
        # Pose tahmini
        results = pose.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Landmarkları çiz
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Landmarkları al
            landmarks = results.pose_landmarks.landmark

            # Belirli landmarkları al
            shoulder_left = [landmarks[11].x, landmarks[11].y]  # Sol omuz (11)
            elbow_left = [landmarks[13].x, landmarks[13].y]    # Sol dirsek (13)
            wrist_left = [landmarks[15].x, landmarks[15].y]    # Sol bilek (15)
            shoulder_right = [landmarks[12].x, landmarks[12].y] # Sağ omuz (12)
            elbow_right = [landmarks[14].x, landmarks[14].y]   # Sağ dirsek (14)
            wrist_right = [landmarks[16].x, landmarks[16].y]   # Sağ bilek (16)
            hip_left = [landmarks[23].x, landmarks[23].y]      # Sol kalça (23)
            hip_right = [landmarks[24].x, landmarks[24].y]     # Sağ kalça (24)

            # Açıları hesapla
            angle_left_shoulder_elbow = calculate_angle(hip_left, shoulder_left, elbow_left)
            angle_right_shoulder_elbow = calculate_angle(hip_right, shoulder_right, elbow_right)
            angle_left_elbow_wrist = calculate_angle(shoulder_left, elbow_left, wrist_left)
            angle_right_elbow_wrist = calculate_angle(shoulder_right, elbow_right, wrist_right)

            # Açıları kontrol et
            if (75 <= angle_left_shoulder_elbow <= 160) and (75 <= angle_right_shoulder_elbow <= 160):
                if angle_left_elbow_wrist >= 75 and angle_left_elbow_wrist <= 160 and angle_right_elbow_wrist >= 75 and angle_right_elbow_wrist <= 160:
                    if stage is None:  # Hiçbir aşamada değilse
                        stage = 'down'  # İlk olarak aşağı aşamasına geç
                    elif stage == 'down':  # Eğer aşağı aşamasındaysak
                        stage = 'up'  # Yukarı aşamasına geç
                elif stage == 'up':  # Eğer yukarı aşamasındaysak
                    counter += 1  # Sayaç artır
                    stage = 'down'  # Aşağı aşamasına geç

            else:
                stage = None  # Açı uygun değilse durumu sıfırla

            # Açıları ve sayacı görüntüle
            cv2.putText(image, f'Count: {counter}', (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(image, f'Left Angle: {angle_left_shoulder_elbow:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, f'Right Angle: {angle_right_shoulder_elbow:.2f}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Görüntüyü göster
        cv2.imshow('Shoulder Press Angle Detection', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
