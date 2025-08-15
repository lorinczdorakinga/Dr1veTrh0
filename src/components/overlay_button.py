from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QFont, QPixmap, QPainter, QTransform
from PyQt6.QtCore import Qt, QTimer
from src.core.logic.abstract_functions import get_resource_path
from src.core.logic.sound_manager import SoundManager

class OverlayButton(QPushButton):
    def __init__(self, text=None, parent=None, path=None, sound_manager=None):
        super().__init__(text, parent)
        self.sound_manager = sound_manager or SoundManager.get_instance(parent)
        self.setMinimumSize(200, 60)
        self.path = path
        
        font = QFont("Comic Sans MS")
        font.setPointSize(14)
        font.setBold(True)
        self.setFont(font)
        
        self.clicked.connect(self.play_click_sound)
        self.background_img = QPixmap()
        
        if path:
            self.update_image(path)
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 10px;
                    font-family: "Comic Sans MS";
                    font-weight: bold;
                    font-size: 24pt;
                }
            """)
        else:
            self.setDefaultStyle()

    def play_click_sound(self):
        print("Playing button_click.wav")
        if self.sound_manager:
            try:
                QTimer.singleShot(0, lambda: self.sound_manager.play_effect(self.sound_manager.button_click))
            except AttributeError:
                print("Error: SoundManager is not properly initialized")
        else:
            print("SoundManager is None; skipping sound")

    def paintEvent(self, event):
        if self.path and not self.background_img.isNull():
            painter = QPainter(self)
            painter.drawPixmap(self.rect(), self.background_img.scaled(
                self.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))
            super().paintEvent(event)
        else:
            super().paintEvent(event)

    def update_image(self, new_image_path):
        try:
            new_background_img = QPixmap(new_image_path)
            if not new_background_img.isNull():
                self.background_img = new_background_img
                self.path = new_image_path
                print(f"Successfully loaded image: {new_image_path}")
                self.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: white;
                        border: 3px solid black;
                        border-radius: 5px;
                        padding: 10px;
                        font-family: "Comic Sans MS";
                        font-weight: bold;
                        font-size: 22pt;
                    }
                """)
                self.repaint()
            else:
                print(f"Failed to load image from {new_image_path}: Image is null")
        except Exception as e:
            print(f"An error occurred while updating the image: {e}")

    def flip_image(self):
        if self.path and not self.background_img.isNull():
            transform = QTransform()
            transform.scale(-1, 1)
            flipped_pixmap = self.background_img.transformed(transform, Qt.TransformationMode.SmoothTransformation)
            self.background_img = flipped_pixmap
            self.update()
        else:
            print("No image to flip")

    def setDefaultStyle(self):
        self.setStyleSheet("""
        QPushButton {
            background-color: rgba(255, 120, 0, 240);
            color: white;
            border: 3px solid black;
            border-radius: 5px;
            padding: 10px;
            font-family: "Comic Sans MS";
            font-weight: bold;
            font-size: 22pt;
        }
        QPushButton:hover {
            background-color: rgba(220, 110, 0, 240);
            border: 3px solid black;
        }
        QPushButton:pressed {
            background-color: rgba(180, 70, 0, 220);
        }
        """)

    def setChosenStyle(self):
        self.setStyleSheet("""
        QPushButton {
            background-color: rgba(180, 70, 0, 240);
            color: white;
            border: 3px solid black;
            border-radius: 10px;
            padding: 12px;
            font-family: "Comic Sans MS";
            font-weight: bold;
            font-size: 22pt;
        }
        """)