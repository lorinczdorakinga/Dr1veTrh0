from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QFont, QColor, QPalette
from PyQt6.QtCore import Qt, pyqtSignal
import sys

from gui.game_elements.overlay_button import OverlayButton
from gui.game_elements.overlay_label import OverlayLabel
from gui.game_scenes.landing_overlays.game_modes import GameModes

class Pause(QWidget):
    resume_game_signal = pyqtSignal()  # Signal to notify parent that game should resume
    
    def __init__(self, parent=None, current_game_mode=None):
        # Setup
        super().__init__(parent)
        self.parent = parent
        
        # Initialize with parent's game mode or default
        if current_game_mode is None and hasattr(parent, 'current_game_mode'):
            self.current_game_mode = parent.current_game_mode
        elif current_game_mode is not None:
            self.current_game_mode = current_game_mode
        else:
            self.current_game_mode = "default"

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # No window frame
        palette = QPalette()
        # Set the background color with an alpha value (e.g., 128 for 50% transparency)
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 128))
        self.setPalette(palette)
        self.setAutoFillBackground(True)  # Enable auto fill background

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)  # Add space between widgets
        
        # Buttons Container Widget with HBoxLayout
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        
        # Left spacer to push buttons right
        # spacer_widget = QWidget()
        # spacer_widget.setFixedWidth(self.setalig)  # This sets the left margin wanted
        # buttons_layout.addWidget(spacer_widget)
        
        # Buttons Column Container
        buttons_column = QWidget()
        buttons_column_layout = QVBoxLayout(buttons_column)
        buttons_column_layout.setSpacing(20)  # Space between buttons
        
        # Initialize game modes overlay and connect its signals
        self.game_modes_overlay = GameModes(self)
        self.game_modes_overlay.move(500, 25)
        self.game_modes_overlay.default_mode_selected.connect(self.update_game_mode_label)
        self.game_modes_overlay.reverse_mode_selected.connect(self.update_game_mode_label)
        self.game_modes_overlay.double_trouble_mode_selected.connect(self.update_game_mode_label)
        self.game_modes_overlay.speedrun_mode_selected.connect(self.update_game_mode_label)

        # Create game mode label
        self.game_mode_label = OverlayLabel(f"Game Mode: {self.current_game_mode}", parent=self)
        self.game_mode_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Create buttons
        self.resume_button = OverlayButton("Resume Game")
        self.resume_button.setFixedSize(300, 80)
        self.resume_button.clicked.connect(self.resume_game)

        self.play_again = OverlayButton("Play again")
        self.play_again.setFixedSize(300, 80)
        self.play_again.clicked.connect(self.play_again_fn)

        self.game_modes_button = OverlayButton("Game Modes")
        self.game_modes_button.setFixedSize(300, 80)
        self.game_modes_button.clicked.connect(self.game_modes_overlay_toggle)
        
        self.back_to_menu = OverlayButton("Back to Menu")
        self.back_to_menu.setFixedSize(300, 80)
        self.back_to_menu.clicked.connect(self.back_to_menu_fn)

        self.quit = OverlayButton("Quit Game")
        self.quit.setFixedSize(300, 80)
        self.quit.clicked.connect(self.quit_game_fn)

        buttons_column_layout.addWidget(self.resume_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        buttons_column_layout.addWidget(self.play_again, alignment=Qt.AlignmentFlag.AlignHCenter)
        buttons_column_layout.addWidget(self.game_modes_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        buttons_column_layout.addWidget(self.back_to_menu, alignment=Qt.AlignmentFlag.AlignHCenter)
        buttons_column_layout.addWidget(self.quit, alignment=Qt.AlignmentFlag.AlignHCenter)
        buttons_column_layout.addStretch()  # Push buttons to top of column
        
        buttons_layout.addWidget(buttons_column, alignment=Qt.AlignmentFlag.AlignLeft)
        buttons_layout.addStretch()  # Push buttons to left of container
        
        # Create layout with spacing
        main_layout.addStretch(1)  
        main_layout.addWidget(self.game_mode_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(buttons_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        main_layout.addStretch(1) 

        self.game_modes_overlay.hide() 
        self.setLayout(main_layout)
        
        self.sync_game_modes_overlay()
        self.update_game_mode_label()
    
    def update_game_mode_label(self):
        """Update the game mode label with the current mode"""
        self.current_game_mode = self.game_modes_overlay.active_mode

        display_text = self.current_game_mode
        if display_text == "double_trouble":
            display_text = "double trouble"
        elif display_text == "default":
            display_text = "default"
        elif display_text == "reverse":
            display_text = "reverse"
        elif display_text == "speedrun":
            display_text = "speedrun"
        elif display_text == None:
            display_text = "default"
        self.game_mode_label.setText(f"Game Mode: {display_text}")
        
        # Also update parent if it exists
        if self.parent and hasattr(self.parent, 'current_game_mode'):
            self.parent.current_game_mode = self.current_game_mode
    
    def sync_game_modes_overlay(self):
        """Sync the game modes overlay with the current game mode"""
        if self.current_game_mode == "default":
            self.game_modes_overlay.activate_default_mode()
        elif self.current_game_mode == "reverse":
            self.game_modes_overlay.activate_reverse_mode()
        elif self.current_game_mode == "double_trouble":
            self.game_modes_overlay.activate_double_trouble_mode()
        elif self.current_game_mode == "speedrun":
            self.game_modes_overlay.activate_speedrun_mode()
    
    def game_modes_overlay_toggle(self):
        if self.game_modes_overlay.isVisible():
            self.game_modes_overlay.hide()
            self.game_modes_button.setDefaultStyle()
        else:
            self.sync_game_modes_overlay()
            self.game_modes_overlay.show()
            self.game_modes_overlay.raise_()
            self.game_modes_button.setChosenStyle()

    def resume_game(self):
        if self.parent:
            if hasattr(self.parent, 'set_game_mode'):
                self.parent.set_game_mode(self.current_game_mode)
            
            if hasattr(self.parent, 'toggle_pause'):
                self.parent.toggle_pause()
        else:
            # Fallback if parent doesn't have toggle_pause
            self.hide()
            self.resume_game_signal.emit()

    def play_again_fn(self):
        self.parent.elaborate_answer.retry_game_fn()
        self.hide()
        
    def back_to_menu_fn(self):
        from gui.menu_window import Menu # Import here to avoid circular imports
        self.hide()
        self.parent.close()
        self.menu = Menu()
        self.menu.showFullScreen()

    def quit_game_fn(self):
        self.hide()
        self.parent.close()
        sys.exit()