import cv2
import mediapipe as mp
import numpy as np

mp_face_mesh = mp.solutions.face_mesh

# Eye indices from MediaPipe FaceMesh model
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

class WinkDetector:
    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.EAR_THRESHOLD = 0.2
        self.winking = False

        self.wink_counter = 0
        self.max_wink_frames = 3   # Require blink for 3 consecutive frames
        self.debounce_frames = 10  # Debounce after detection

    def _calculate_ear(self, eye_points, landmarks, width, height):
        coords = [(
            int(landmarks[i].x * width), 
            int(landmarks[i].y * height)) 
            for i in eye_points]
        A = self._distance(coords[1], coords[5])
        B = self._distance(coords[2], coords[4])
        C = self._distance(coords[0], coords[3])
        ear = (A + B) / (2.0 * C)
        return ear

    def _distance(self, p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def detect_wink(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        h, w, _ = frame.shape
        current_wink = False

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]

            left_ear = self._calculate_ear(LEFT_EYE, face_landmarks.landmark, w, h)
            right_ear = self._calculate_ear(RIGHT_EYE, face_landmarks.landmark, w, h)

            # Only one eye closed → possible wink
            if (left_ear < self.EAR_THRESHOLD) != (right_ear < self.EAR_THRESHOLD):
                self.wink_counter += 1
                if self.wink_counter >= self.max_wink_frames:
                    current_wink = True
                    self.wink_counter = -self.debounce_frames  # Start debounce cooldown
            else:
                if self.wink_counter > 0:
                    self.wink_counter -= 1  # Reset counter if no wink detected
        else:
            # No face detected: reset counter
            self.wink_counter = 0
        self.winking = current_wink
        return self.winking

    def release(self):
        self.face_mesh.close()