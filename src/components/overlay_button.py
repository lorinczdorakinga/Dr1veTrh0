from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QFont, QPixmap, QPainter, QTransform
from PyQt6.QtCore import Qt

class OverlayButton(QPushButton):
    def __init__(self, text, parent=None, path=None):
        super().__init__(text, parent)
        self.setMinimumSize(200, 60)
        self.path = path
        
        # Set font
        font = QFont("Comic Sans MS")
        font.setPointSize(14)
        font.setBold(True)
        self.setFont(font)
        
        # Initialize background image
        self.background_img = QPixmap()
        
        if path:
            self.update_image(path)
            # Make the button completely transparent when an image is used
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
            # Apply styling for when no image is used
            self.setDefaultStyle()


    def paintEvent(self, event):
        """Override paintEvent only if we're using a background image"""
        if hasattr(self, 'path') and self.path not in ["", None] and not self.background_img.isNull():
            painter = QPainter(self)
            
            # First draw the background image
            painter.drawPixmap(self.rect(), self.background_img.scaled(
                self.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))
            
            # Then let the parent class draw everything else (text, borders, etc.)
            # We need to call the parent's paintEvent to ensure text is applied
            super().paintEvent(event)
        else:
            # If no image, just use the default paint event
            super().paintEvent(event)

    # def setText(self, text):
    #     self.text = text
    #     self.adjustSize()
    #     self.updateGeometry()
    #     self.update()

    def update_image(self, new_image_path):
        """Update the button's image to a new one"""
        if self.background_img is not None:
            try:
                new_background_img = QPixmap(new_image_path)
                if not new_background_img.isNull():
                    self.background_img = new_background_img
                    self.path = new_image_path
                    print(f"Successfully loaded image: {new_image_path}")
                    
                    # Update style to transparent when setting a new image
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
                    
                    self.repaint()  # Use repaint() instead of update() for immediate refresh
                else:
                    print(f"Failed to load image from {new_image_path}: Image is null")
            except Exception as e:
                print(f"An error occurred while updating the image: {e}")

    def flip_image(self):
        """Flip the image horizontally"""
        if hasattr(self, 'path') and self.path not in ["", None]:
            if not self.background_img.isNull():
                transform = QTransform()
                transform.scale(-1, 1)  # Flip horizontally
                flipped_pixmap = self.background_img.transformed(transform, Qt.TransformationMode.SmoothTransformation)
                self.background_img = flipped_pixmap
                self.update()  # Schedule a repaint
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