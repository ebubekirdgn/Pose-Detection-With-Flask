import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

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

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
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
                angle1 = calculate_angle(left_hip, left_knee, left_ankle)  # Sol bacak açısı
                angle2 = calculate_angle(right_hip, right_knee, right_ankle)  # Sağ bacak açısı

                # Açı kontrolü
                if angle1 < 90 and angle2 < 90:
                    stage = "down"  # Aşağı
                if angle1 > 90 and angle2 > 90 and stage == 'down':
                    stage = "up"  # Yukarı
                    counter += 1  # Sayaç artır

                # Ekrana yazdırma
                cv2.putText(image, f'Counter: {counter}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(image, f'Angle1: {int(angle1)}', (int(left_knee[0]), int(left_knee[1] - 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)  # Sol dizin üstüne yaz
                cv2.putText(image, f'Angle2: {int(angle2)}', (int(right_knee[0]), int(right_knee[1] - 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)  # Sağ dizin üstüne yaz

            except:
                pass

            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.imshow('Squat Control', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
