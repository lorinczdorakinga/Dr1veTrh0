from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QStyle, QPushButton, QHBoxLayout, QLineEdit, QSizePolicy, QFrame
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QFont, QPalette, QBrush, QColor
import sys

from src.core.logic.abstract_functions import get_resource_path
from src.components.notification import show_notification
from src.core.logic.firebase_crud import FirebaseCRUD
from src.components.overlay_button import OverlayButton
from src.components.overlay_label import OverlayLabel

class Register(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._setup_ui()
        self._initialize_elements()
        self.fdb = FirebaseCRUD()

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

    def register_fn(self, username, email, password, confirm_password):
        if not username or not email or not password or not confirm_password:
            show_notification("Error", "Please fill in all fields.")
            return
        
        if password != confirm_password:
            show_notification("Error", "Passwords do not match.")
            return
        if not email.__contains__("@") and  not email.__contains__("."):
            show_notification("Error", "Please enter a valid email address.")
            return

        if len(password) < 6:
            show_notification("Error", "Password must be at least 6 characters long.")
            return

        res = self.fdb.register_user(username, email, password)
        if res is not None:
            show_notification("Success", f"Registration successful for {username}")
            self.parent.switch_to_login()
        else:
            show_notification("Error", "Registration failed. Please try again.")

    def back(self):
        self.parent.exit_widget()

    def _initialize_elements(self):
        """Create and arrange all buttons and input fields """
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

        self.title_label = OverlayLabel("Sign Up")
        font = QFont("Comic Sans MS", 24, QFont.Weight.Bold)
        self.title_label.setFont(font)
        self.title_label.setTextColor("white")
        central_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        username_layout = QHBoxLayout()
        user_icon = QLabel()
        path = get_resource_path("img/user.svg")
        user_icon.setPixmap(QPixmap(path).scaled(24, 24))
        username_layout.addWidget(user_icon, stretch=0)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 10px;
                padding: 5px;
                font-family: "Comic Sans MS";
            }
        """)
        username_layout.addWidget(self.username_input, stretch=1)
        dummy_label = QLabel()
        dummy_label.setFixedWidth(24)
        username_layout.addWidget(dummy_label, stretch=0)
        central_layout.addLayout(username_layout)

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
        dummy_label_email = QLabel()
        dummy_label_email.setFixedWidth(24)
        email_layout.addWidget(dummy_label_email, stretch=0)
        central_layout.addLayout(email_layout)

        password_layout = QHBoxLayout()
        lock_icon = QLabel()
        path = get_resource_path("img/password.svg")
        lock_icon.setPixmap(QPixmap(path).scaled(24, 24))
        password_layout.addWidget(lock_icon, stretch=0)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 10px;
                padding: 5px;
                font-family: "Comic Sans MS";
            }
        """)
        password_layout.addWidget(self.password_input, stretch=1)
        self.visibility_icon = QLabel()
        self.invisible_path = get_resource_path("img/invisible.svg")
        self.visible_path = get_resource_path("img/visible.svg")
        self.visibility_icon.setPixmap(QPixmap(self.invisible_path).scaled(24, 24))
        self.visibility_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.visibility_icon.mousePressEvent = self.toggle_password_visibility
        password_layout.addWidget(self.visibility_icon, stretch=0)
        central_layout.addLayout(password_layout)

        confirm_password_layout = QHBoxLayout()
        lock_icon_confirm = QLabel()
        path = get_resource_path("img/password.svg")
        lock_icon_confirm.setPixmap(QPixmap(path).scaled(24, 24))
        confirm_password_layout.addWidget(lock_icon_confirm, stretch=0)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setStyleSheet("""
            QLineEdit {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 10px;
                padding: 5px;
                font-family: "Comic Sans MS";
            }
        """)
        confirm_password_layout.addWidget(self.confirm_password_input, stretch=1)
        self.confirm_visibility_icon = QLabel()
        self.confirm_visibility_icon.setPixmap(QPixmap(self.invisible_path).scaled(24, 24))
        self.confirm_visibility_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.confirm_visibility_icon.mousePressEvent = self.toggle_confirm_password_visibility
        confirm_password_layout.addWidget(self.confirm_visibility_icon, stretch=0)
        central_layout.addLayout(confirm_password_layout)

        register_button = OverlayButton("Register")
        register_button.clicked.connect(lambda: self.register_fn(
            self.username_input.text(), 
            self.email_input.text(), 
            self.password_input.text(), 
            self.confirm_password_input.text()
        ))
        central_layout.addWidget(register_button, alignment=Qt.AlignmentFlag.AlignCenter)
        central_layout.addStretch()

        login_layout = QVBoxLayout()
        login_layout.addStretch()
        login_button = OverlayButton("Already have an account? Sign In")
        login_button.setFlat(True)
        font = login_button.font()
        font.setUnderline(True)
        login_button.setFont(font)
        login_button.setStyleSheet("""
            OverlayButton {
                background-color: transparent;
                color: lightblue;
                font-size: 16pt;
                border: none;
            }
            OverlayButton:hover {
                color: skyblue;
            }
        """)
        login_button.clicked.connect(self.login_fn)
        login_layout.addWidget(login_button, alignment=Qt.AlignmentFlag.AlignCenter)
        central_layout.addLayout(login_layout)

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

    def login_fn(self):
        self.parent.switch_to_login()

    def toggle_password_visibility(self, event):
        """Toggle the visibility of the password"""
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.visibility_icon.setPixmap(QPixmap(self.visible_path).scaled(24, 24))
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.visibility_icon.setPixmap(QPixmap(self.invisible_path).scaled(24, 24))

    def toggle_confirm_password_visibility(self, event):
        """Toggle the visibility of the confirm password"""
        if self.confirm_password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.confirm_visibility_icon.setPixmap(QPixmap(self.visible_path).scaled(24, 24))
        else:
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_visibility_icon.setPixmap(QPixmap(self.invisible_path).scaled(24, 24))