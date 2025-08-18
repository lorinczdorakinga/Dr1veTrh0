# Modified src/scenes/pause.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPalette, QFont
import sys
from src.components.overlay_button import OverlayButton
from src.components.overlay_label import OverlayLabel
from src.components.game_modes import GameModes
from src.overlays.settings import SettingsPage
from src.core.logic.sound_manager import SoundManager

class Pause(QWidget):
    resume_game_signal = pyqtSignal()
    
    MODE_DISPLAY_NAMES = {
        "default": "Default",
        "reverse": "Reverse",
        "double_trouble": "Double Trouble",
        "speedrun": "Speedrun",
        None: "Default"
    }

    def __init__(self, parent=None, current_game_mode=None, sound_manager=None):
        super().__init__(parent)
        self.parent = parent
        self.current_game_mode = self._determine_initial_mode(current_game_mode)
        self.width = self.parent.width() if self.parent else 1280
        self.height = self.parent.height() if self.parent else 960
        self.sound_manager = sound_manager or SoundManager.get_instance()
        
        self._setup_ui()
        self._init_game_modes_overlay()
        self._create_buttons()
        
        self.game_modes_overlay.set_active_mode(self.current_game_mode)
        self.update_game_mode_label()

    def _determine_initial_mode(self, current_game_mode):
        if current_game_mode is not None:
            return current_game_mode
        if hasattr(self.parent, 'current_game_mode'):
            return self.parent.current_game_mode
        return "default"

    def _setup_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 128))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setSpacing(int(self.height * 0.02))
        self.main_layout.setContentsMargins(
            int(self.width * 0.03), int(self.height * 0.05),
            int(self.width * 0.03), int(self.height * 0.05)
        )

        if self.layout() is None:
            main_container_layout = QVBoxLayout(self)
            main_container_layout.addWidget(self.main_widget)
            main_container_layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(main_container_layout)
        
        # Fetch highscore from AuthHandler or Firebase
        highscore = self.get_highscore()
        highscore_label = OverlayLabel(
            f"Highscore: {highscore}", 
            parent=self
        )
        highscore_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        font = QFont()
        font.setPointSize(int(self.height * 0.03))
        font.setBold(True)
        font.setFamily("Comic Sans MS")
        highscore_label.setStyleSheet("color: white")
        highscore_label.setContentsMargins(50, 0, 0, 0)
        highscore_label.setFont(font)
        self.main_layout.addWidget(highscore_label)

    def get_highscore(self):
        if hasattr(self.parent, 'auth_handler') and self.parent.auth_handler:
            user = self.parent.auth_handler.get_current_user()
            if user:
                highscore = self.parent.auth_handler.fdb.get_user_highscore_by_mode(
                    user['localId'], self.current_game_mode
                )
                return highscore if highscore is not None else 0
        return 0

    def _init_game_modes_overlay(self):
        self.game_modes_overlay = GameModes(self)
        self.game_modes_overlay.setGeometry(
            int(self.width * 0.55),
            int(self.height * 0.25),
            int(self.width * 0.25),
            int(self.height * 0.6)
        )
        self.game_modes_overlay.mode_selected.connect(self.set_game_mode)
        self.game_mode_label = OverlayLabel(
            f"Game Mode: {self.MODE_DISPLAY_NAMES[self.current_game_mode]}", 
            parent=self
        )
        self.game_mode_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        font = QFont()
        font.setPointSize(int(self.height * 0.03))
        self.game_mode_label.setFont(font)

    def _create_buttons(self):
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        buttons_column = QWidget()
        buttons_column_layout = QVBoxLayout(buttons_column)
        buttons_column_layout.setSpacing(int(self.height * 0.02))

        button_definitions = [
            ("Resume Game", self.resume_game),
            ("Play Again", self.play_again_fn),
            ("Game Modes", self.game_modes_overlay_toggle),
            ("Settings", self.settings_overlay_toggle),
            ("Back to Menu", self.back_to_menu_fn),
            ("Quit Game", self.quit_game_fn)
        ]

        button_width = int(self.width * 0.2)
        button_height = int(self.height * 0.08)
        for text, callback in button_definitions:
            button = OverlayButton(text, sound_manager=self.sound_manager)
            button.setFixedSize(button_width, button_height)
            button.clicked.connect(callback)
            buttons_column_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignHCenter)

        buttons_layout.addWidget(buttons_column, alignment=Qt.AlignmentFlag.AlignLeft)
        buttons_layout.addStretch()

        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.game_mode_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(buttons_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addStretch(1)

    def _play_in_game_music(self):
        if self.sound_manager and self.sound_manager.music_enabled:
            self.sound_manager.play_music(self.sound_manager.in_game_music)
        else:
            print("Music disabled, not playing in-game music")

    def set_game_mode(self, mode):
        self.current_game_mode = mode
        self.game_modes_overlay.set_active_mode(mode)
        display_text = self.MODE_DISPLAY_NAMES.get(self.current_game_mode, "Default")
        self.game_mode_label.setText(f"Game Mode: {display_text}")
        
        if self.parent and hasattr(self.parent, 'current_game_mode'):
            self.parent.current_game_mode = self.current_game_mode

        self.play_again_fn()

    def update_game_mode_label(self):
        display_text = self.MODE_DISPLAY_NAMES.get(self.current_game_mode, "Default")
        self.game_mode_label.setText(f"Game Mode: {display_text}")

    def game_modes_overlay_toggle(self):
        if self.game_modes_overlay.isVisible():
            self.game_modes_overlay.hide()
        else:
            self.game_modes_overlay.set_active_mode(self.current_game_mode)
            self.game_modes_overlay.show()
            self.game_modes_overlay.raise_()
            self.game_modes_overlay.move(
                int(self.width * 0.55),
                int(self.height * 0.25)
            )
            self.game_modes_overlay.resize(
                int(self.width * 0.25),
                int(self.height * 0.6)
            )

    def settings_overlay_toggle(self):
        if not hasattr(self, 'settings_overlay'):
            self.settings_overlay = SettingsPage(self, sound_manager=self.sound_manager)
        if self.settings_overlay.isVisible():
            self.settings_overlay.hide()
        else:
            self.settings_overlay.show()
            self.settings_overlay.raise_()

    def resume_game(self):
        if self.parent and hasattr(self.parent, 'toggle_pause'):
            self.parent.toggle_pause(pause_overlay=self)
        else:
            self.hide()
            self.resume_game_signal.emit()

    def play_again_fn(self):
        if self.sound_manager and self.sound_manager.sfx_enabled:
            self.sound_manager.stop_all()
            QTimer.singleShot(0, lambda: self.sound_manager.play_effect(self.sound_manager.game_start))
        if self.sound_manager and self.sound_manager.music_enabled:
            QTimer.singleShot(200, self._play_in_game_music)

        if hasattr(self.parent, 'elaborate_answer'):
            self.parent.elaborate_answer.retry_game_fn()
        self.hide()
        
    def back_to_menu_fn(self):
        from src.scenes.menu.menu_window import Menu  # Local import to avoid circular imports
        self.hide()
        if self.sound_manager:
            self.sound_manager.stop_all()
            if self.sound_manager.music_enabled:
                QTimer.singleShot(200, lambda: self.sound_manager.play_music(self.sound_manager.lobby_music))
        if self.parent:
            self.parent.close()
        self.menu = Menu(sound_manager=self.sound_manager)
        self.menu.showFullScreen()

    def quit_game_fn(self):
        self.hide()
        if self.parent:
            self.parent.close()
        sys.exit()