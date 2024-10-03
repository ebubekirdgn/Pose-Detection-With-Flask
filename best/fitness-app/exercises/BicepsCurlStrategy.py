import cv2
import mediapipe as mp
import numpy as np

from exercises.exercise_strategy import ExerciseStrategy


class BicepsCurlStrategy(ExerciseStrategy):

    @staticmethod
    def calculate_angle(a, b, c):
        a = np.array(a)  # İlk nokta
        b = np.array(b)  # Orta nokta
        c = np.array(c)  # Son nokta
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle

    def perform_exercise(self):
        # Pose algılama ve çizim araçları
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
        cap = cv2.VideoCapture(0)  # Kamerayı aç
        counter = 0
        stage = None

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                ret, frame = cap.read()
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

                    # Landmarkları al (Sol kol için dirsek, omuz ve bilek)
                    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * frame.shape[1],
                                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * frame.shape[0]]
                    left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * frame.shape[1],
                                landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * frame.shape[0]]
                    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x * frame.shape[1],
                                landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y * frame.shape[0]]

                    # Sağ kol için landmarkları al
                    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * frame.shape[1],
                                    landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * frame.shape[0]]
                    right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x * frame.shape[1],
                                landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y * frame.shape[0]]
                    right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x * frame.shape[1],
                                landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y * frame.shape[0]]

                    # Sol kol açısını hesapla
                    angle1 = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
                    # Sağ kol açısını hesapla
                    angle2 = self.calculate_angle(right_shoulder, right_elbow, right_wrist)

                    # Açı kontrolü: Biceps curl aşağı mı yukarı mı?
                    if angle1 > 160 and angle2 > 160:
                        stage = "down"
                    if angle1 < 30 and angle2 < 30 and stage == 'down':
                        stage = "up"
                        counter += 1  # Sayaç artır
                      
                    # Ekrana yazdırma
                    cv2.putText(image, f'Counter: {counter}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(image, f'{int(angle1)}', (int(left_elbow[0]), int(left_elbow[1] - 20)),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    cv2.putText(image, f'{int(angle2)}', (int(right_elbow[0]), int(right_elbow[1] - 20)),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                except Exception as e:
                    pass

                # Pozları çiz
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                ret, buffer = cv2.imencode('.jpg', image)  # JPEG formatına çevir
                frame = buffer.tobytes()

                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        cap.release()
