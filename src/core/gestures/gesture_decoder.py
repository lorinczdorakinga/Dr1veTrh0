import mediapipe as mp
from src.core.gestures.landmarks_dictionary import get_hand_landmarks
from src.core.gestures.methods.finger_count import FingerCount

class GestureDecoder():
    def __init__(self):
        super().__init__()
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def detect_gestures(self, landmarks):
        landmarks_dictionary = get_hand_landmarks(landmarks, self.mp_hands)
        if landmarks_dictionary is None:
            return None
        
        count_list = FingerCount().test(landmarks_dictionary)
        return self.evaluate(count_list)

    def evaluate(self, values):
        if not values:
            return None
        return [1 if val else 0 for val in values]