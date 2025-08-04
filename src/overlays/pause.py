from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette, QFont
import sys

from src.components.overlay_button import OverlayButton
from src.components.overlay_label import OverlayLabel
from src.overlays.game_modes import GameModes

class Pause(QWidget):
    resume_game_signal = pyqtSignal()
    
    # Game mode display mapping
    MODE_DISPLAY_NAMES = {
        "default": "Default",
        "reverse": "Reverse",
        "double_trouble": "Double Trouble",
        "speedrun": "Speedrun",
        None: "Default"
    }

    def __init__(self, parent=None, current_game_mode=None):
        super().__init__(parent)
        self.parent = parent
        self.current_game_mode = self._determine_initial_mode(current_game_mode)
        self.width = self.parent.width() if self.parent else 1280
        self.height = self.parent.height() if self.parent else 960
        
        self._setup_ui()
        self._init_game_modes_overlay()
        self._create_buttons()
        
        self.game_modes_overlay.set_active_mode(self.current_game_mode)
        self.update_game_mode_label()

    def _determine_initial_mode(self, current_game_mode):
        """Determine the initial game mode based on parameters and parent"""
        if current_game_mode is not None:
            return current_game_mode
        if hasattr(self.parent, 'current_game_mode'):
            return self.parent.current_game_mode
        return "default"

    def _setup_ui(self):
        """Initialize the basic UI components"""
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 128))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setSpacing(int(self.height * 0.02))  # 2% of height
        self.main_layout.setContentsMargins(
            int(self.width * 0.03), int(self.height * 0.05),
            int(self.width * 0.03), int(self.height * 0.05)
        )  # Responsive margins

        # Only set layout if not already set
        if self.layout() is None:
            main_container_layout = QVBoxLayout(self)
            main_container_layout.addWidget(self.main_widget)
            main_container_layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(main_container_layout)
        
        highscore_label = OverlayLabel(
            f"Highscore: {self.parent.highscore}", 
            parent=self
        )
        highscore_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        font = QFont()
        font.setPointSize(int(self.height * 0.03))  # 3% of height
        font.setBold(True)
        font.setFamily("Comic Sans MS")
        highscore_label.setStyleSheet("color: white")
        highscore_label.setContentsMargins(50, 0, 0, 0)
        highscore_label.setFont(font)
        self.main_layout.addWidget(highscore_label)

    def _init_game_modes_overlay(self):
        """Initialize the game modes overlay and connections"""
        self.game_modes_overlay = GameModes(self)
        # Position overlay next to buttons
        self.game_modes_overlay.setGeometry(
            int(self.width * 0.55),  # 55% from left
            int(self.height * 0.25),  # 25% from top
            int(self.width * 0.25),  # 25% of width
            int(self.height * 0.6)  # 60% of height
        )
        
        # Connect mode_selected signal to update game mode
        self.game_modes_overlay.mode_selected.connect(self.set_game_mode)

        self.game_mode_label = OverlayLabel(
            f"Game Mode: {self.MODE_DISPLAY_NAMES[self.current_game_mode]}", 
            parent=self
        )
        self.game_mode_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        font = QFont()
        font.setPointSize(int(self.height * 0.03))  # 3% of height
        self.game_mode_label.setFont(font)

    def _create_buttons(self):
        """Create and arrange all buttons"""
        
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        buttons_column = QWidget()
        buttons_column_layout = QVBoxLayout(buttons_column)
        buttons_column_layout.setSpacing(int(self.height * 0.02))  # 2% of height

        # Button definitions with their actions
        button_definitions = [
            ("Resume Game", self.resume_game),
            ("Play Again", self.play_again_fn),
            ("Game Modes", self.game_modes_overlay_toggle),
            ("Back to Menu", self.back_to_menu_fn),
            ("Quit Game", self.quit_game_fn)
        ]

        # Create and add all buttons with responsive sizing
        button_width = int(self.width * 0.2)  # 20% of width
        button_height = int(self.height * 0.08)  # 8% of height
        for text, callback in button_definitions:
            button = OverlayButton(text)
            button.setFixedSize(button_width, button_height)
            button.clicked.connect(callback)
            buttons_column_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignHCenter)

        buttons_layout.addWidget(buttons_column, alignment=Qt.AlignmentFlag.AlignLeft)
        buttons_layout.addStretch()

        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.game_mode_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(buttons_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addStretch(1)

    def set_game_mode(self, mode):
        """Set the current game mode and update UI"""
        self.current_game_mode = mode
        self.game_modes_overlay.set_active_mode(mode)
        display_text = self.MODE_DISPLAY_NAMES.get(self.current_game_mode, "Default")
        self.game_mode_label.setText(f"Game Mode: {display_text}")
        
        if self.parent and hasattr(self.parent, 'current_game_mode'):
            self.parent.current_game_mode = self.current_game_mode

    def update_game_mode_label(self):
        """Update the game mode label with the current mode"""
        display_text = self.MODE_DISPLAY_NAMES.get(self.current_game_mode, "Default")
        self.game_mode_label.setText(f"Game Mode: {display_text}")

    def game_modes_overlay_toggle(self):
        """Toggle the game modes overlay visibility"""
        if self.game_modes_overlay.isVisible():
            self.game_modes_overlay.hide()
        else:
            self.game_modes_overlay.set_active_mode(self.current_game_mode)
            self.game_modes_overlay.show()
            self.game_modes_overlay.raise_()
            # Ensure overlay is positioned next to buttons
            self.game_modes_overlay.move(
                int(self.width * 0.55),  # 55% from left
                int(self.height * 0.25),  # 25% from top
            )
            self.game_modes_overlay.resize(
                int(self.width * 0.25),  # 25% of width
                int(self.height * 0.6)  # 60% of height
            )

    def resume_game(self):
        """Resume the game without resetting state"""
        if self.parent and hasattr(self.parent, 'toggle_pause'):
            self.parent.toggle_pause(pause_overlay=self)
        else:
            self.hide()
            self.resume_game_signal.emit()

    def play_again_fn(self):
        """Handle play again action"""
        if hasattr(self.parent, 'elaborate_answer'):
            self.parent.elaborate_answer.retry_game_fn()
        self.hide()
        
    def back_to_menu_fn(self):
        """Return to main menu"""
        from src.scenes.menu.menu_window import Menu
        self.hide()
        if self.parent:
            self.parent.close()
        self.menu = Menu()
        self.menu.showFullScreen()

    def quit_game_fn(self):
        """Quit the application"""
        self.hide()
        if self.parent:
            self.parent.close()
        sys.exit()