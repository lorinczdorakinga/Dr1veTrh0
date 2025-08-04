from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtGui import QPainter, QColor, QPalette, QFont
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QHBoxLayout, QStackedLayout, QFrame
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import QPoint, QTimer

from src.components.overlay_button import OverlayButton
from src.components.overlay_label import OverlayLabel

class TimeIsUpOverlay(QWidget):
    def __init__(self, parent=None, highscore=False):
        # Setup
        super().__init__(parent)
        self.highscore = highscore
        self.parent = parent
        self.width = self.parent.width() if self.parent else 1280
        self.height = self.parent.height() if self.parent else 960
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # No window frame
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 200))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        self.resize(self.width, self.height)
        self.move(0, 0)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            int(self.width * 0.03), int(self.height * 0.05),
            int(self.width * 0.03), int(self.height * 0.05)
        )  # Responsive margins
        
        # Add elements with improved styling
        self.label = QLabel("Time is up! You lost!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        font = QFont()
        font.setPointSize(int(self.height * 0.03))  # 3% of height
        font.setBold(True)
        font.setFamily("Comic Sans MS")
        self.label.setFont(font)
        self.label.setStyleSheet("color: white;")

        self.highscore_label = OverlayLabel("New highscore reached!", self)
        self.highscore_label.setFont(QFont("Comic Sans MS", 24, QFont.Weight.Bold))
        self.highscore_label.setTextColor(QColor("#FF0000"))  # Bright red for visibility
        # self.highscore_label.setFixedWidth(self.width // 2)
        self.highscore_label.hide()
        
        self.play_again = OverlayButton("Play again", self)
        self.play_again.setFixedSize(
            int(self.width * 0.2),  # 20% of width
            int(self.height * 0.08)  # 8% of height
        )
        self.main_menu = OverlayButton("Main menu", self)
        self.main_menu.setFixedSize(
            int(self.width * 0.2),  # 20% of width
            int(self.height * 0.08)  # 8% of height
        )
        
        layout.addStretch(1)
        layout.addWidget(self.label)
        layout.addStretch(1)
        layout.addWidget(self.highscore_label, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
        layout.addWidget(self.play_again, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.main_menu, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
    
    def showEvent(self, event):
        """Ensure the overlay is properly sized when shown"""
        if self.parent:
            self.width = self.parent.width()
            self.height = self.parent.height()
            self.resize(self.width, self.height)
        if self.highscore:
            self.highscore_label.show()
            self.highscore_label.raise_()
            QTimer.singleShot(10000, self.highscore_label.hide)

        super().showEvent(event)