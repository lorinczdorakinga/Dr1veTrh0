from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtGui import QPainter, QColor, QPalette
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QHBoxLayout, QStackedLayout, QFrame
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import QPoint, QTimer

from gui.game_elements.overlay_button import OverlayButton

class CorrectAnswerOverlay(QWidget):
    def __init__(self, parent=None, code=None):
        # Setup
        super().__init__(parent)
        self.parent = parent
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # No window frame
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 200))
        self.setPalette(palette)
        self.setAutoFillBackground(True)  # Enable auto fill background
        if parent:
            self.resize(parent.width(), parent.height())
        else:
            self.resize(1280, 960)
            
        # Move to top-left corner to cover the entire parent widget
        self.move(0, 0)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)  # Add some margins
        
        # Add elements with improved styling
        self.label = QLabel("Correct!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        font = self.label.font()
        font.setPointSize(36)
        font.setBold(True)
        font.setFamily("Comic Sans MS")
        self.label.setFont(font)
        self.label.setStyleSheet("color: white;")
        
        # Code display label
        self.code_label = QLabel()
        self.code_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        font = self.code_label.font()
        font.setPointSize(24)
        self.code_label.setFont(font)
        self.code_label.setStyleSheet("color: white;")
        
        self.continue_game = OverlayButton("Continue", self)
        
        # Layout arrangement
        layout.addStretch(1)
        layout.addWidget(self.label)
        layout.addStretch(1)
        layout.addWidget(self.code_label)
        layout.addStretch(1)
        layout.addWidget(self.continue_game, 0, Qt.AlignmentFlag.AlignCenter)  # Center the button horizontally
        layout.addStretch(1)
        
        # Set initial code if provided
        if code:
            self.update_code(code)
    
    def showEvent(self, event):
        """Ensure the overlay is properly sized when shown"""
        if self.parent:
            self.resize(self.parent.width(), self.parent.height())
        super().showEvent(event)
    
    def update_code(self, code, current_game_mode=None):
        """Update the displayed code"""
        print(f"--------------------------------------------------------------------------------------------Updating code: {current_game_mode}")
        if code:
            if current_game_mode == "default" or current_game_mode == "double_trouble" or current_game_mode == "speedrun":
                decimal_code = self.binary_array_to_decimal(code)
                binary_code = self.binary_array_to_binary_number(code)
                self.code_label.setText(f"{decimal_code}<sub>(10)</sub>  →  {binary_code}<sub>(2)</sub>")

            elif current_game_mode == "reverse":
                decimal_code = code
                binary_code = self.decimal_to_binary(code)
                self.code_label.setText(f"{binary_code}<sub>(2)</sub>  →  {decimal_code}<sub>(10)</sub>")

            # Make sure rich text rendering is enabled
            self.code_label.setTextFormat(Qt.TextFormat.RichText)
            # Set the font family
            font = self.code_label.font()
            font.setFamily("Comic Sans MS")
            self.code_label.setFont(font)

    def binary_array_to_decimal(self, binary_array):
        """Convert a binary array of size 5 to a decimal number"""
        decimal = int("".join(str(bit) for bit in binary_array), 2)
        return decimal
    
    def binary_array_to_binary_number(self, binary_array):
        """Convert a binary array of size 5 to a binary number"""
        binary_number = "".join(str(bit) for bit in binary_array)
        return binary_number
    
    def decimal_to_binary(self, decimal):
        """Convert a decimal number to a binary array of size 5"""
        binary = bin(decimal)[2:].zfill(5)
        return binary