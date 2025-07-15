from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtGui import QPainter, QColor, QPalette
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QHBoxLayout, QStackedLayout, QFrame
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import QPoint, QTimer

from gui.game_elements.overlay_button import OverlayButton

class TimeIsUpOverlay(QWidget):
    def __init__(self, parent=None):
        # Setup
        super().__init__(parent)

        self.parent = parent
        
        # Configure the widget to appear as an overlay
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # No window frame
        
        # Create a QPalette
        palette = QPalette()
        # Set the background color with an alpha value (e.g., 128 for 50% transparency)
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 200))
        self.setPalette(palette)
        self.setAutoFillBackground(True)  # Enable auto fill background
        
        # Match parent size initially
        if parent:
            self.resize(parent.width(), parent.height())
        else:
            self.resize(1280, 960)
            
        # Move to top-left corner to cover the entire parent widget
        self.move(0, 0)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)  # Add some margins
        
        # Add elements with improved styling
        self.label = QLabel("Time is up! You lost!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        font = self.label.font()
        font.setPointSize(24)
        font.setBold(True)
        font.setFamily("Comic Sans MS")
        self.label.setFont(font)
        self.label.setStyleSheet("color: white;")
        
        self.play_again = OverlayButton("Play again", self)
        self.main_menu = OverlayButton("Main menu", self)
        
        layout.addStretch(1)
        layout.addWidget(self.label)
        layout.addStretch(1)
        layout.addWidget(self.play_again, 0, Qt.AlignmentFlag.AlignCenter)  # Center the button horizontally
        layout.addWidget(self.main_menu, 0, Qt.AlignmentFlag.AlignCenter)  # Center the button horizontally
        layout.addStretch(1)
            
    def showEvent(self, event):
        """Ensure the overlay is properly sized when shown"""
        if self.parent:
            self.resize(self.parent.width(), self.parent.height())
        super().showEvent(event)