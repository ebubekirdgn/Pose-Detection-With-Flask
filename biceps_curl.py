import cv2
import mediapipe as mp
import numpy as np

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

def run():
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    
    cap = cv2.VideoCapture(0)
    
    # Sayaç ve state (durum)
    counter = 0
    stage = None

    # Mediapipe Pose modelini başlatma
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

                # Landmark koordinatları
                left_hip = [landmarks[24].x * frame.shape[1], landmarks[24].y * frame.shape[0]]
                left_shoulder = [landmarks[12].x * frame.shape[1], landmarks[12].y * frame.shape[0]]
                left_elbow = [landmarks[14].x * frame.shape[1], landmarks[14].y * frame.shape[0]]

                right_hip = [landmarks[23].x * frame.shape[1], landmarks[23].y * frame.shape[0]]
                right_shoulder = [landmarks[11].x * frame.shape[1], landmarks[11].y * frame.shape[0]]
                right_elbow = [landmarks[13].x * frame.shape[1], landmarks[13].y * frame.shape[0]]

                left_wrist = [landmarks[16].x * frame.shape[1], landmarks[16].y * frame.shape[0]]
                right_wrist = [landmarks[15].x * frame.shape[1], landmarks[15].y * frame.shape[0]]

                # Açıları hesaplama
                shoulder_angle_left = calculate_angle(left_hip, left_shoulder, left_elbow)
                shoulder_angle_right = calculate_angle(right_hip, right_shoulder, right_elbow)

                elbow_angle_left = calculate_angle(left_wrist, left_elbow, left_shoulder)
                elbow_angle_right = calculate_angle(right_wrist, right_elbow, right_shoulder)

                # Açıları ilgili eklem bölgelerine yazdırma
                cv2.putText(image, str(int(shoulder_angle_left)),
                            tuple(np.multiply(left_shoulder, [1, 1]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(image, str(int(shoulder_angle_right)),
                            tuple(np.multiply(right_shoulder, [1, 1]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

                cv2.putText(image, str(int(elbow_angle_left)),
                            tuple(np.multiply(left_elbow, [1, 1]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(image, str(int(elbow_angle_right)),
                            tuple(np.multiply(right_elbow, [1, 1]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

                # Açı kontrolleri
                if 70 <= shoulder_angle_left <= 80 and 70 <= shoulder_angle_right <= 80:
                    shoulder_feedback = "Shoulder Correct"
                else:
                    shoulder_feedback = "Shoulder Incorrect"

                if 20 <= elbow_angle_left <= 160 and 20 <= elbow_angle_right <= 160:
                    elbow_feedback = "Elbow Correct"
                else:
                    elbow_feedback = "Elbow Incorrect"

                # Sağ üst köşede geri bildirim gösterimi
                cv2.putText(image, shoulder_feedback, (10, 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(image, elbow_feedback, (10, 200),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

                # Sayaç ve state logic (up, down)
                if elbow_angle_left > 160 and elbow_angle_right > 160:
                    stage = "down"
                if elbow_angle_left < 30 and elbow_angle_right < 30 and stage == 'down':
                    stage = "up"
                    counter += 1

                # Sağ üst köşede sayaç gösterimi
                cv2.putText(image, 'Counter: ' + str(counter),
                            (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            except:
                pass

            # Poz landmarks'lerini çizdirme
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.imshow('Biceps Curl', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
