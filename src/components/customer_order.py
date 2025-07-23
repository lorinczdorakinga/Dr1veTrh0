import random
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtCore import Qt

from src.core.logic.abstract_functions import get_resource_path

class CustomerOrder(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("Initializing customer order...")
        self.setMinimumSize(300, 200)
        self.resize(400, 300)
        
        # Initialize attributes
        self.order = None  # Current selected order (as string)
        self.path = None   # Current selected path or index
        self.previous_paths = []  # Keep track of previous paths to avoid repetition
        
        # Set up layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create container for overlaid images
        self.container = QWidget()
        self.container.setMinimumSize(400, 300)
        
        # Set up speech bubble background
        bubble_image_path = get_resource_path("img/bubble.png")
        self.bubble_label = QLabel(self.container)
        
        try:
            self.bubble_image = QPixmap(bubble_image_path).scaled(
                350, 250, Qt.AspectRatioMode.KeepAspectRatio
            )
            # Set up mirrored bubble image
            self.bubble_image = self.bubble_image.transformed(QTransform().scale(-1, 1))
            self.bubble_label.setPixmap(self.bubble_image)
        except Exception as e:
            print(f"Error loading bubble image: {e}")
            # Fallback in case image doesn't load
            self.bubble_label.setText("Order")
            self.bubble_label.setStyleSheet("background-color: lightblue; border-radius: 15px;")
            
        self.bubble_label.setGeometry(0, 0, 350, 250)
        
        # Set up menu image overlay
        self.menu_image_label = QLabel(self.container)
        
        # Add container to main layout
        layout.addWidget(self.container)
        
        # Initially hide - will show when needed
        self.show()
    
    def randomize_order_image(self, array=None):
        """Select a random image from the provided array, avoiding recent selections"""
        if not array or len(array) == 0:
            return False
            
        try:
            # Convert to list
            available_indices = list(array)
            
            if len(available_indices) <= 0:
                return False
                
            # If we have only one option or very few options, we need to reuse recent selections
            if len(available_indices) == 1:
                self.path = available_indices[0]
            elif len(available_indices) <= len(self.previous_paths):
                # If we have fewer options than our history, just pick any
                self.path = random.choice(available_indices)
            else:
                # Filter out recent selections if possible
                fresh_choices = [idx for idx in available_indices if idx not in self.previous_paths]
                if fresh_choices:
                    self.path = random.choice(fresh_choices)
                else:
                    self.path = random.choice(available_indices)
            
            # Update the selection history, keeping at most 2 previous selections
            self.previous_paths.append(self.path)
            if len(self.previous_paths) > 2:
                self.previous_paths.pop(0)
            
            self.update_menu_image()
            return True
            
        except Exception as e:
            return False
    
    def update_menu_image(self):
        """Update the visual menu image"""
        
        try:
            # Store current order
            self.order = self.path
            
            # Load and scale the image
            menu_image_path = get_resource_path(f"img/menu/")
            menu_image_path += "/" + self.path + ".png"
            self.menu_image = QPixmap(menu_image_path)
            
            if self.menu_image.isNull():
                print(f"Error: Failed to load menu image from {menu_image_path}")
                self.menu_image_label.setText("Image not found")
                return False
                
            self.menu_image = self.menu_image.scaled(
                200, 200, Qt.AspectRatioMode.KeepAspectRatio
            )
            
            # Update the label
            self.menu_image_label.setPixmap(self.menu_image)
            self.menu_image_label.setGeometry(
                int((self.container.width() - self.menu_image.width()) / 2 - 25),
                int((self.container.height() - self.menu_image.height()) / 2 - 25),
                self.menu_image.width(),
                self.menu_image.height()
            )
            return True
            
        except Exception as e:
            print(f"Error updating menu image: {e}")
            self.menu_image_label.setText("Error loading image")
            return False