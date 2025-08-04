import sys
import time
import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QApplication, QHBoxLayout, QLabel,
    QStackedLayout, QFrame, QSizePolicy
)
from PyQt6.QtGui import QIcon, QFont, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QPoint, QTimer, QTime

from src.core.logic.abstract_functions import get_resource_path
from src.components.overlay_label import OverlayLabel
from src.components.overlay_button import OverlayButton
from src.components.daily_deals import DailyDealsLabel
from src.components.customer_order import CustomerOrder
from src.overlays.pause import Pause
from src.core.logic.elaborate_answer import ElaborateAnswer
from .drivethru.whole_drivehtru_window import WholeDriveThruWindow
from .kitchen.kitchen import Kitchen
from src.components.camera import Camera_Widget

class Test(QWidget):
    def __init__(self, auth_handler, current_game_mode=None):
        super().__init__()
        self.auth_handler = auth_handler
        self.current_game_mode = current_game_mode
        self.highscore = self.get_user_highscore()
        self._setup_screen()
        self._initialize_ui()
        self._setup_overlays()
        self._configure_initial_state()
        self.showFullScreen()

    def _setup_screen(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        self.screen_width = screen_geometry.width()
        self.screen_height = screen_geometry.height()
        self.setMinimumSize(self.screen_width, self.screen_height)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def _initialize_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.stacked_layout = QStackedLayout()
        self._add_scenes()

        self.game_container = QWidget()
        self.game_container.setLayout(self.stacked_layout)
        self.main_layout.addWidget(self.game_container)

    def _add_scenes(self):
        self.scene1_widget = WholeDriveThruWindow(width=self.screen_width, height=self.screen_height)
        self.scene2_widget = Kitchen(width=self.screen_width, height=self.screen_height)
        self.stacked_layout.addWidget(self.scene1_widget)
        self.stacked_layout.addWidget(self.scene2_widget)
        self.current_scene = "drive_thru"
        self.stacked_layout.setCurrentIndex(0)

    def _setup_overlays(self):
        self.daily_deals = DailyDealsLabel(self, current_game_mode=self.current_game_mode)
        self.daily_deals.move(self.screen_width - self.daily_deals.width() - 50, 310)

        self.customer_order = CustomerOrder(self)
        self.customer_order.move(350, 350)

        self.camera_widget = Camera_Widget(self)
        self.elaborate_answer = ElaborateAnswer(self)
        self.elaborate_answer.resize(self.screen_width, self.screen_height)

        self.validate_code_button = OverlayButton("", self)
        self.validate_code_button.resize(200, 60)
        self.validate_code_button.move(self.screen_width - 200 - 50, self.screen_height - 360)
        self.validate_code_button.clicked.connect(self.validate_current_code)

        self.change_button = OverlayButton("", self, get_resource_path("img/arrow_right.png"))
        self.change_button.clicked.connect(self.toggle_scenes)
        self.change_button.move(self.screen_width - 150 - 50, self.screen_height - 200)
        self.change_button.resize(150, 100)

        self.timer_label = OverlayLabel("", self, get_resource_path("img/timer.jpg"))
        self.timer_label.move(150, 50)

        self.correct_answers_count = 0
        self.score_label = OverlayLabel(f"Score: {self.correct_answers_count}", self, get_resource_path("img/timer.jpg"))
        self.score_label.move(self.screen_width - self.score_label.width() - 100, 50)

        self.game_playing = True
        self.pause_game = Pause(self)
        self.pause_game.resize(self.screen_width, self.screen_height)
        self.pause_game.hide()

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_time_display)
        self.update_timer.start(1000 // 60)

        self.game_start_time = QTime.currentTime()

    def _configure_initial_state(self):
        self.had_active_order = False
        self.remaining_time = 0
        self.camera_widget.hide()
        self.elaborate_answer.hide()
        self.validate_code_button.hide()
        self.customer_order.hide()
        self._raise_elements()

    def _raise_elements(self):
        for widget in [self.change_button, self.timer_label, self.daily_deals, self.customer_order, self.score_label]:
            widget.raise_()

    def set_game_mode(self, mode):
        self.current_game_mode = mode
        self.daily_deals.current_game_mode = mode
        self.scene1_widget.order_window.reset_timer()
        self.setup_camera()
        self.initialize_game_mode()

    def initialize_game_mode(self):
        self.daily_deals.create_daily_deals_list(self.current_game_mode)
        self.customer_order.randomize_order_image(self.daily_deals.images)
        self.find_decimal_code()
        self._configure_mode_settings()

    def _configure_mode_settings(self):
        mode_configs = {
            "reverse": {"time": 20, "button_text": "Wink to validate", "hands": 2, "enabled": False},
            "default": {"time": 20, "button_text": "Validate", "hands": 1, "enabled": True},
            "double_trouble": {"time": 60, "button_text": "Wink to validate", "hands": 2, "enabled": False},
            "speedrun": {"time": 10, "button_text": "Validate", "hands": 1, "enabled": True}
        }
        config = mode_configs.get(self.current_game_mode, mode_configs["default"])

        self._set_order_time(config["time"])
        self.validate_code_button.setText(config["button_text"])
        self.validate_code_button.setEnabled(config["enabled"])
        if config["hands"] > 1 and hasattr(self.camera_widget, 'update_number_of_hands'):
            self.camera_widget.update_number_of_hands(config["hands"])

        self.code = self.decimal_code if self.current_game_mode == "reverse" else self.decimal_to_binary_array(self.decimal_code)
        self.image_index = 0
        self.dec_imal_code = 0
        if self.current_game_mode == "double_trouble":
            self.update_orders()
        print(f"{self.current_game_mode.capitalize()} mode initialized with {config['time']}s order time")

    def _set_order_time(self, seconds):
        self.scene1_widget.seconds_to_order = seconds
        self.scene1_widget.order_start_time = QTime.currentTime()

    def setup_camera(self):
        camera_width = self.camera_widget.width()
        self.camera_widget.move(self.screen_width - camera_width - 50, (self.screen_height - self.camera_widget.height()) // 2 - 100)
        self.camera_widget.validation_method = "wink" if self.current_game_mode in ["double_trouble", "reverse"] else "click"
        self.camera_widget.hide()

    def resizeEvent(self, event):
        self.timer_label.move(150, 50)
        self.score_label.move(self.width() - self.score_label.width() - 100, 50)
        self.change_button.move(self.width() - 150 - 50, self.height() - 200)
        super().resizeEvent(event)
        self._raise_elements()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self.elaborate_answer.isHidden():
            self.last_pause_time = QTime.currentTime()
            self.toggle_pause(pause_overlay=True)
        super().keyPressEvent(event)

    def toggle_pause(self, pause_overlay=None):
        current_time = QTime.currentTime()
        if self.game_playing:
            if hasattr(self.scene1_widget, 'get_remaining_time'):
                self.paused_remaining_time = self.scene1_widget.get_remaining_time() / 1000
            self.timer_label.setText(f"Time: {self.paused_remaining_time:.1f}s")
            self.timer_label.update()
            self.scene1_widget.set_paused(True)
            self.scene2_widget.set_paused(True)
            self.update_timer.stop()
            self.scene1_widget.lower()
            self.scene2_widget.lower()
            if pause_overlay:
                self.pause_game.show()
                self.pause_game.raise_()
            self.score_label.raise_()
            self.timer_label.raise_()
            self.pause_start_time = current_time
            print(f"Game paused at {current_time.toString('hh:mm:ss.zzz')} with {self.paused_remaining_time:.1f}s remaining")
        else:
            pause_duration = self.pause_start_time.msecsTo(current_time)
            print(f"Game resumed after {pause_duration}ms pause with {self.paused_remaining_time:.1f}s remaining")
            order_window = self.scene1_widget.order_window
            if order_window.middle_reached:
                new_order_start_time = QTime.currentTime().addMSecs(-int((order_window.seconds_to_order - self.paused_remaining_time) * 1000))
                order_window.order_start_time = new_order_start_time
            self.scene1_widget.set_paused(False)
            self.scene2_widget.set_paused(False)
            self.update_timer.start()
            self.scene1_widget.raise_()
            self.scene2_widget.raise_()
            self.pause_game.hide()
        self.game_playing = not self.game_playing

    def back_to_menu(self):
        from src.scenes.menu.menu_window import Menu
        self.menu = Menu()
        self.menu.show()
        self.close()

    def toggle_scenes(self):
        self.elaborate_answer.hide()
        if self.current_scene == "drive_thru":
            self.stacked_layout.setCurrentIndex(1)
            self.current_scene = "kitchen"
            self._update_kitchen_ui()
            self.change_button.flip_image()
        else:
            self.stacked_layout.setCurrentIndex(0)
            self.current_scene = "drive_thru"
            self._update_drive_thru_ui()
            self.change_button.flip_image()

    def _update_kitchen_ui(self):
        if self.remaining_time > 0:
            self.validate_code_button.setText("Wink to Validate" if self.current_game_mode == "double_trouble" else "Validate")
            self.validate_code_button.show()
            self.had_active_order = True
        else:
            self.validate_code_button.hide()
        self.camera_widget.show()
        self.daily_deals.hide()
        self.customer_order.hide()

    def _update_drive_thru_ui(self):
        self.camera_widget.hide()
        if (self.remaining_time <= 0 and self.had_active_order) or \
           (self.elaborate_answer.isVisible() and hasattr(self.elaborate_answer, 'correct_answer_overlay') and
            self.elaborate_answer.correct_answer_overlay.isVisible()):
            if self.correct_answers_count % 5 == 0 and self.correct_answers_count > 1 and self.current_game_mode:
                self.update_orders()
                self.had_active_order = False
            else:
                self.had_active_order = False
        if self.remaining_time <= 0:
            self.customer_order.hide()
        self.daily_deals.show()

    def update_orders(self):
        if self.daily_deals:
            self.daily_deals.create_daily_deals_list(self.current_game_mode)
            self.randomize_customer_order()
            print("Orders updated!")

    def randomize_customer_order(self):
        self.customer_order.randomize_order_image(self.daily_deals.images)
        self.find_decimal_code()
        self.code = self.decimal_code if self.current_game_mode == "reverse" else self.decimal_to_binary_array(self.decimal_code)
        self.customer_order.update_menu_image()
        self.camera_widget.update_true_code(self.code)

    def update_time_display(self):
        if not self.game_playing:
            self.timer_label.text = f"Time: {self.paused_remaining_time:.1f}s"
            self.timer_label.update()
            return
        if hasattr(self.scene1_widget, 'get_remaining_time'):
            previous_time = self.remaining_time
            self.remaining_time = self.scene1_widget.get_remaining_time() / 1000
            self.timer_label.text = f"Time: {self.remaining_time:.1f}s"
            self.timer_label.update()
            if previous_time > 0:
                self.had_active_order = True
            if self.remaining_time <= 0 and not self.elaborate_answer.isVisible() and previous_time > 0:
                self.validate_current_code()
            self._update_scene_ui()

    def _update_scene_ui(self):
        if self.current_scene == "drive_thru":
            self.customer_order.setVisible(self.remaining_time > 0)
            self.validate_code_button.hide()
        elif self.current_scene == "kitchen":
            if self.remaining_time > 0 and not self.elaborate_answer.isVisible():
                self.validate_code_button.show()
            else:
                self.validate_code_button.hide()

    def update_score_display(self):
        self.score_label.text = f"Score: {self.correct_answers_count}"
        self.score_label.update()
        print(f"Score updated: {self.correct_answers_count} correct answers")

    def reset_timer(self):
        order_window = self.scene1_widget.order_window
        order_window.reset_timer()
        order_window.middle_reached = False
        order_window.order_start_time = QTime.currentTime()
        order_window.x -= order_window.speed
        self.remaining_time = 0
        self.timer_label.text = f"Time: {self.remaining_time:.1f}s"
        self.timer_label.update()
        print("Timer reset to 0")
        self._update_scene_ui()

    def reset_score_display(self):
        self.correct_answers_count = 0
        self.update_score_display()

    def find_decimal_code(self):
        self.decimal_code = 0
        for i, image in enumerate(self.daily_deals.images):
            if str(image) == self.customer_order.order:
                self.image_index = i
                self.decimal_code = self.daily_deals.codes[i]
                print(f"@@@@@@@@@@@@@@DECIMAL CODE: {self.decimal_code}")
                break
        else:
            print("Warning: No matching image found for customer order.")

    def decimal_to_binary_array(self, decimal):
        binary = bin(decimal)[2:].zfill(5)
        return [int(bit) for bit in binary]

    def validate_current_code(self):
        if self.elaborate_answer.isVisible():
            return
        self.had_active_order = False
        if self.current_scene == "kitchen":
            current_code = self.camera_widget.get_currently_shown_code()
        else:
            current_code = None
        formatted_true_code = ''.join(map(str, self.code)) if isinstance(self.code, list) else str(self.code)
        print(f"CURRENT CODE: {current_code} TRUE CODE: {formatted_true_code} REMAINING TIME: {self.remaining_time}")
        self.elaborate_answer.elaborate(
            true_code=formatted_true_code,
            current_code=current_code,
            remaining_time=self.remaining_time,
            current_game_mode=self.current_game_mode
        )

    def get_user_highscore(self):
        user = self.auth_handler.get_current_user()
        if user:
            uid = user.get('localId') or user.get('uid')
            if uid:
                return self.auth_handler.fdb.get_user_highscore_by_mode(uid, self.current_game_mode)
        return 999

    def check_and_update_highscore(self):
        if not self.auth_handler.current_user:
            return False
        current_score = self.correct_answers_count
        game_mode = self.current_game_mode
        highscore_key = f'{game_mode}_mode_highscore'
        print(highscore_key)
        current_highscore = self.auth_handler.current_user.get(highscore_key, 0)
        if current_score > current_highscore:
            uid = self.auth_handler.current_user['localId']
            email = self.auth_handler.current_user['email']
            self.auth_handler.fdb.update_highscore(uid, game_mode, current_score, email)
            self.auth_handler.current_user[highscore_key] = current_score
            return True
        return False

    