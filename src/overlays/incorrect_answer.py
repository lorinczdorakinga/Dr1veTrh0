from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtGui import QPainter, QColor, QPalette, QFont
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QHBoxLayout, QStackedLayout, QFrame
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import QPoint, QTimer

from src.components.overlay_button import OverlayButton

class IncorrectAnswerOverlay(QWidget):
    def __init__(self, parent=None, true_code=None, current_code=None):
        # Setup
        super().__init__(parent)
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
        self.label = QLabel("Game over!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        font = QFont()
        font.setPointSize(int(self.height * 0.04))  # 4% of height
        font.setFamily("Comic Sans MS")
        font.setBold(True)
        self.label.setFont(font)
        self.label.setStyleSheet("color: white;")

        # Code display labels
        self.true_code_label = QLabel("")
        self.true_code_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        font = QFont()
        font.setPointSize(int(self.height * 0.03))  # 3% of height
        self.true_code_label.setFont(font)
        self.true_code_label.setStyleSheet("color: white;")
        
        self.current_code_label = QLabel("")
        self.current_code_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        font = QFont()
        font.setPointSize(int(self.height * 0.03))  # 3% of height
        self.current_code_label.setFont(font)
        self.current_code_label.setStyleSheet("color: white;")

        self.retry_game = OverlayButton("Retry", self)
        self.retry_game.setFixedSize(
            int(self.width * 0.2),  # 20% of width
            int(self.height * 0.08)  # 8% of height
        )
        self.main_menu = OverlayButton("Main Menu", self)
        self.main_menu.setFixedSize(
            int(self.width * 0.2),  # 20% of width
            int(self.height * 0.08)  # 8% of height
        )
        
        layout.addStretch(1)
        layout.addWidget(self.label)
        layout.addStretch(1)
        layout.addWidget(self.true_code_label)
        layout.addWidget(self.current_code_label)
        layout.addStretch(1)
        layout.addWidget(self.retry_game, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.main_menu, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
        
        # Set initial code if provided
        if true_code and current_code:
            self.update_code(true_code, current_code)
    
    def showEvent(self, event):
        """Ensure the overlay is properly sized when shown"""
        if self.parent:
            self.width = self.parent.width()
            self.height = self.parent.height()
            self.resize(self.width, self.height)
        super().showEvent(event)

    def update_code(self, true_code, current_code, current_game_mode=None):
        """Update the displayed code labels with the true and current codes"""
        print(f"--------------------------------------------------------------------------------------------Updating code: {true_code}, {current_code}")
        print(f"--------------------------------------------------------------------------------------------Updating game mode: {current_game_mode}")

        if true_code and current_code:
            if current_game_mode == "default" or current_game_mode == "double_trouble" or current_game_mode == "speedrun":
                true_decimal = self.binary_array_to_decimal(true_code)
                true_binary_number = self.binary_array_to_binary_number(true_code)
                
                self.true_code_label.setText(f"{true_decimal}<sub>(10)</sub>  →  {true_binary_number}<sub>(2)</sub>")
                self.current_code_label.setText(f"{current_code}<sub>(2)</sub>  !=  {true_binary_number}<sub>(2)</sub>")
            
            elif current_game_mode == "reverse":
                true_binary_number = self.decimal_to_binary(true_code)
                
                self.true_code_label.setText(f"{true_binary_number}<sub>(2)</sub>  →  {true_code}<sub>(10)</sub>")
                self.current_code_label.setText(f"{true_binary_number}<sub>(2)</sub>  !=  {current_code}<sub>(10)</sub>")

            self.true_code_label.setTextFormat(Qt.TextFormat.RichText)
            font = QFont()
            font.setPointSize(int(self.height * 0.03))  # 3% of height
            font.setFamily("Comic Sans MS")
            self.true_code_label.setFont(font)
            self.current_code_label.setTextFormat(Qt.TextFormat.RichText)
            font = QFont()
            font.setPointSize(int(self.height * 0.03))  # 3% of height
            font.setFamily("Comic Sans MS")
            self.current_code_label.setFont(font)
        else:
            self.current_code_label.setText("Please show a valid code.")

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