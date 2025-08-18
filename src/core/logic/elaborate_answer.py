from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer
from src.overlays.correct_answer import CorrectAnswerOverlay
from src.overlays.incorrect_answer import IncorrectAnswerOverlay
from src.overlays.time_is_up import TimeIsUpOverlay

class ElaborateAnswer(QWidget):
    def __init__(self, parent=None, sound_manager=None):
        super().__init__(parent)
        self._parent_test = parent
        self.sound_manager = sound_manager
        self.is_music_playing = False  # Track if in-game music is playing

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
        self.incorrect_answer_overlay = IncorrectAnswerOverlay(parent=self, true_code=None, current_code=None, highscore=False, sound_manager=self.sound_manager)
        self.time_is_up_overlay = TimeIsUpOverlay(parent=self, highscore=False)
        
        self.correct_answer_overlay.hide()
        self.incorrect_answer_overlay.hide()
        self.time_is_up_overlay.hide()
        
        self.correct_answer_overlay.continue_game.clicked.connect(self.continue_fn)
        self.time_is_up_overlay.play_again.clicked.connect(self.play_again_fn)
        self.incorrect_answer_overlay.retry_game.clicked.connect(self.retry_game_fn)
        self.incorrect_answer_overlay.main_menu.clicked.connect(self.back_to_menu_fn)
        self.time_is_up_overlay.main_menu.clicked.connect(self.back_to_menu_fn)

        # Start in-game music on initialization if not already playing
        self._setup_sounds()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.correct_answer_overlay.resize(self.width(), self.height())
        self.time_is_up_overlay.resize(self.width(), self.height())

    def _play_correct_sound(self):
        if self.sound_manager:
            self.sound_manager.play_effect(self.sound_manager.correct_code)

    def _play_incorrect_sound(self):
        if self.sound_manager:
            self.sound_manager.play_effect(self.sound_manager.bad_code)

    def _play_out_of_time_sound(self):
        if self.sound_manager:
            self.sound_manager.play_effect(self.sound_manager.out_of_time)

    def _play_game_end_music(self):
        if self.sound_manager:
            self.sound_manager.play_music(self.sound_manager.game_end_music)

    def _play_in_game_music(self):
        if self.sound_manager and not self.is_music_playing:
            self.sound_manager.play_music(self.sound_manager.in_game_music)
            self.is_music_playing = True
            print("Started in-game music")

    def _play_game_start_sound(self):
        if self.sound_manager:
            self.sound_manager.play_effect(self.sound_manager.game_start)

    def _setup_sounds(self):
        if self.sound_manager:
            self._play_in_game_music()
            self._play_game_start_sound()

    def update_code_values(self, true_code, current_code, remaining_time, current_game_mode):
        self.true_code = true_code
        self.current_code = current_code
        self.remaining_time = remaining_time
        self.current_game_mode = current_game_mode or "default"

    def shown_code_to_decimal(self, binary_string):
        return binary_string.count('1')

    def binary_array_to_decimal(self, binary_array):
        return int("".join(str(bit) for bit in binary_array), 2)

    def elaborate(self, true_code, current_code, remaining_time, current_game_mode):
        self.update_code_values(true_code, current_code, remaining_time, current_game_mode)
        print(f"Comparing codes - True: {self.true_code}, Current: {self.current_code} - remaining time: {remaining_time}")
        
        [overlay.hide() for overlay in [self.correct_answer_overlay, self.time_is_up_overlay, self.incorrect_answer_overlay]]
        
        [overlay.move(0, 0) for overlay in [self.correct_answer_overlay, self.time_is_up_overlay, self.incorrect_answer_overlay]]
        
        if self._parent_test:
            self._parent_test.toggle_pause()

        if remaining_time <= 0:
            self._parent_test.game_ended = True
            self.highscore = self._parent_test.check_and_update_highscore()
            self.time_is_up_overlay.update_code(self.highscore)
            self.show()
            self.raise_()
            self.time_is_up_overlay.show()
            self.time_is_up_overlay.raise_()

            self.sound_manager.stop_all()
            self.is_music_playing = False  # Reset music tracking
            self._play_game_end_music()
            QTimer.singleShot(100, self._play_out_of_time_sound)
            return
        
        if self.current_game_mode == "reverse":
            self.current_code = self.shown_code_to_decimal(self.current_code)
            self.true_code = self.binary_array_to_decimal(self.true_code)
        
        if self.true_code == self.current_code:
            self._parent_test.update_timer.stop()
            self._parent_test.reset_timer()
            self._parent_test.correct_answers_count += 1
            self._parent_test.update_score_display()

            self.correct_answer_overlay.update_code(self.true_code, current_game_mode)
            
            self.show()
            self.raise_()
            self.correct_answer_overlay.show()
            self.correct_answer_overlay.raise_()
            
            QTimer.singleShot(100, self._play_correct_sound)
        else:
            self._parent_test.game_ended = True
            self.highscore = self._parent_test.check_and_update_highscore()
            self.incorrect_answer_overlay.update_code(self.true_code, self.current_code, current_game_mode, self.highscore)
            
            self.show()
            self.raise_()
            self.incorrect_answer_overlay.show()
            self.incorrect_answer_overlay.raise_()

            self.sound_manager.stop_all()
            self.is_music_playing = False  # Reset music tracking
            QTimer.singleShot(100, self._play_incorrect_sound)
            self._play_game_end_music()

    def _reset_game(self, full_reset=False):
        if full_reset:
            self._parent_test.reset_score_display()
            self._parent_test.correct_answers_count = 0  # Reset score for full reset
        self._parent_test.toggle_pause()
        self._parent_test.reset_timer()

        if full_reset or self._parent_test.correct_answers_count % 5 == 0:
            self._parent_test.update_orders()
        else:
            self._parent_test.randomize_customer_order()
        self._parent_test.had_active_order = False
        
        if self._parent_test.current_scene != "drive_thru":
            self._parent_test.toggle_scenes()
        
        if full_reset:
            self.sound_manager.stop_all()
            self.is_music_playing = False
            self._setup_sounds()  # Restart music only on full reset
        self._parent_test.game_ended = False

    def continue_fn(self):
        self.correct_answer_overlay.hide()
        self.hide()
        self._reset_game(full_reset=False)  # No music reset on continue

    def retry_game_fn(self):
        self.incorrect_answer_overlay.hide()
        self.hide()
        self._reset_game(full_reset=True)  # Full reset includes music restart

    def play_again_fn(self):
        self.time_is_up_overlay.hide()
        self.hide()
        self._reset_game(full_reset=True)  # Full reset includes music restart

    def back_to_menu_fn(self):
        from src.scenes.menu.menu_window import Menu
        
        [overlay.hide() for overlay in [self.time_is_up_overlay, self.incorrect_answer_overlay]]
        self.hide()

        self.sound_manager.stop_all()
        self.is_music_playing = False  # Reset music tracking

        if self._parent_test:
            self._parent_test.toggle_pause()
            self._parent_test.reset_timer()
            self._parent_test.reset_score_display()
            if self._parent_test.current_scene == "kitchen":
                self._parent_test.toggle_scenes()
        self.menu = Menu(sound_manager=self.sound_manager)
        self.menu.showFullScreen()
        self._parent_test.close()