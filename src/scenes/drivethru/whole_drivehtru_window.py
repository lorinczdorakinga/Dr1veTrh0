from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPalette, QBrush
from src.core.logic.abstract_functions import get_resource_path
from src.scenes.drivethru.drivethru import DriveThruGame

class WholeDriveThruWindow(QWidget):
    def __init__(self, parent=None, width=1280, height=960):
        super().__init__(parent)
        self.width = max(width, 1280)
        self.height = max(height, 960)
        self.setFixedSize(self.width, self.height)
        self.seconds_to_order = 20
        self.remaining_time = 0

        # Set background image
        self.background_image = QPixmap(get_resource_path("img/drivetrhu.jpg")).scaled(
            self.width, self.height, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        palette = QPalette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(self.background_image))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Initialize DriveThruGame
        self.order_window = DriveThruGame(self, width=int(self.width * 0.406), height=int(self.height * 0.416))
        self.order_window.move(
            int(self.width * 0.191),  # 22.8% from left
            int(self.height * 0.4)  # 51.1% from top
        )
        self.order_window.set_order_time(self.seconds_to_order)

        # Load foreground image
        self.foreground_image = QPixmap(get_resource_path("img/drivethru_ablak.png"))

        # Static foreground position
        self.foreground_x = -int(self.width * 0.02)
        self.foreground_y = -int(self.height * 0.7)
        self.foreground_width = int(self.width * 0.304 * 3.25)
        self.foreground_height = int(self.height * 0.717 * 3.25)

        # Create foreground label
        self.foreground_label = QLabel(self)
        scaled_foreground = self.foreground_image.scaled(
            self.foreground_width, self.foreground_height,
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.foreground_label.setPixmap(scaled_foreground)
        self.foreground_label.setGeometry(
            self.foreground_x, self.foreground_y, self.foreground_width, self.foreground_height
        )
        self.foreground_label.raise_()

        # Timer for updating the game
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)  # ~60 FPS

        # Layout (empty)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            int(self.width * 0.191), int(self.height * 0.5),
            int(self.width * 0.191), int(self.height * 0.5)
        )

    def update_game(self):
        """Update game logic and trigger repaint"""
        if not self.order_window.paused:
            self.order_window.update(self.seconds_to_order)
            self.remaining_time = self.order_window.get_remaining_time()
            self.update()

    def get_remaining_time(self):
        """Get the remaining order time"""
        return self.remaining_time

    def reset_timer(self):
        """Reset the timer and game state"""
        self.remaining_time = 0
        self.order_window.reset_timer()

    def set_paused(self, paused):
        """Set the pause state"""
        self.order_window.set_paused(paused)