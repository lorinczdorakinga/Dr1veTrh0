from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSpacerItem, QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette
from src.components.overlay_label import OverlayLabel
from src.components.overlay_button import OverlayButton
from src.core.logic.abstract_functions import get_resource_path
import requests
import webbrowser
import logging  # For debug
from src.components.notification import show_notification
from src.scenes.menu.auth_handler import AuthHandler
from src.core.logic.sound_manager import SoundManager
from src.core.logic.abstract_functions import did_user_pay  # Ensure this is your func

logging.basicConfig(level=logging.DEBUG)  # Add logs

class PaywallNotificationDialog(QDialog):
    button_clicked = pyqtSignal(str)

    def __init__(self, title: str, message: str, parent: QWidget | None = None, sound_manager=None):
        super().__init__(parent)
        self.sound_manager = sound_manager or SoundManager.get_instance(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setup_overlay_style()
        self._initialize_elements(title, message)
        self._center_content()

    def setup_overlay_style(self):
        """Apply overlay style like AuthHandler: frameless + transparent background."""
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 200))  # Semi-transparent black (fixed alpha=200)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Ensure full size of parent (will reapply in showEvent for dynamic parents)
        if self.parent():
            parent_rect = self.parent().geometry()
            self.resize(parent_rect.width(), parent_rect.height())
            self.move(0, 0)

    def _initialize_elements(self, title: str, message: str):
        # Central widget (like UserPage's central_widget)
        central_width = 500
        self.central_widget = QWidget()  # Save ref for mousePressEvent
        self.central_widget.setFixedWidth(central_width)
        self.central_widget.setStyleSheet("""
            QWidget {
                background-color: #222222;
                border-radius: 15px;
                border: none;
            }
        """)

        central_layout = QVBoxLayout(self.central_widget)
        central_layout.setContentsMargins(20, 20, 20, 20)
        central_layout.setSpacing(20)

        # Title (OverlayLabel, like UserPage)
        self.title_label = OverlayLabel(title)
        font = QFont("Comic Sans MS", 24, QFont.Weight.Bold)
        self.title_label.setFont(font)
        self.title_label.setTextColor("white")
        central_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Message (OverlayLabel, styled like scores_label)
        self.message_label = OverlayLabel(message)
        font = QFont("Comic Sans MS", 14, QFont.Weight.Normal)
        self.message_label.setFont(font)
        self.message_label.setTextColor("white")
        self.message_label.setStyleSheet("background-color: #333; padding: 10px; border-radius: 10px;")
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        central_layout.addWidget(self.message_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Spacer
        central_layout.addSpacerItem(QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        # Button row (Close left, I'm in right)
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        # Close button (disabled style)
        close_button = OverlayButton("Close", parent=self, sound_manager=self.sound_manager)
        close_button.setDisabledStyle()  # Grayed-out
        close_button.clicked.connect(lambda: self._on_button('close'))
        close_button.setFixedWidth(200)
        button_layout.addWidget(close_button)

        button_layout.addStretch(1)

        # I'm in button (default style)
        imin_button = OverlayButton("I'm in", parent=self, sound_manager=self.sound_manager)
        imin_button.setDefaultStyle()  # Orange
        imin_button.clicked.connect(lambda: self._on_button('imin'))
        imin_button.setFixedWidth(200)
        button_layout.addWidget(imin_button)

        button_layout.addStretch(1)
        central_layout.addLayout(button_layout)

        # Bottom spacer
        central_layout.addSpacerItem(QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

    def _center_content(self):
        """Center the central content in the full overlay using stretches (no fixed spacers)."""
        # Main layout for the entire dialog (transparent overlay)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Horizontal centering wrapper
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addStretch(1)
        horizontal_layout.addWidget(self.central_widget)
        horizontal_layout.addStretch(1)

        # Vertical centering: add stretch top, content, stretch bottom
        main_layout.addStretch(1)
        main_layout.addLayout(horizontal_layout)
        main_layout.addStretch(1)

        # Remove any min width / adjustSize that could crop; let layout expand
        self.setMinimumSize(0, 0)  # Allow full resize

    def _on_button(self, action: str):
        error_msg = None  # Initialize here to avoid UnboundLocalError
        if action == 'imin':
            auth_handler = AuthHandler()
            user = auth_handler.get_current_user()
            user_id = user['localId'] if user else None
            if not user_id:
                error_msg = "Log in required."
                show_notification("Error", error_msg)
                self.reject()
                self.close()
                return

            # Health check
            try:
                health = requests.get('http://localhost:3000/health', timeout=5)
                if health.status_code != 200:
                    raise Exception("Server not healthy")
            except Exception as e:
                error_msg = f"Payment server unavailable: {str(e)}"
                logging.error(error_msg)
                show_notification("Error", error_msg)
                self.close()
                return

            payload = {'user_id': user_id, 'price_id': 'price_1SHNH34C01LI6RDherzKg3tK'}
            try:
                response = requests.post(
                    'http://localhost:3000/create-checkout-session',
                    json=payload,
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                if 'url' in data:
                    logging.info("Opening Stripe Checkout")
                    webbrowser.open(data['url'])
                    self.start_polling()
                    self.accept()  # Optional: close dialog on success start
                else:
                    error_msg = data.get('error', 'Unknown response from server')
            except requests.exceptions.RequestException as e:
                error_msg = f"Network error: {str(e)}"
            except Exception as e:
                error_msg = str(e)
            
            if error_msg:
                logging.error(error_msg)
                show_notification("Error", error_msg)
        else:
            self.reject()
        self.close()
    def start_polling(self):
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.check_status)
        self.poll_timer.start(5000)  # Every 5s

    def mousePressEvent(self, event):
        """Background click outside central: sound + close."""
        if self.sound_manager:
            self.sound_manager.play_effect(self.sound_manager.button_click)
        # If click is outside the central widget, treat as 'close'
        if not self.central_widget.geometry().contains(event.position().toPoint()):
            self._on_button('close')
        super().mousePressEvent(event)

    def showEvent(self, event):
        """Ensure full coverage on show (in case parent resized)."""
        if self.parent():
            parent_rect = self.parent().geometry()
            self.setGeometry(parent_rect)  # Covers entire parent
        super().showEvent(event)

    def check_status(self):
        if did_user_pay():
            self.poll_timer.stop()
            show_notification("Success", "Premium unlocked!")
            
# --------------------------------------------------------------------------
# Convenience function
# --------------------------------------------------------------------------
def show_paywall_notification(title: str, message: str, parent: QWidget | None = None, sound_manager=None) -> str:
    """
    Show the overlay-style paywall dialog and return 'close' or 'imin'.
    """
    dlg = PaywallNotificationDialog(title, message, parent, sound_manager)
    dlg.exec()  # Modal block
    if dlg.result() == QDialog.DialogCode.Accepted:
        return 'imin'
    return 'close'
