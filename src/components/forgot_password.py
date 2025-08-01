from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from src.core.logic.abstract_functions import get_resource_path
from src.components.notification import show_notification
from src.core.logic.firebase_crud import FirebaseCRUD
from src.components.overlay_button import OverlayButton
from src.components.overlay_label import OverlayLabel

class ForgotPassword(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.fdb = FirebaseCRUD()
        self._setup_ui()
        self._initialize_elements()

    def _setup_ui(self):
        """Initialize the basic UI components"""
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(50, 50, 50, 50)

        if self.layout() is None:
            main_container_layout = QVBoxLayout(self)
            main_container_layout.addWidget(self.main_widget)
            main_container_layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(main_container_layout)

    def _initialize_elements(self):
        """Create and arrange all buttons and input fields"""
        central_width = 500
        central_widget = QWidget()
        central_widget.setFixedWidth(central_width)
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #222;
                border-radius: 15px;
            }
        """)

        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(20, 20, 20, 20)
        central_layout.setSpacing(20)

        # Title Label
        self.title_label = OverlayLabel("Reset Password")
        font = QFont("Comic Sans MS", 24, QFont.Weight.Bold)
        self.title_label.setFont(font)
        self.title_label.setTextColor("white")
        central_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Email Input
        email_layout = QHBoxLayout()
        email_icon = QLabel()
        path = get_resource_path("img/email.svg")
        email_icon.setPixmap(QPixmap(path).scaled(24, 24))
        email_layout.addWidget(email_icon, stretch=0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setStyleSheet("""
            QLineEdit {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 10px;
                padding: 5px;
                font-family: "Comic Sans MS";
            }
        """)
        email_layout.addWidget(self.email_input, stretch=1)
        dummy_label = QLabel()
        dummy_label.setFixedWidth(24)
        email_layout.addWidget(dummy_label, stretch=0)
        central_layout.addLayout(email_layout)

        # Reset Password Button
        reset_button = OverlayButton("Send Reset Link")
        reset_button.clicked.connect(self.reset_password_fn)
        central_layout.addWidget(reset_button, alignment=Qt.AlignmentFlag.AlignCenter)
        central_layout.addStretch()

        # Back Button
        back_button = OverlayButton("Back")
        back_button.clicked.connect(self.back)
        back_layout = QHBoxLayout()
        back_layout.addStretch()
        back_layout.addWidget(back_button)
        back_layout.addStretch()
        central_layout.addLayout(back_layout)

        self.main_layout.addStretch(1)
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addStretch(1)
        horizontal_layout.addWidget(central_widget)
        horizontal_layout.addStretch(1)
        self.main_layout.addLayout(horizontal_layout)
        self.main_layout.addStretch(1)

    def reset_password_fn(self):
        """Handle password reset request with better validation"""
        email = self.email_input.text().strip()
        
        # Enhanced email validation
        if not email:
            show_notification("Error", "Please enter your email address.")
            return
        
        # Better email format validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            show_notification("Error", "Please enter a valid email address.")
            return
        
        try:
            success = self.fdb.recover_password_by_email(email)
            if success:
                show_notification("Success", 
                    f"Password reset instructions have been sent to {email}. "
                    "Please check your email and follow the instructions.")
                self.parent.switch_to_login()
            else:
                show_notification("Error", 
                    "Unable to send reset email. Please verify your email address "
                    "and ensure you have an account with us.")
                
        except Exception as e:
            show_notification("Error", "An unexpected error occurred. Please try again later.")
    def back(self):
        """Return to login page"""
        self.parent.switch_to_login()