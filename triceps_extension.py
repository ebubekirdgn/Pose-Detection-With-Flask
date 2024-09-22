import cv2
import mediapipe as mp
import numpy as np

# Mediapipe ayarları
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Açı hesaplama fonksiyonu
def calculate_angle(a, b, c):
    a = np.array(a)  # İlk nokta
    b = np.array(b)  # Ortadaki nokta
    c = np.array(c)  # Son nokta

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

def run():
    cap = cv2.VideoCapture(0)
    counter = 0
    stage = None

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                # Triceps Extension için önemli noktalar
                left_shoulder = [results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * frame.shape[1],
                                 results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * frame.shape[0]]
                left_elbow = [results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * frame.shape[1],
                               results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * frame.shape[0]]
                left_wrist = [results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value].x * frame.shape[1],
                               results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value].y * frame.shape[0]]

                right_shoulder = [results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * frame.shape[1],
                                  results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * frame.shape[0]]
                right_elbow = [results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x * frame.shape[1],
                               results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y * frame.shape[0]]
                right_wrist = [results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value].x * frame.shape[1],
                               results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value].y * frame.shape[0]]

                # Sol kol için açı hesapla
                left_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)

                # Sağ kol için açı hesapla
                right_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

                # Açı kontrolü
                if left_angle > 160 and right_angle > 160:
                    stage = "down"  # Aşağı hareket

                if left_angle < 30 and right_angle < 30 and stage == 'down':
                    stage = "up"  # Yukarı hareket
                    counter += 1  # Sayaç artır

                # Ekrana yazdırma
                cv2.putText(image, f'{int(left_angle)}', (int(left_elbow[0]), int(left_elbow[1] + 20)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)  # Sol kol
                cv2.putText(image, f'{int(right_angle)}', (int(right_elbow[0]), int(right_elbow[1] + 20)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)  # Sağ kol

                # Geri bildirim
                if left_angle < 30 or right_angle < 30:
                    feedback = "Keep going!"
                elif (left_angle > 160 and right_angle > 160):
                    feedback = "Good job!"
                else:
                    feedback = "Try again!"

                cv2.putText(image, feedback, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(image, f'Counter: {counter}', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.imshow('Triceps Extension Control', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
