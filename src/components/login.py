from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QStyle, QPushButton, QHBoxLayout, QLineEdit, QSizePolicy, QFrame
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QFont, QPalette, QBrush, QColor
import sys

from src.core.logic.abstract_functions import get_resource_path
from src.components.notification import show_notification
from src.components.overlay_button import OverlayButton
from src.components.overlay_label import OverlayLabel
from src.components.forgot_password import ForgotPassword
from src.components.register import Register

class UserAuth(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._setup_ui()
        self._initialize_elements()

    def _setup_ui(self):
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(50, 50, 50, 50)

        if self.layout() is None:
            main_container_layout = QVBoxLayout(self)
            main_container_layout.addWidget(self.main_widget)
            main_container_layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(main_container_layout)

    def login_fn(self, email, password):
        res = self.parent.fdb.login_user(email, password)
        if isinstance(res, dict) and 'idToken' in res:
            show_notification("Success", f"Login successful for {res.get('displayName', 'User')}")
            self.parent.set_current_user(res)
            self.parent.user_page.update_user_data()
            self.parent.switch_to_user_page()
        else:
            error_msg = res if isinstance(res, str) else "Login failed. Please check your credentials."
            show_notification("Error", error_msg)

    def register_fn(self):
        self.parent.switch_to_register()

    def forgot_password_fn(self):
        self.parent.switch_to_forgot_password()

    def back(self):
        self.parent.exit_widget()

    def _initialize_elements(self):
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

        self.title_label = OverlayLabel("Sign In")
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
        self.username_input.setPlaceholderText("Email")
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

        login_button = OverlayButton("Log in")
        login_button.clicked.connect(lambda: self.login_fn(self.username_input.text(), self.password_input.text()))
        central_layout.addWidget(login_button, alignment=Qt.AlignmentFlag.AlignCenter)
        central_layout.addStretch()

        forgot_layout = QVBoxLayout()
        forgot_layout.addStretch()
        forgot_button = OverlayButton("Forgot Password?")
        forgot_button.setFlat(True)
        font = forgot_button.font()
        font.setUnderline(True)
        forgot_button.setFont(font)
        forgot_button.setStyleSheet("""
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
        forgot_button.clicked.connect(self.forgot_password_fn)
        forgot_layout.addWidget(forgot_button, alignment=Qt.AlignmentFlag.AlignCenter)
        central_layout.addLayout(forgot_layout)

        register_button = OverlayButton("Register now")
        register_button.clicked.connect(self.register_fn)
        central_layout.addWidget(register_button, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def toggle_password_visibility(self, event):
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.visibility_icon.setPixmap(QPixmap(self.visible_path).scaled(24, 24))
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.visibility_icon.setPixmap(QPixmap(self.invisible_path).scaled(24, 24))