import sys
import pygame
import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QApplication, QHBoxLayout, QLabel,
    QStackedLayout, QFrame, QSizePolicy
)
from PyQt6.QtGui import QIcon, QFont, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QPoint, QTimer

from .pygame_to_pyqt import pygame_to_qwidget

from gui.game_elements.overlay_label import OverlayLabel
from gui.game_elements.overlay_button import OverlayButton
from gui.game_elements.drivethru.daily_deals import DailyDealsLabel
from gui.game_elements.drivethru.customer_order import CustomerOrder

from gui.game_scenes.landing_overlays.pause import Pause
from gui.game_elements.kitchen.elaborate_answer import ElaborateAnswer

from .whole_drivehtru_window import WholeDriveThruWindow
from .kitchen import Kitchen
from gui.game_elements.kitchen.camera import Camera_Widget


class Test(QWidget):
    def __init__(self, current_game_mode=None):
        super().__init__()
        self.setWindowTitle("Game Window")
        
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        self.screen_width = screen_geometry.width()
        self.screen_height = screen_geometry.height()
        self.setMinimumSize(self.screen_width, self.screen_height)
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.current_game_mode = current_game_mode

        # Create layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.current_game_mode = None
        
        # Create stacked layout
        self.stacked_layout = QStackedLayout()
        
        # Create widgets
        DriveThruWidget = pygame_to_qwidget(WholeDriveThruWindow)
        KitchenWidget = pygame_to_qwidget(Kitchen)
        
        screen_rect = QApplication.primaryScreen().geometry()
        width = screen_rect.width()
        height = screen_rect.height()

        self.scene1_widget = DriveThruWidget(width=width, height=height)
        self.scene2_widget = KitchenWidget(width=width, height=height)
        
        # Add widgets to layout
        self.stacked_layout.addWidget(self.scene1_widget)
        self.stacked_layout.addWidget(self.scene2_widget)
        
        self.game_container = QWidget()
        self.game_container.setLayout(self.stacked_layout)
        self.main_layout.addWidget(self.game_container)
        
        # Create pause overlay
        self.pause_game = Pause(self, current_game_mode=self.current_game_mode)
        self.pause_game.resize(width, height)
        self.game_playing = True
        self.pause_start_time = 0
        self.paused_remaining_time = 0

        # Create daily deals
        self.daily_deals = DailyDealsLabel(self, current_game_mode=self.current_game_mode)
        self.daily_deals.move(width - self.daily_deals.width() - 50, 310)

        # Create customer order
        self.customer_order = CustomerOrder(self)
        self.customer_order.move(350, 350)

        # Create camera widget
        self.camera_widget = Camera_Widget(self)

        # Create elaborate answer overlay - IMPORTANT: Ensure this has proper parent reference!
        self.elaborate_answer = ElaborateAnswer(self)
        self.elaborate_answer.resize(width, height)
        
        # Create validate button
        self.validate_code_button = OverlayButton("", self)
        self.validate_code_button.resize(200, 60)
        self.validate_code_button.move(width - self.validate_code_button.width() - 50, height - self.validate_code_button.height() - 300)

        self.validate_code_button.clicked.connect(self.validate_current_code)

        # Create scene change button
        self.change_button = OverlayButton("", self, "/Users/lorinczdora/Documents/Development/GestureAI/img/arrow_right.png")
        self.change_button.clicked.connect(self.toggle_scenes)
        self.change_button.move(width - self.change_button.width() - 50, height - self.change_button.height() - 100)
        self.change_button.resize(150, 100)
        
        # Create timer label
        self.timer_label = OverlayLabel("", self, "/Users/lorinczdora/Documents/Development/GestureAI/img/timer.jpg")
        self.timer_label.move(150, 50)

        # FEATURE 2: Create score counter and label
        self.correct_answers_count = 0
        self.score_label = OverlayLabel(f"Score: {self.correct_answers_count}", self, "/Users/lorinczdora/Documents/Development/GestureAI/img/timer.jpg")
        self.score_label.move(width - self.score_label.width() - 100, 50)
        
        # Initial scene setup
        self.stacked_layout.setCurrentIndex(0)
        self.current_scene = "drive_thru"
        
        # Set up timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_time_display)
        self.update_timer.start(100)  # Update every 100ms
        
        # Track if there was an active order
        self.had_active_order = False
        self.remaining_time = 0
                
        # Initially hide elements that shouldn't be visible
        self.camera_widget.hide()
        self.pause_game.hide()
        self.elaborate_answer.hide()
        self.validate_code_button.hide()
        self.customer_order.hide()

        # Show fullscreen
        self.showFullScreen()
        
        # Ensure elements are on top
        self.change_button.raise_()
        self.timer_label.raise_()
        self.daily_deals.raise_()
        self.customer_order.raise_()
        self.score_label.raise_()

    def set_game_mode(self, mode):
        self.current_game_mode = mode
        self.daily_deals.current_game_mode = mode
        # First reset any previous game state
        if hasattr(self.scene1_widget, 'pygame_app'):
            self.scene1_widget.pygame_app.order_window.reset_timer()
        
        # Initialize game mode specific settings
        self.setup_camera()
        self.initialize_game_mode()

    def initialize_game_mode(self):
        self.daily_deals.create_daily_deals_list(self.current_game_mode)
        self.customer_order.randomize_order_image(self.daily_deals.images)

        if self.current_game_mode == "reverse":
            # Set standard order time for reverse mode
            if hasattr(self.scene1_widget, 'pygame_app'):
                self.scene1_widget.pygame_app.seconds_to_order = 20
                self.scene1_widget.pygame_app.order_window.seconds_to_order = 20
            
            self.validate_code_button.setText("Wink to validate")
            self.validate_code_button.setEnabled(False)
            self.find_decimal_code()
            self.code = self.decimal_code
            self.image_index = 0
            self.decimal_code = 0
            if hasattr(self.camera_widget, 'update_number_of_hands'):
               self.camera_widget.update_number_of_hands(2)
            print("Reverse mode initialized with 20s order time")
            
        else:
            self.find_decimal_code()
            self.code = self.decimal_to_binary_array(self.decimal_code)
            self.image_index = 0
            self.decimal_code = 0

            if self.current_game_mode == "default":
                # Set standard order time for default mode
                if hasattr(self.scene1_widget, 'pygame_app'):
                    self.scene1_widget.pygame_app.seconds_to_order = 20
                    self.scene1_widget.pygame_app.order_window.seconds_to_order = 20
                self.validate_code_button.setText("Validate")
            
            elif self.current_game_mode == "double_trouble":
                # Set standard order time for double handed mode
                if hasattr(self.scene1_widget, 'pygame_app'):
                    self.scene1_widget.pygame_app.seconds_to_order = 60
                    self.scene1_widget.pygame_app.order_window.seconds_to_order = 60
                if hasattr(self.camera_widget, 'update_number_of_hands'):
                    self.camera_widget.update_number_of_hands(2)
                self.update_orders()
                self.validate_code_button.setText("Wink to validate")
                self.validate_code_button.setEnabled(False)
                
            elif self.current_game_mode == "speedrun":
                # Set reduced order time for speedrun mode (10s)
                if hasattr(self.scene1_widget, 'pygame_app'):
                    self.scene1_widget.pygame_app.seconds_to_order = 10
                    self.scene1_widget.pygame_app.order_window.seconds_to_order = 10
                self.validate_code_button.setText("Validate")
                
    def setup_camera(self):
        """Position the camera widget and related UI elements properly on the screen"""
       
        if hasattr(self, 'camera_widget'):
            camera_width = self.camera_widget.width()
            camera_x = self.screen_width - camera_width - 50
            camera_y = (self.screen_height - self.camera_widget.height()) // 2 - 100
            self.camera_widget.move(camera_x, camera_y)
            if self.current_game_mode == "double_trouble" or self.current_game_mode == "reverse":
                self.camera_widget.validation_method = "wink"
            elif self.current_game_mode == "speedrun" or self.current_game_mode == "default":
                self.camera_widget.validation_method = "click"
            self.camera_widget.hide()

    def resizeEvent(self, event):
        width = self.width()
        height = self.height()

        if hasattr(self, 'timer_label'):
            self.timer_label.move(150, 50)
            self.timer_label.raise_()
            self.timer_label.show()

        if hasattr(self, 'score_label'):
            self.score_label.move(width - self.score_label.width() - 100, 50)
            self.score_label.raise_()
            self.score_label.show()

        if hasattr(self, 'change_button'):
            self.change_button.move(
                width - self.change_button.width() - 50,
                height - self.change_button.height() - 100
            )
            self.change_button.raise_()
            self.change_button.show()

        super().resizeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            # Store the current time before toggling pause
            if self.elaborate_answer.isHidden():
                self.last_pause_time = pygame.time.get_ticks()
                self.toggle_pause(pause_overlay=True)
        super().keyPressEvent(event)
        
    def toggle_pause(self, pause_overlay=None):
        """Toggle pause state with proper time preservation"""
        current_time = pygame.time.get_ticks()
        
        if self.game_playing:
            # PAUSING THE GAME
            
            # Store the exact remaining time at pause moment
            if hasattr(self.scene1_widget, 'get_remaining_time'):
                self.paused_remaining_time = self.scene1_widget.get_remaining_time() / 1000
            
            # Display the paused time immediately
            self.timer_label.text = f"Time: {self.paused_remaining_time:.1f}s"
            self.timer_label.update()
            
            # Pause the game state - stop both PyGame widgets
            self.scene1_widget.set_paused(True)
            self.scene2_widget.set_paused(True)
            
            # Stop the UI update timer
            self.update_timer.stop()

            if pause_overlay:            
                self.pause_game.show()
                self.pause_game.raise_()
                
            # Store the pause start time
            self.pause_start_time = current_time
            print(f"Game paused at {self.pause_start_time}ms with {self.paused_remaining_time:.1f}s remaining")
        else:
            # RESUMING THE GAME
            
            # Calculate pause duration
            pause_duration = current_time - self.pause_start_time
            print(f"Game resumed after {pause_duration}ms pause with {self.paused_remaining_time:.1f}s remaining")
            
            # Force update the timer in DriveThruGame to match our paused time
            if hasattr(self.scene1_widget, 'pygame_app') and hasattr(self.scene1_widget.pygame_app, 'order_window'):
                # Calculate what the order_start_time should be to give us the paused_remaining_time
                order_window = self.scene1_widget.pygame_app.order_window
                seconds_to_order = order_window.seconds_to_order
                
                # Set order_start_time to a value that will result in our paused_remaining_time
                # current_time - (seconds_to_order - paused_remaining_time) * 1000
                new_order_start_time = current_time - (seconds_to_order - self.paused_remaining_time) * 1000
                
                if order_window.middle_reached:
                    order_window.order_start_time = int(new_order_start_time)
                    print(f"Reset order_start_time to {order_window.order_start_time} to preserve {self.paused_remaining_time:.1f}s")
            
            # Resume the game state
            self.scene1_widget.set_paused(False)
            self.scene2_widget.set_paused(False)
            
            # Restart the UI update timer
            self.update_timer.start()
            
            # Hide the pause overlay
            self.pause_game.hide()
        
        # Toggle the game_playing state
        self.game_playing = not self.game_playing
    def back_to_menu(self):
        from gui.menu_window import Menu
        self.menu = Menu()
        self.menu.show()
        self.close()
    def toggle_scenes(self):
        self.elaborate_answer.hide()
        
        if self.current_scene == "drive_thru":
            # Switch to kitchen scene
            self.stacked_layout.setCurrentIndex(1)
            self.current_scene = "kitchen"
            
            if self.remaining_time > 0.00:
                if self.current_game_mode == "double_trouble":
                    self.validate_code_button.setText("Wink to Validate")
                else: 
                    self.validate_code_button.setText("Validate Code")
                    
                self.validate_code_button.show()
                self.validate_code_button.raise_()
                self.had_active_order = True  # Track active order
            else:
                self.validate_code_button.hide()
                
            self.change_button.flip_image()
            self.camera_widget.show()
            self.camera_widget.raise_()
            self.daily_deals.hide()
            self.customer_order.hide()
            
        else:
            # Switch to drive-thru scene
            self.stacked_layout.setCurrentIndex(0)
            self.current_scene = "drive_thru"
            self.change_button.flip_image()
            self.camera_widget.hide()
            
            # Update code if time is up AND we had an active order, or if we got the answer correct
            if (self.remaining_time <= 0.00 and self.had_active_order) or \
            (self.elaborate_answer.isVisible() and hasattr(self.elaborate_answer, 'correct_answer_overlay') and
                self.elaborate_answer.correct_answer_overlay.isVisible()):
                
                if self.correct_answers_count % 5 == 0 and self.correct_answers_count > 1:
                    if self.current_game_mode is not None:
                        print(self.current_game_mode)
                        self.update_orders()
                    else:
                        self.randomize_customer_order()
                        
                    self.had_active_order = False  # Reset the flag
                else:
                    # Don't show customer_order here - let update_time_display handle it
                    self.had_active_order = False
                    
            else:
                # self.randomize_customer_order()
                self.had_active_order = False
                
            # Always ensure customer_order is hidden initially in drive-thru scene
            if self.remaining_time <= 0.00:
                self.customer_order.hide()
                
            self.daily_deals.show()
            self.daily_deals.raise_()

    def update_orders(self):
        """Update food orders, daily deals and corresponding code"""
        print("update_orders called" + str(self.daily_deals))
        if self.daily_deals is not None:
            self.daily_deals.create_daily_deals_list(self.current_game_mode)
            self.randomize_customer_order()
            print("Orders updated!")

    def randomize_customer_order(self):
        self.customer_order.randomize_order_image(self.daily_deals.images)
        self.find_decimal_code()
        if self.current_game_mode == "reverse":
            self.code = self.decimal_code
        else:  # default, double_trouble, speedrun modes
            self.code = self.decimal_to_binary_array(int(self.decimal_code))

        self.customer_order.update_menu_image()
        self.camera_widget.update_true_code(self.code)
        
    def update_time_display(self):
        """Update time display with pause handling"""
        if not self.game_playing:
            self.timer_label.text = f"Time: {self.paused_remaining_time:.1f}s"
            self.timer_label.update()
            return
            
        if hasattr(self.scene1_widget, 'get_remaining_time'):
            previous_time = self.remaining_time if hasattr(self, 'remaining_time') else 0
            self.remaining_time = self.scene1_widget.get_remaining_time() / 1000
            self.timer_label.text = f"Time: {self.remaining_time:.1f}s"
            self.timer_label.update()
            
            # Track if we had an active order (time > 0)
            if previous_time > 0.00:
                self.had_active_order = True
                
            if self.current_scene == "drive_thru":
                if self.remaining_time > 0.00:
                    # Show customer_order only when time is ticking
                    self.customer_order.show()
                    self.customer_order.raise_()
                    self.validate_code_button.hide()
                elif self.remaining_time <= 0:
                    # Hide customer_order when time is up
                    self.customer_order.hide()
                    # Only validate and update if there was an active order
                    if self.had_active_order:
                        self.validate_current_code()
                        
            elif self.current_scene == "kitchen":
                if self.remaining_time <= 0.00 and self.validate_code_button.isVisible():
                    self.validate_code_button.hide()
                    if self.had_active_order:
                        self.validate_current_code()
                elif self.remaining_time > 0 and not self.elaborate_answer.isVisible():
                        self.validate_code_button.show()
                        self.validate_code_button.raise_()
    def update_score_display(self):
        """Update the score display with the current count of correct answers"""
        self.score_label.text = f"Score: {self.correct_answers_count}"
        self.score_label.update()
        print(f"Score updated: {self.correct_answers_count} correct answers")
    def reset_timer(self):
        """Reset the timer to 0"""
        if hasattr(self.scene1_widget, 'pygame_app') and hasattr(self.scene1_widget.pygame_app, 'order_window'):
            # Reset at the lowest level - the DriveThruGame object
            self.scene1_widget.pygame_app.order_window.reset_timer()
            # Also reset the middle_reached flag to false
            self.scene1_widget.pygame_app.order_window.middle_reached = False
            # Reset the time tracking variables
            self.scene1_widget.pygame_app.order_window.order_start_time = pygame.time.get_ticks()
            # Force the x position to move the car out
            self.scene1_widget.pygame_app.order_window.x -= self.scene1_widget.pygame_app.order_window.speed
            
        # Update the remaining time display
        self.remaining_time = 0
        self.timer_label.text = f"Time: {self.remaining_time:.1f}s"
        self.timer_label.update()
        print("Timer reset to 0 - with improved method that resets DriveThruGame state")
        
        # Since time is now 0, handle UI updates
        if self.current_scene == "drive_thru" and self.customer_order.isVisible():
            self.customer_order.hide()
        elif self.current_scene == "kitchen" and self.validate_code_button.isVisible():
            self.validate_code_button.hide()
    def reset_score_display(self):
        """Reset the score display to 0"""
        self.correct_answers_count = 0
        self.score_label.text = f"Score: {self.correct_answers_count}"
        self.score_label.update()
        print("Score reset to 0")

    def find_decimal_code(self):
        for i in range(len(self.daily_deals.images)):
            if str(self.daily_deals.images[i]) == self.customer_order.order:
                self.image_index = i
                print(self.image_index)
                print(self.daily_deals.codes)
                for j in range(len(self.daily_deals.codes)):
                    if j == self.image_index:
                        self.decimal_code = self.daily_deals.codes[j]
                        print("@@@@@@@@@@@@@@DECIMAL CODE: " + str(self.decimal_code))

    def decimal_to_binary_array(self, decimal):
        """Convert a decimal number to a binary array of size 5"""
        binary = bin(decimal)[2:].zfill(5)
        binary_array = [int(bit) for bit in binary]
        # reversed_array = binary_array[::-1]
        return binary_array
    
    def validate_current_code(self):
        """Get the current code at button click time and validate it"""
        # Don't allow multiple validation attempts while elaborate_answer is shown
        if self.elaborate_answer.isVisible():
            return
        
        self.had_active_order = False
        self.validate_code_button.hide()
        
        if self.correct_answers_count % 5 == 0 and self.correct_answers_count > 1:
            self.update_orders()
            print(f"Updating orders after {self.correct_answers_count} correct answers")
        
        current_code = self.camera_widget.get_currently_shown_code()
        
        # Format the true code to match the current code format
        formatted_true_code = ""
        if isinstance(self.code, list):
            # Convert list of integers to string format
            formatted_true_code = ''.join(map(str, self.code))
        else:
            # If it's already a string or other format, convert to string
            formatted_true_code = str(self.code)
        
        print(f"CURRENT CODE: {current_code} TRUE CODE: {formatted_true_code} REMAINING TIME: {self.remaining_time}")
        
        self.elaborate_answer.elaborate(
            true_code=formatted_true_code, 
            current_code=current_code, 
            remaining_time=self.remaining_time, 
            current_game_mode=self.current_game_mode
        )