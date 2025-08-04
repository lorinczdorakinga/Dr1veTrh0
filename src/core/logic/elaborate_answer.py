import sys
from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtGui import QPainter, QColor, QPalette
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QHBoxLayout, QStackedLayout, QFrame
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import QPoint, QTimer

from src.overlays.correct_answer import CorrectAnswerOverlay
from src.overlays.incorrect_answer import IncorrectAnswerOverlay
from src.overlays.time_is_up import TimeIsUpOverlay
from src.components.overlay_label import OverlayLabel

class ElaborateAnswer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent_test = parent
        
        self.true_code = None
        self.current_code = None
        self.remaining_time = None
        self.current_game_mode = None
        self.highscore = False
        self.setVisible(False)
        
        if parent:
            self.resize(parent.screen_width, parent.screen_height)
        else:
            self.resize(1280, 960)
            
        self.correct_answer_overlay = CorrectAnswerOverlay(parent=self, code=None)
        self.incorrect_answer_overlay = IncorrectAnswerOverlay(parent=self, true_code=None, current_code=None, highscore=False)
        self.time_is_up_overlay = TimeIsUpOverlay(parent=self, highscore=False)
        
        self.correct_answer_overlay.hide()
        self.incorrect_answer_overlay.hide()
        self.time_is_up_overlay.hide()
        
        if hasattr(self.correct_answer_overlay, 'continue_game'):
            self.correct_answer_overlay.continue_game.clicked.connect(self.continue_fn)
        
        if hasattr(self.time_is_up_overlay, 'play_again'):
            self.time_is_up_overlay.play_again.clicked.connect(self.play_again_fn)

        if hasattr(self.incorrect_answer_overlay, 'retry_game'):
            self.incorrect_answer_overlay.retry_game.clicked.connect(self.retry_game_fn)

        if hasattr(self.incorrect_answer_overlay, 'main_menu') and hasattr(self.time_is_up_overlay, 'main_menu'):
            self.incorrect_answer_overlay.main_menu.clicked.connect(self.back_to_menu_fn)
            self.time_is_up_overlay.main_menu.clicked.connect(self.back_to_menu_fn)
            
        print(f"ElaborateAnswer initialized with parent: {self._parent_test}")
        print(f"Parent has update_orders: {hasattr(self._parent_test, 'update_orders') if self._parent_test else False}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.correct_answer_overlay.resize(self.width(), self.height())
        self.time_is_up_overlay.resize(self.width(), self.height())

    def update_code_values(self, true_code, current_code, remaining_time, current_game_mode):
        self.true_code = true_code
        self.current_code = current_code
        self.remaining_time = remaining_time
        if current_game_mode is None:
            self.current_game_mode = "default"
        else:
            self.current_game_mode = current_game_mode

    def shown_code_to_decimal(self, binary_string):
        decimal_number = binary_string.count('1')
        return decimal_number
    
    def binary_array_to_decimal(self, binary_array):
        decimal = int("".join(str(bit) for bit in binary_array), 2)
        return decimal

    def elaborate(self, true_code, current_code, remaining_time, current_game_mode):
        self.update_code_values(true_code, current_code, remaining_time, current_game_mode)
        print(f"Comparing codes - True: {self.true_code}, Current: {self.current_code} - remaining time: {remaining_time}")
        
        self.correct_answer_overlay.hide()
        self.time_is_up_overlay.hide()
        self.incorrect_answer_overlay.hide()
        
        self.correct_answer_overlay.move(0, 0)
        self.time_is_up_overlay.move(0, 0)
        self.incorrect_answer_overlay.move(0, 0)
        
        if self._parent_test and hasattr(self._parent_test, 'toggle_pause'):
            self._parent_test.toggle_pause()

        if remaining_time <= 0:
            self._parent_test.check_and_update_highscore()
            self.show()
            self.raise_()
            self.time_is_up_overlay.show()
            self.time_is_up_overlay.raise_()
            return
        
        if self._parent_test.current_game_mode == "reverse":
            self.current_code = self.shown_code_to_decimal(self.current_code)
            self.true_code = self.binary_array_to_decimal(self.true_code)
        
        if self.true_code == self.current_code:
            if self._parent_test and hasattr(self._parent_test, 'update_timer'):
                self._parent_test.update_timer.stop()
            if hasattr(self._parent_test, 'reset_timer'):
                self._parent_test.reset_timer()
            if self._parent_test and hasattr(self._parent_test, 'correct_answers_count'):
                self._parent_test.correct_answers_count += 1
                if hasattr(self._parent_test, 'update_score_display'):
                    self._parent_test.update_score_display()

            if hasattr(self.correct_answer_overlay, 'update_code'):
                self.correct_answer_overlay.update_code(self.true_code, current_game_mode)
                
            self.show()
            self.raise_()
            self.correct_answer_overlay.show()
            self.correct_answer_overlay.raise_()
        else:
            self.highscore = self._parent_test.check_and_update_highscore()
            if hasattr(self.incorrect_answer_overlay, 'update_code'):
                self.incorrect_answer_overlay.update_code(self.true_code, self.current_code, current_game_mode, self.highscore)
                
            self.show()
            self.raise_()
            self.incorrect_answer_overlay.show()
            self.incorrect_answer_overlay.raise_()

    def continue_fn(self):
        self.correct_answer_overlay.hide()
        self.hide()
        
        if self._parent_test:
            if self._parent_test.current_scene != "drive_thru":
                self._parent_test.toggle_scenes()
        
            if hasattr(self._parent_test, 'toggle_pause'):
                self._parent_test.toggle_pause()
            
            if hasattr(self._parent_test, 'update_orders') and hasattr(self._parent_test, 'correct_answers_count'):
                print("Calling parent's update_orders method via explicit reference")
                if self._parent_test.correct_answers_count > 1 and self._parent_test.correct_answers_count % 5 == 0:
                    self._parent_test.update_orders()
                    self._parent_test.had_active_order = False
                else: 
                    self._parent_test.randomize_customer_order()
                    self._parent_test.had_active_order = False
        
    def retry_game_fn(self):
        self.incorrect_answer_overlay.hide()
        self.hide()
        
        if self._parent_test:
            if hasattr(self._parent_test, 'reset_score_display'):
                self._parent_test.reset_score_display()
            if hasattr(self._parent_test, 'toggle_pause'):
                self._parent_test.toggle_pause()   
            if hasattr(self._parent_test, 'reset_timer'):
                self._parent_test.reset_timer()

            if hasattr(self._parent_test, 'set_game_mode'):
                self._parent_test.set_game_mode(self._parent_test.current_game_mode)
            if hasattr(self._parent_test, 'update_orders'):
                print("Calling parent's update_orders method via explicit reference")
                self._parent_test.update_orders()
                self._parent_test.had_active_order = False
            if self._parent_test and hasattr(self._parent_test, 'toggle_scenes'):
                print("Calling parent's toggle_scenes method via explicit reference")
                if self._parent_test.current_scene == "kitchen":
                    self._parent_test.toggle_scenes()

    def play_again_fn(self):
        self.time_is_up_overlay.hide()
        self.hide()
        
        if self._parent_test:
            if hasattr(self._parent_test, 'toggle_pause'):
                self._parent_test.toggle_pause()
            
            if hasattr(self._parent_test, 'reset_timer'):
                self._parent_test.reset_timer()
                print("Timer reset after correct answer")
            if hasattr(self._parent_test, 'update_orders'):
                print("Calling parent's update_orders method via explicit reference")
                self._parent_test.update_orders()
            if hasattr(self._parent_test, 'toggle_scenes'):
                print("Calling parent's toggle_scenes method via explicit reference")
                if self._parent_test.current_scene == "kitchen":
                    self._parent_test.toggle_scenes()
            if hasattr(self._parent_test, 'update_score_display'):
                print("Calling parent's update_score_display method via explicit reference")
                self._parent_test.reset_score_display()
    
    def back_to_menu_fn(self):
        from src.scenes.menu.menu_window import Menu
        
        self.time_is_up_overlay.hide()
        self.incorrect_answer_overlay.hide()
        self.hide()

        if self._parent_test:
            if hasattr(self._parent_test, 'toggle_pause'):
                self._parent_test.toggle_pause()
            if hasattr(self._parent_test, 'reset_timer'):
                self._parent_test.reset_timer()
                print("Timer reset after correct answer")
            if hasattr(self._parent_test, 'reset_score_display'):
                self._parent_test.reset_score_display()
            if hasattr(self._parent_test, 'toggle_scenes'):
                print("Calling parent's toggle_scenes method via explicit reference")
                if self._parent_test.current_scene == "kitchen":
                    self._parent_test.toggle_scenes()
        self.menu = Menu()
        self.menu.showFullScreen()
        self._parent_test.close()