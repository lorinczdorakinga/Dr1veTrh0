from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QFont, QPalette, QBrush
import sys

from gui.game_elements.overlay_button import OverlayButton
from gui.game_elements.overlay_label import OverlayLabel

from .game_scenes.test import Test
from .game_scenes.landing_overlays.game_modes import GameModes
from .game_scenes.landing_overlays.help import Help


class Menu(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Menu")
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        self.width = screen_geometry.width()
        self.height = screen_geometry.height()

        self.setMinimumSize(self.width, self.height)
        self.showFullScreen()

        # Keep track of the current game mode
        self.current_game_mode = None

        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)

        # Set background image using palette
        self.resize_background()

        # Initialize overlays
        self.game_modes_overlay = GameModes(self)
        self.help_overlay = Help(self)
        
        # Connect game modes signals to update current_game_mode
        self.game_modes_overlay.default_mode_selected.connect(lambda: self.set_game_mode("default"))
        self.game_modes_overlay.reverse_mode_selected.connect(lambda: self.set_game_mode("reverse"))
        self.game_modes_overlay.double_trouble_mode_selected.connect(lambda: self.set_game_mode("double_trouble"))
        self.game_modes_overlay.speedrun_mode_selected.connect(lambda: self.set_game_mode("speedrun"))

        # Buttons Container Widget with HBoxLayout
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)

        # Left spacer to push buttons right
        spacer_widget = QWidget()
        spacer_widget.setFixedWidth(100)
        buttons_layout.addWidget(spacer_widget)

        # Buttons Column Container
        buttons_column = QWidget()
        buttons_column_layout = QVBoxLayout(buttons_column)
        buttons_column_layout.setSpacing(40)

        # Create buttons
        self.start = OverlayButton("Start")
        self.start.clicked.connect(self.open_game_fn)
        self.start.setFixedSize(300, 80)

        self.game_modes_button = OverlayButton("Game Modes")
        self.game_modes_button.clicked.connect(self.game_modes_fn)
        self.game_modes_button.setFixedSize(300, 80)

        self.help = OverlayButton("Help")
        self.help.clicked.connect(self.help_fn)
        self.help.setFixedSize(300, 80)

        self.quit = OverlayButton("Quit")
        self.quit.clicked.connect(self.quit_fn)
        self.quit.setFixedSize(300, 80)

        # Add buttons to the column layout
        buttons_column_layout.addWidget(self.start)
        buttons_column_layout.addWidget(self.game_modes_button)
        buttons_column_layout.addWidget(self.help)
        buttons_column_layout.addWidget(self.quit)
        buttons_column_layout.addStretch()

        # Add the buttons column to the buttons container
        buttons_layout.addWidget(buttons_column, alignment=Qt.AlignmentFlag.AlignLeft)
        buttons_layout.addStretch()

        # Credit label
        self.credit = OverlayLabel("")
        self.credit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.credit.setTextColor("black")
        self.credit.setText("Made by Lorincz Dora-Kinga")

        self.game_modes_overlay.hide()
        self.help_overlay.hide()

        # Top stretch to push content downward
        main_layout.addStretch(3)

        # Add buttons container
        main_layout.addWidget(buttons_container)

        # Bottom stretch to create space before the credit label
        main_layout.addStretch(1)

        # Create a dedicated widget + layout for the credit label with margins
        credit_container = QWidget()
        credit_layout = QHBoxLayout(credit_container)
        credit_layout.setContentsMargins(0, 0, 20, 20)  # Right and bottom margin
        credit_layout.addWidget(self.credit, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        # Add the credit container to the main layout
        main_layout.addWidget(credit_container)

        # Optional: set spacing and margins on main layout
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)  # Prevent edge clipping

        # Handle window resize
        self.resizeEvent = self.handle_resize_event

    def resize_background(self):
        background_image_path = "/Users/lorinczdora/Documents/Development/GestureAI/img/lobby.jpg"
        pixmap = QPixmap(background_image_path).scaled(
            self.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        palette = self.palette()
        palette.setBrush(self.backgroundRole(), QBrush(pixmap))
        self.setPalette(palette)

    def handle_resize_event(self, event):
        self.resize_background()
        if hasattr(self, 'game_modes_overlay'):
            self.game_modes_overlay.resize(event.size().width(), event.size().height())
        super().resizeEvent(event)

    def set_game_mode(self, mode):
        """Set the current game mode and update UI accordingly"""
        self.current_game_mode = mode
        print(f"Game mode changed to: {mode}")
        
    def select_current_game_mode(self):
        """Update the game mode buttons to show the currently selected mode"""
        if self.current_game_mode == "default":
            self.game_modes_overlay.activate_default_mode()
        elif self.current_game_mode == "reverse":
            self.game_modes_overlay.activate_reverse_mode()
        elif self.current_game_mode == "double_trouble":
            self.game_modes_overlay.activate_double_trouble_mode()
        elif self.current_game_mode == "speedrun":
            self.game_modes_overlay.activate_speedrun_mode()

    def open_game_fn(self):
        if self.current_game_mode is None:
            self.current_game_mode = "default"
        print(f"Starting game with {self.current_game_mode} mode")
        self.game = Test(current_game_mode=self.current_game_mode)

        if hasattr(self.game, 'set_game_mode'):
            self.game.set_game_mode(self.current_game_mode)

        self.game.showFullScreen()
        self.close()  # Hide the menu window while playing

    def game_modes_fn(self):
        print("Game Modes button clicked")
        if self.game_modes_overlay.isVisible():
            self.game_modes_overlay.hide()
            self.game_modes_button.setDefaultStyle()
        else:
            self.select_current_game_mode()
            self.game_modes_overlay.show()
            self.game_modes_overlay.raise_()
            self.game_modes_button.setChosenStyle()

    def help_fn(self):
        if self.help_overlay.isVisible():
            self.help_overlay.hide()
            self.help.setDefaultStyle()
        else:
            self.help_overlay.show()
            self.help_overlay.raise_()
            self.help.setChosenStyle()

    def quit_fn(self):
        print("Quitting...")
        self.close()
        sys.exit()