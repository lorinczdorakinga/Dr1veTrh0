import pygame
import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtGui import QFont

class OrderTimer(QWidget):
    def __init__(self):
        self.time = 10
        layout = QVBoxLayout()

        self.timer = QLabel(str(self.time))
        self.timer.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        font = QFont()
        font.setPointSize(22)  
        font.setBold(True)     
        self.timer.setFont(font)
        self.timer.setMargin(50)

        self.secondSceneButton = QPushButton("Katamhoz")
        self.secondSceneButton.clicked.connect(self.switch_to_scene2)
        
        layout.addWidget(self.timer)
        layout.addWidget(self.secondSceneButton)

    def OrderProcessing(self):
        self.time = 10
        for _ in range(self.time):
            self.timer.setText(str(self.time))
            print(self.time)
            self.time -= 1
            pygame.time.wait(1000)  # Wait for 1 second
    def switch_to_scene2(self):
        return False

