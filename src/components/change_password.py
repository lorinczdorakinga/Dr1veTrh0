from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from src.core.logic.abstract_functions import get_resource_path
from src.components.notification import show_notification
from src.core.logic.firebase_crud import FirebaseCRUD
from src.components.overlay_button import OverlayButton
from src.components.overlay_label import OverlayLabel

class ChangePassword(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.fdb = FirebaseCRUD()
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

        self.title_label = OverlayLabel("Change Password")
        font = QFont("Comic Sans MS", 24, QFont.Weight.Bold)
        self.title_label.setFont(font)
        self.title_label.setTextColor("white")
        central_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        current_password_layout = QHBoxLayout()
        lock_icon_current = QLabel()
        path = get_resource_path("img/password.svg")
        lock_icon_current.setPixmap(QPixmap(path).scaled(24, 24))
        current_password_layout.addWidget(lock_icon_current, stretch=0)
        self.current_password_input = QLineEdit()
        self.current_password_input.setPlaceholderText("Current Password")
        self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_password_input.setStyleSheet("""
            QLineEdit {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 10px;
                padding: 5px;
                font-family: "Comic Sans MS";
            }
        """)
        current_password_layout.addWidget(self.current_password_input, stretch=1)
        dummy_label_current = QLabel()
        dummy_label_current.setFixedWidth(24)
        current_password_layout.addWidget(dummy_label_current, stretch=0)
        central_layout.addLayout(current_password_layout)

        new_password_layout = QHBoxLayout()
        lock_icon_new = QLabel()
        lock_icon_new.setPixmap(QPixmap(path).scaled(24, 24))
        new_password_layout.addWidget(lock_icon_new, stretch=0)
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("New Password")
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setStyleSheet("""
            QLineEdit {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 10px;
                padding: 5px;
                font-family: "Comic Sans MS";
            }
        """)
        new_password_layout.addWidget(self.new_password_input, stretch=1)
        dummy_label_new = QLabel()
        dummy_label_new.setFixedWidth(24)
        new_password_layout.addWidget(dummy_label_new, stretch=0)
        central_layout.addLayout(new_password_layout)

        change_button = OverlayButton("Change Password")
        change_button.clicked.connect(self.change_password_fn)
        central_layout.addWidget(change_button, alignment=Qt.AlignmentFlag.AlignCenter)
        central_layout.addStretch()

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

    def change_password_fn(self):
        current_password = self.current_password_input.text()
        new_password = self.new_password_input.text()
        if not current_password or not new_password:
            show_notification("Error", "Please enter both current and new passwords.")
            return

        user = self.parent.get_current_user()
        if user and 'email' in user:
            reauth_result = self.fdb.reauthenticate_user(user['email'], current_password)
            if reauth_result:
                result = self.fdb.update_user_password(reauth_result['idToken'], new_password)
                if result:
                    if 'idToken' in result:
                        user['idToken'] = result['idToken']
                    if 'refreshToken' in result:
                        user['refreshToken'] = result['refreshToken']
                    
                    show_notification("Success", "Password updated successfully.")
                    self.back()
                else:
                    show_notification("Error", "Failed to update password.")
            else:
                show_notification("Error", "Current password is incorrect.")
        else:
            show_notification("Error", "Not logged in.")

    def back(self):
        self.parent.switch_to_user_page()

    def mousePressEvent(self, event):
        self.parent.hide()