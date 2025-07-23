# the widget of the camera
import sys
import cv2
import mediapipe as mp
import math

from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt, QTimer 
from PyQt6.QtGui import QImage, QPixmap

from src.core.gestures.wink_detector import WinkDetector

from src.core.logic.abstract_functions import get_resource_path

from src.core.gestures.gesture_decoder import GestureDecoder
from src.components.overlay_label import OverlayLabel

class Camera_Widget(QWidget):
    def __init__(self, parent=None, code=None):
        super().__init__(parent)
        self.resize(550, 500)

        self.true_code = code
        self.number_of_hands = 1
        self.validation_method = "click"
        self.parent = parent

        self.wink_detector = WinkDetector()
        self.previous_wink_detection = False
        # Initialize camera
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            raise IOError("Failed to open camera. Please check permissions.")

        # Set up layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # Image label for camera feed
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.image_label.resize(500, 400)
        self.image_label.setStyleSheet("border: 2px solid black;")
        
        # Result text label
        text_image_path = get_resource_path("img/gesture_label.jpg")
        print(f"Using text image path: {text_image_path}")
        self.resultText_label = OverlayLabel("", parent=parent, path=text_image_path)
        self.resultText_label.setFixedSize(300, 80)
        self.resultText_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.resultText_label.setStyleSheet("background-color: rgba(255, 255, 255, 0);")  # Make background transparent
        
        main_layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(self.resultText_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Start timer to update the frame
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30 ms
        
        # Set up mediapipe
        self.mp_hands = mp.solutions.hands
        self.initialize_hands_detector()
        self.mp_drawing = mp.solutions.drawing_utils
        self.gesture_decoder = GestureDecoder()
        
        # Store previous gestures to avoid redundant updates
        self.current_gesture = None
        
        # Keep track of detected hands count for UI adjustments
        self.detected_hands_count = 0

    def initialize_hands_detector(self):
        """Initialize or reinitialize the MediaPipe Hands detector with current settings"""
        # Close existing hands detector if it exists
        if hasattr(self, 'hands'):
            self.hands.close()
            
        # Create a new hands detector with current settings
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.number_of_hands,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    
    def update_true_code(self, new_code):
        """Update the widget with a new binary code"""
        self.true_code = new_code
        # Reset previous gestures to force a UI update
        print(f"Camera code updated to: {new_code}")

    def update_number_of_hands(self, new_number_of_hands):
        """Update the widget with a new number of hands"""
        self.number_of_hands = new_number_of_hands
        # Reinitialize the hands detector with the new number of hands
        self.initialize_hands_detector()
        if self.number_of_hands == 2:
            self.wink_detector.__init__()
        print(f"Number of hands updated to: {new_number_of_hands}")
    
    def update_result_label_size(self, hands_count):
        """Update the result label size based on the number of detected hands"""
        # Only resize if the hands count has changed
        if hands_count != self.detected_hands_count:
            self.detected_hands_count = hands_count
            if hands_count == 2:
                self.resultText_label.setFixedSize(300, 80)
                self.resultText_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            else:
                self.resultText_label.setFixedSize(200, 80)

    def ResultInText(self, list_data):
        if not list_data:
            self.resultText_label.setText("")
            return

        # Reverse the gestures to display them in the correctly
        list_data = [gesture[::-1] for gesture in list_data]
        if self.parent.current_game_mode == "reverse":
            # Count open fingers per hand
            finger_counts = [sum(gesture) for gesture in list_data]

            # If exactly two hands are detected, sum both (e.g., 2 + 5 = 7)
            if len(finger_counts) == 2:
                total = sum(finger_counts)
                result_string = str(total)
            else:
                # Show individual counts separated by space (for 1 or more than 2 hands)
                result_string = ' '.join(str(count) for count in finger_counts)
        else:
            # For other modes: convert each gesture to binary string, e.g., [1,0,0,1,0] -> "10010"
            gesture_strings = [''.join(str(bit) for bit in gesture) for gesture in list_data]
            result_string = ' '.join(gesture_strings)

        self.resultText_label.setText(result_string)
    
    def update_frame(self):
        # Read a frame from the camera
        ret, frame = self.capture.read()
        if not ret:
            return
        # Convert the frame from BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Process the frame with Mediapipe Hands
        self.results = self.hands.process(frame_rgb)
        # Draw hand landmarks on the frame and detect gestures
        multi_hand_gestures = []

        if self.results.multi_hand_landmarks:
            for landmarks in self.results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks\
                (frame_rgb, landmarks, self.mp_hands.HAND_CONNECTIONS)
                gesture = self.gesture_decoder.detect_gestures(landmarks)
                if gesture:
                    multi_hand_gestures.append(gesture)

        self.current_wink_detection = self.wink_detector.detect_wink(frame)
        if self.current_wink_detection != self.previous_wink_detection:
            if self.validation_method == "wink" and self.current_wink_detection:
                if hasattr(self.parent, 'validate_current_code')\
                    and hasattr(self.parent, 'remaining_time')\
                    and self.parent.remaining_time > 0\
                    and hasattr(self.parent, 'current_scene') \
                    and self.parent.current_scene == "kitchen"\
                    and hasattr(self.parent, 'elaborate_answer')\
                    and self.parent.elaborate_answer.isHidden():
                        self.parent.validate_current_code()                    
               
        # Update UI label size based on number of hands
        self.update_result_label_size(len(multi_hand_gestures))

        # Always update current_gesture
        self.current_gesture = multi_hand_gestures if multi_hand_gestures else []
        self.previous_wink_detection = self.current_wink_detection

        # Show raw gesture data in label
        if multi_hand_gestures:
            self.ResultInText(self.current_gesture)
        else:
            self.resultText_label.setText("")
            
        # Convert the frame to a QImage
        height, width, channel = frame_rgb.shape
        bytes_per_line = 3 * width
        qt_image = QImage(
            frame_rgb.data,
            width, 
            height, 
            bytes_per_line, 
            QImage.Format.Format_RGB888)
        
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(
            self.image_label.width(),
            self.image_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        
        # Display the image
        self.image_label.setPixmap(scaled_pixmap)

    def get_currently_shown_code(self):
        """Returns the current gesture(s) as a formatted string"""
        if not hasattr(self, 'current_gesture') or not self.current_gesture:
            return ""

        # Convert each gesture list to a binary string
        gesture_strings = [''.join(str(bit) for bit in gesture) for gesture in self.current_gesture]

        # Join with space if multiple hands
        result = ' '.join(gesture_strings)
        #flip the result array
        result = result[::-1]
        print(f"Current code: {result}")
        return result

    def closeEvent(self, event):
        self.timer.stop()
        if hasattr(self, 'hands'):
            self.hands.close()
        self.capture.release()
        event.accept()
