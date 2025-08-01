from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QInputDialog, QLineEdit
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from src.components.overlay_label import OverlayLabel
from src.components.overlay_button import OverlayButton
from src.components.notification import show_notification

class UserPage(QWidget):
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

    def _initialize_elements(self):
        central_width = 500
        central_widget = QWidget()
        central_widget.setFixedWidth(central_width)
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #222;
                border-radius: 15px;
                border: none;
            }
        """)

        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(20, 20, 20, 20)
        central_layout.setSpacing(20)

        self.title_label = OverlayLabel("User Profile")
        font = QFont("Comic Sans MS", 24, QFont.Weight.Bold)
        self.title_label.setFont(font)
        self.title_label.setTextColor("white")
        central_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.username_label = OverlayLabel("Username: Loading...")
        font = QFont("Comic Sans MS", 16)
        self.username_label.setFont(font)
        self.username_label.setTextColor("white")
        central_layout.addWidget(self.username_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.email_label = OverlayLabel("Email: Loading...")
        font = QFont("Comic Sans MS", 16)
        self.email_label.setFont(font)
        self.email_label.setTextColor("white")
        central_layout.addWidget(self.email_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.scores_label = OverlayLabel("High Scores:\nLoading...")
        font = QFont("Comic Sans MS", 14)
        self.scores_label.setFont(font)
        self.scores_label.setTextColor("white")
        self.scores_label.setWordWrap(True)
        self.scores_label.setFixedHeight(300)
        central_layout.addWidget(self.scores_label, alignment=Qt.AlignmentFlag.AlignCenter)

        change_email_button = OverlayButton("Change Email")
        change_email_button.clicked.connect(self.change_email)
        central_layout.addWidget(change_email_button, alignment=Qt.AlignmentFlag.AlignCenter)

        change_password_button = OverlayButton("Change Password")
        change_password_button.clicked.connect(self.change_password)
        central_layout.addWidget(change_password_button, alignment=Qt.AlignmentFlag.AlignCenter)

        logout_button = OverlayButton("Log Out")
        logout_button.clicked.connect(self.logout)
        central_layout.addWidget(logout_button, alignment=Qt.AlignmentFlag.AlignCenter)

        back_button = OverlayButton("Back")
        back_button.clicked.connect(self.back)
        central_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        scroll_area = QScrollArea()
        scroll_area.setWidget(central_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addStretch(1)
        horizontal_layout.addWidget(scroll_area)
        horizontal_layout.addStretch(1)

        self.main_layout.addStretch(1)
        self.main_layout.addLayout(horizontal_layout)
        self.main_layout.addStretch(1)

    def update_user_data(self):
        user = self.parent.get_current_user()
        if user:
            self.username_label.setText(f"Username: {user.get('displayName', user['email'])}")
            self.email_label.setText(f"Email: {user['email']}")
            scores = self.parent.fdb.get_user_records(user['localId'])
            if scores:
                scores_text = "High Scores:\n"
                for key, value in scores.items():
                    if key.endswith("_highscore"):
                        mode_name = key.replace("_highscore", "").replace("_", " ").title()
                        scores_text += f"{mode_name}: {value}\n"
            else:
                scores_text = "High Scores:\nNo scores available."
            self.scores_label.setText(scores_text)
        else:
            self.username_label.setText("Username: Not logged in")
            self.email_label.setText("Email: Not logged in")
            self.scores_label.setText("High Scores:\nNot logged in")

    def change_email(self):
        new_email, ok = QInputDialog.getText(self, "Change Email", "Enter new email:", QLineEdit.EchoMode.Normal)
        if ok and new_email:
            user = self.parent.get_current_user()
            if user and 'idToken' in user:
                result = self.parent.fdb.update_user_email(user['idToken'], new_email)
                if result:
                    user['email'] = new_email
                    self.email_label.setText(f"Email: {new_email}")
                    show_notification("Success", "Email updated successfully.")
                else:
                    show_notification("Error", "Failed to update email.")
            else:
                show_notification("Error", "Not logged in.")

    def change_password(self):
        new_password, ok = QInputDialog.getText(self, "Change Password", "Enter new password:", QLineEdit.EchoMode.Password)
        if ok and new_password:
            user = self.parent.get_current_user()
            if user and 'idToken' in user:
                result = self.parent.fdb.update_user_password(user['idToken'], new_password)
                if result:
                    show_notification("Success", "Password updated successfully.")
                else:
                    show_notification("Error", "Failed to update password.")
            else:
                show_notification("Error", "Not logged in.")

    def logout(self):
        self.parent.logout()

    def back(self):
        self.parent.exit_widget()