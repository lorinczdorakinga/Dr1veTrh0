from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QFont, QPalette, QBrush
import sys

from src.core.logic.abstract_functions import get_resource_path
from src.scenes.menu.auth_handler import AuthHandler
from src.components.overlay_button import OverlayButton
from src.components.overlay_label import OverlayLabel
from src.scenes.test import Test
from src.overlays.game_modes import GameModes
from src.overlays.help import Help

class Menu(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.auth_handler = AuthHandler(self)  # Initialize AuthHandler to check session
        self._setup_ui()
        self._initialize_elements()

        # Connect signals for dynamic updates
        self.auth_handler.user_logged_in.connect(self.update_auth_button)
        self.auth_handler.user_logged_out.connect(self.update_auth_button)

        self.showFullScreen()

    def _initialize_elements(self):
        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(int(self.height * 0.02))  # 2% of screen height

        # Initialize overlays
        self.game_modes_overlay = GameModes(self)
        self.game_modes_overlay.setGeometry(
            int(self.width * 0.25),
            int(self.height * 0.25),
            int(self.width * 0.25),
            int(self.height * 0.6)
        )
        self.game_modes_overlay.mode_selected.connect(self.set_game_mode)

        # Buttons Container Widget with HBoxLayout
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)

        # Left spacer to push buttons right
        spacer_widget = QWidget()
        spacer_widget.setFixedWidth(int(self.width * 0.06))
        buttons_layout.addWidget(spacer_widget)

        # Buttons Column Container
        buttons_column = QWidget()
        buttons_column_layout = QVBoxLayout(buttons_column)
        buttons_column_layout.setSpacing(int(self.height * 0.04))

        # Create buttons with responsive sizing
        button_width = int(self.width * 0.2)
        button_height = int(self.height * 0.08)

        # Set auth button based on login status
        self.auth = OverlayButton("thinking")
        self.auth.setFixedSize(button_width, button_height)
        self.check_if_user_logged_in()

        self.start = OverlayButton("Start")
        self.start.clicked.connect(self.open_game_fn)
        self.start.setFixedSize(button_width, button_height)

        self.game_modes_button = OverlayButton("Game Modes")
        self.game_modes_button.clicked.connect(self.game_modes_fn)
        self.game_modes_button.setFixedSize(button_width, button_height)

        self.help = OverlayButton("Help")
        self.help.clicked.connect(self.help_fn)
        self.help.setFixedSize(button_width, button_height)

        self.quit = OverlayButton("Quit")
        self.quit.clicked.connect(self.quit_fn)
        self.quit.setFixedSize(button_width, button_height)

        # Add buttons to the column layout
        buttons_column_layout.addWidget(self.start)
        buttons_column_layout.addWidget(self.game_modes_button)
        buttons_column_layout.addWidget(self.help)
        buttons_column_layout.addWidget(self.quit)
        buttons_column_layout.addStretch()

        buttons_layout.addWidget(buttons_column, alignment=Qt.AlignmentFlag.AlignLeft)
        buttons_layout.addStretch()

        # Credit label
        self.credit = OverlayLabel("Made by Lorincz Dora-Kinga")
        self.credit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.credit.setTextColor("black")
        font = QFont()
        font.setPointSize(int(self.height * 0.02))
        self.credit.setFont(font)

        self.game_modes_overlay.hide()
        self.help_overlay = Help(self)
        self.help_overlay.hide()

        main_layout.addWidget(self.auth, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        main_layout.addStretch(3)
        main_layout.addWidget(buttons_container)
        main_layout.addStretch(1)

        credit_container = QWidget()
        credit_layout = QHBoxLayout(credit_container)
        credit_layout.setContentsMargins(0, 0, int(self.width * 0.015), int(self.height * 0.02))
        credit_layout.addWidget(self.credit, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(credit_container)

        main_layout.setContentsMargins(int(self.width * 0.015), int(self.height * 0.02), int(self.width * 0.015), int(self.height * 0.02))
        self.resizeEvent = self.handle_resize_event
        self.game_modes_overlay.set_active_mode(self.current_game_mode)

    def _setup_ui(self):
        self.setWindowTitle("Menu")
        self.screen = QApplication.primaryScreen()
        self.screen_geometry = self.screen.geometry()
        self.width = self.screen_geometry.width()
        self.height = self.screen_geometry.height()
        self.setMinimumSize(self.width, self.height)
        self.current_game_mode = "default"
        self.resize_background()

    def resize_background(self):
        background_image_path = get_resource_path("img/lobby.jpg")
        pixmap = QPixmap(background_image_path).scaled(
            self.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        palette = self.palette()
        palette.setBrush(self.backgroundRole(), QBrush(pixmap))
        self.setPalette(palette)

    def handle_resize_event(self, event):
        self.width = event.size().width()
        self.height = event.size().height()
        self.resize_background()
        if hasattr(self, 'game_modes_overlay'):
            self.game_modes_overlay.resize(int(self.width * 0.25), int(self.height * 0.6))
            self.game_modes_overlay.move(int(self.width * 0.25), int(self.height * 0.25))
        super().resizeEvent(event)

    def set_game_mode(self, mode):
        self.current_game_mode = mode
        self.game_modes_overlay.set_active_mode(mode)
        print(f"Game mode changed to: {mode}")

    def open_game_fn(self):
        print(f"Starting game with {self.current_game_mode} mode")
        self.game = Test(auth_handler=self.auth_handler, current_game_mode=self.current_game_mode)        
        if hasattr(self.game, 'set_game_mode'):
            self.game.set_game_mode(self.current_game_mode)
        self.game.showFullScreen()
        self.close()

    def game_modes_fn(self):
        print("Game Modes button clicked")
        if self.game_modes_overlay.isVisible():
            self.game_modes_overlay.hide()
            self.game_modes_button.setDefaultStyle()
        else:
            self.game_modes_overlay.set_active_mode(self.current_game_mode)
            self.game_modes_overlay.show()
            self.game_modes_overlay.raise_()
            self.game_modes_button.setChosenStyle()
            self.game_modes_overlay.move(int(self.width * 0.25), int(self.height * 0.25))
            self.game_modes_overlay.resize(int(self.width * 0.25), int(self.height * 0.6))

    def check_if_user_logged_in(self):
        if self.auth_handler.is_user_logged_in():
            self.auth.setText("Already logged in")
            self.auth.clicked.connect(self.open_user_page)
        else:
            self.auth.setText("Log in / Sign up")
            self.auth.clicked.connect(self.auth_fn)
    def auth_fn(self):
        self.auth_handler.switch_to_login()
        self.auth_handler.show()
        self.auth_handler.raise_()
        self.auth.setDefaultStyle()

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

    def open_user_page(self):
        self.auth_handler.switch_to_user_page()
        self.auth_handler.show()
        self.auth_handler.raise_()

    def update_auth_button(self):
        if self.auth_handler.is_user_logged_in():
            self.auth.setText("Already logged in")
            self.auth.clicked.disconnect()
            self.auth.clicked.connect(self.open_user_page)
        else:
            self.auth.setText("Log in / Sign up")
            self.auth.clicked.disconnect()
            self.auth.clicked.connect(self.auth_fn)