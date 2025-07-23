from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QTime
from PyQt6.QtGui import QPalette, QBrush, QPixmap
from src.core.logic.abstract_functions import get_resource_path

class Kitchen(QWidget):
    def __init__(self, parent=None, width=1280, height=960):
        super().__init__(parent)
        self.width = max(width, 1280)
        self.height = max(height, 960)
        self.setFixedSize(self.width, self.height)
        self.seconds_to_order = 20
        self.remaining_time = 0
        self.paused = False
        self.order_start_time = None

        # Set background image
        try:
            self.background_image = QPixmap(get_resource_path("img/kitchen.jpg")).scaled(
                self.width, self.height, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
        except:
            self.background_image = QPixmap()
            self.background_image.fill(Qt.GlobalColor.blue)  # Fallback blue background

        palette = QPalette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(self.background_image))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Timer for updating remaining time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(16)  # ~60 FPS

    def update_time(self):
        """Update the remaining time"""
        if self.paused or not self.order_start_time:
            return
        current_time = QTime.currentTime()
        elapsed_time = self.order_start_time.msecsTo(current_time)
        self.remaining_time = max(0, self.seconds_to_order * 1000 - elapsed_time)

    def get_remaining_time(self):
        """Get the remaining time"""
        return self.remaining_time

    def reset_timer(self):
        """Reset the timer"""
        self.remaining_time = 0
        self.order_start_time = None

    def set_order_time(self, time):
        """Set the order time in seconds"""
        self.seconds_to_order = time
        if not self.paused and not self.order_start_time:
            self.order_start_time = QTime.currentTime()

    def set_paused(self, paused):
        """Set the pause state"""
        self.paused = paused
        if not paused and not self.order_start_time:
            self.order_start_time = QTime.currentTime()