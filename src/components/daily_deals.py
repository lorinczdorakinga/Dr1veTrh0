import random
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from src.core.logic.abstract_functions import get_resource_path

class DailyDealsLabel(QLabel):
    def __init__(self, parent=None, current_game_mode=None):
        super().__init__(parent)
        self.setMinimumSize(150, 300)
        self.resize(280, 400)

        self.current_game_mode = current_game_mode
        self.codes = []
        self.images = []
        self.images_in_file = []
        
        # Initialize the layout property
        self.order = None
        
        # Load available menu images
        self.load_available_images()
        
        self.show()

    def decimal_array_to_binary_array(self, decimal_array):
        binary_array = []
        for decimal_value in decimal_array:
            # Convert to binary and remove '0b' prefix
            binary_value = bin(decimal_value)[2:]
            
            # Pad to ensure at least 5 bits (since we'll keep the last 4 bits)
            binary_value = binary_value.zfill(5)
            
            # If longer than 5 bits, take the last 5 bits
            if len(binary_value) > 5:
                binary_value = binary_value[-5:]
                
            binary_array.append(binary_value)
            print(f"Decimal: {decimal_value}, Binary: {binary_value}")
        
        return binary_array
       
    def load_available_images(self):
        """Load all available menu images from the img directory"""
        try:
            self.menu_dir = get_resource_path("img/menu/")
            if os.path.exists(self.menu_dir):
                self.images_in_file = [img.split('.')[0] for img in os.listdir(self.menu_dir) 
                                    if img.endswith(".png")]
            else:
                self.images_in_file = []
        except Exception as e:
            self.images_in_file = []
    
    def randomize_menu_images(self):
        """Select random menu images for the daily deals"""
        try:
            # Reload available images in case they changed
            self.load_available_images()
            
            if not self.images_in_file:
                return
                
            # Check if we have enough images
            total_images = len(self.images_in_file)
            needed_images = 5 
            if total_images < needed_images:
                # Fill with available images, might have duplicates
                self.images = random.choices(self.images_in_file, k=needed_images)
            else:
                # Select 5 random unique images
                self.images = random.sample(self.images_in_file, needed_images)
            
        except Exception as e:
            return

    def randomize_one_handed_codes(self):
        """Generate random codes for one-handed mode (range 1-31)"""
        try:
            self.codes = random.sample(range(1, 32), 5)
        except ValueError as e:
            return

    def randomize_double_trouble_codes(self):
        """Generate random codes for two-handed mode (range 32-1023)"""
        try:
            self.codes = random.sample(range(32, 1024), 5)
            print(f"Two-handed codes: {self.codes}")
        except ValueError as e:
            return

    def randomize_reverse_codes(self):
        """Generate random codes for reverse mode (range 1-10)"""
        try:
            self.codes = random.sample(range(1, 11), 5)  # Changed to range(1, 11) to include 10
            self.codes = self.decimal_array_to_binary_array(self.codes)
        except ValueError as e:
           return
        
    def create_daily_deals_list(self, current_game_mode):
        """Create the daily deals list based on the current game mode"""
        try:
            self.current_game_mode = current_game_mode
            
            # Clear previous data
            self.codes = []
            self.images = []
            
            # Clear any existing layout
            if hasattr(self, 'order') and self.order is not None:
                # Remove all widgets from the existing layout
                while self.order.count():
                    item = self.order.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                    elif item.layout():
                        # Also clear nested layouts
                        while item.layout().count():
                            nested_item = item.layout().takeAt(0)
                            if nested_item.widget():
                                nested_item.widget().deleteLater()
                
                # Delete the existing layout by transferring ownership
                QWidget().setLayout(self.order)
            
            # Generate new menu content
            self.randomize_menu_images()
            
            # Generate appropriate codes based on game mode
            if current_game_mode == "double_trouble":
                self.randomize_double_trouble_codes()
            elif current_game_mode == "reverse":
                self.randomize_reverse_codes()
            else:
                self.randomize_one_handed_codes()
                
            # Ensure we have both images and codes before continuing
            if not self.images or not self.codes:
                return
                
            # Make sure images and codes have the same length
            min_length = min(len(self.images), len(self.codes))
            self.images = self.images[:min_length]
            self.codes = self.codes[:min_length]
            
            # Main vertical layout for all orders
            self.order = QVBoxLayout()
            
            # Create each individual order
            for i in range(len(self.images)):
                # Create horizontal layout for each order (image left, code right)
                order_row = QHBoxLayout()
                
                # Add the menu image
                try:
                    image_path = get_resource_path(f"img/menu/")
                    image_path += "/" + self.images[i] + ".png"
                    menu_image = QPixmap(image_path)
                    
                    if menu_image.isNull():
                        image_label = QLabel("?")
                        image_label.setStyleSheet("background-color: gray;")
                        image_label.setFixedSize(100, 100)
                    else:
                        image_label = QLabel()
                        image_label.setPixmap(menu_image.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
                        
                    order_row.addWidget(image_label)
                except Exception as e:
                    label = QLabel("Error")
                    label.setStyleSheet("background-color: red;")
                    order_row.addWidget(label)

                # Add spacer
                order_row.addStretch(1)
                
                # Add the code
                try:
                    code_label = QLabel(str(self.codes[i]))
                    code_label.setStyleSheet("""
                        font-family: 'Comic Sans MS';
                        font-size: 28pt;
                        font-weight: bold;
                        color: white;
                    """)
                    code_label.setMargin(10)
                    order_row.addWidget(code_label)
                except Exception as e:
                    return                
                # Add this horizontal layout to the main vertical layout
                self.order.addLayout(order_row)
                
                # Add a horizontal separator line if not the last item
                if i < len(self.images) - 1:
                    separator = QFrame()
                    separator.setFrameShape(QFrame.Shape.HLine)
                    separator.setFrameShadow(QFrame.Shadow.Sunken)
                    self.order.addWidget(separator)
            
            # Set the layout and update the widget
            self.setLayout(self.order)
            self.update()
            
        except Exception as e:
            return