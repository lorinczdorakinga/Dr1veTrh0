from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QTime
from PyQt6.QtGui import QPainter, QPixmap
from src.core.logic.abstract_functions import get_resource_path

class DriveThruGame(QWidget):
    def __init__(self, parent=None, width=605, height=400):
        super().__init__(parent)
        self.width = width
        self.height = height
        self.setFixedSize(self.width, self.height)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)  # Allow clicks to pass through

        self.x = float(self.width)  # Start off-screen
        self.y = int(self.height * 0.125)  # 12.5% of height (50/400)
        self.speed = int(self.width * 0.0165)  # 1.65% of width (10/605)
        self.middle_reached = False
        self.paused = False
        self.seconds_to_order = 20
        self.order_start_time = None  # Will store QTime
        self.remaining_time = 0

        # Load car image
        self.car_image = QPixmap(get_resource_path("img/car2.png")).scaled(
            int(self.width * 2.644),  # 264.4% of width (1600/605)
            int(self.height * 2),  # 200% of height (800/400)
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )

        # Timer for animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(16)  # ~60 FPS

    def set_paused(self, paused):
        """Set the pause state"""
        self.paused = paused
        if not paused and self.middle_reached and self.order_start_time is None:
            self.order_start_time = QTime.currentTime()

    def update(self, seconds_to_order):
        """Update game state"""
        self.seconds_to_order = seconds_to_order
        if not self.paused:
            self.process_events()
        super().update()

    def update_position(self):
        """Update car position"""
        if self.paused:
            self.update(self.seconds_to_order)
            return

        middle_x = self.width / 2 - (self.car_image.width() / 2)
        if not self.middle_reached and middle_x - self.speed < self.x <= middle_x:
            self.middle_reached = True
            self.order_start_time = QTime.currentTime()

        if not self.middle_reached and self.x > -self.car_image.width():
            self.x -= self.speed
        elif not self.middle_reached and self.x <= -self.car_image.width():
            self.x = float(self.width)

        self.update(self.seconds_to_order)

    def process_events(self):
        """Process timer events"""
        if self.paused or not self.middle_reached or not self.order_start_time:
            return

        current_time = QTime.currentTime()
        elapsed_time = self.order_start_time.msecsTo(current_time)
        self.remaining_time = max(0, self.seconds_to_order * 1000 - elapsed_time)

        if self.remaining_time <= 0:
            self.middle_reached = False
            self.x -= self.speed

    def paintEvent(self, event):
        """Paint the car"""
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        painter.drawPixmap(int(self.x), self.y, self.car_image)
        painter.end()

    def get_remaining_time(self):
        """Get the current remaining time in milliseconds"""
        return self.remaining_time

    def reset_timer(self):
        """Reset the timer and state"""
        self.remaining_time = 0
        self.middle_reached = False
        self.order_start_time = None
        self.x = float(self.width)

    def set_order_time(self, time):
        """Set the order time in seconds"""
        self.seconds_to_order = time