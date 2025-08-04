from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QInputDialog, QLineEdit, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QFont, QPixmap, QColor
from PyQt6.QtCore import Qt

from src.components.overlay_label import OverlayLabel
from src.components.overlay_button import OverlayButton
from src.components.notification import show_notification
from src.core.logic.abstract_functions import get_resource_path

class UserPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._setup_ui()
        self._initialize_elements()

    def _setup_ui(self):
        # Main widget to hold the layout with semi-transparent background matching AuthHandler
        self.main_widget = QWidget(self)
        # self.main_widget.setStyleSheet("background-color: rgba(0, 0, 0, 230);")
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # No margins on outer layout
        self.main_layout.setSpacing(0)

        # Set up the main container layout for the UserPage widget
        main_container_layout = QVBoxLayout(self)
        main_container_layout.setContentsMargins(0, 0, 0, 0)
        main_container_layout.addWidget(self.main_widget)
        self.setLayout(main_container_layout)

    def _initialize_elements(self):
        # Central widget with solid background
        central_width = 590
        central_widget = QWidget()
        central_widget.setFixedWidth(central_width)
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #222222;
                border-radius: 15px;
                border: none;
            }
        """)

        # Content layout inside central_widget
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(20, 20, 20, 20)
        central_layout.setSpacing(20)

        self.title_label = OverlayLabel("User Profile")
        font = QFont("Comic Sans MS", 24, QFont.Weight.Bold)
        self.title_label.setFont(font)
        self.title_label.setTextColor("white")

        # Username Label
        self.username_label = OverlayLabel("Loading...")
        font = QFont("Comic Sans MS", 22, QFont.Weight.Bold)
        self.username_label.setFont(font)
        self.username_label.setTextColor(QColor("#FFD700"))
        self.username_label.setStyleSheet("background-color: #333; padding: 10px; border-radius: 10px;")
        self.username_label.setWordWrap(True)

        # High Scores Section
        highscores_subtitle = OverlayLabel("High Scores")
        font = QFont("Comic Sans MS", 14, QFont.Weight.Bold)
        highscores_subtitle.setFont(font)
        highscores_subtitle.setTextColor("white")

        self.scores_label = OverlayLabel("Loading...")
        font = QFont("Comic Sans MS", 12, QFont.Weight.Light)
        self.scores_label.setFont(font)
        self.scores_label.setTextColor("white")
        self.scores_label.setWordWrap(True)
        self.scores_label.setMinimumHeight(200)

        # Email Section
        email_subtitle = OverlayLabel("Email")
        font = QFont("Comic Sans MS", 14, QFont.Weight.Bold)
        email_subtitle.setFont(font)
        email_subtitle.setTextColor("white")

        email_layout = QHBoxLayout()
        email_icon = QLabel()
        email_icon_path = get_resource_path("img/email.svg")
        email_icon.setPixmap(QPixmap(email_icon_path).scaled(24, 24))
        email_layout.addWidget(email_icon, stretch=0)

        self.email_input = QLineEdit()
        self.email_input.setReadOnly(True)
        self.email_input.setStyleSheet("""
            QLineEdit {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 10px;
                padding: 5px;
                font-family: "Comic Sans MS";
                font-size: 12pt;
            }
        """)
        email_layout.addWidget(self.email_input, stretch=1)

        change_email_button = OverlayButton("Change Email")
        change_email_button.clicked.connect(self.change_email)
        email_layout.addWidget(change_email_button, stretch=0)

        # Password Section
        password_subtitle = OverlayLabel("Password")
        font = QFont("Comic Sans MS", 14, QFont.Weight.Bold)
        password_subtitle.setFont(font)
        password_subtitle.setTextColor("white")

        password_layout = QHBoxLayout()
        password_icon = QLabel()
        password_icon_path = get_resource_path("img/password.svg")
        password_icon.setPixmap(QPixmap(password_icon_path).scaled(24, 24))
        password_layout.addWidget(password_icon, stretch=0)

        self.password_input = QLineEdit()
        self.password_input.setReadOnly(True)
        self.password_input.setText("********")
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 10px;
                padding: 5px;
                font-family: "Comic Sans MS";
                font-size: 12pt;
            }
        """)
        password_layout.addWidget(self.password_input, stretch=1)

        change_password_button = OverlayButton("Change Password")
        change_password_button.clicked.connect(self.change_password)
        password_layout.addWidget(change_password_button, stretch=0)

        # Logout and Back Buttons
        logout_button = OverlayButton("Log Out")
        logout_button.clicked.connect(self.logout)

        back_button = OverlayButton("Back")
        back_button.clicked.connect(self.back)        

        # Page Layout with Fixed Spacers
        central_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        central_layout.addWidget(self.username_label, alignment=Qt.AlignmentFlag.AlignCenter)
        central_layout.addSpacerItem(QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        central_layout.addWidget(highscores_subtitle, alignment=Qt.AlignmentFlag.AlignHCenter)
        central_layout.addWidget(self.scores_label, alignment=Qt.AlignmentFlag.AlignLeft)
        central_layout.addSpacerItem(QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        central_layout.addWidget(email_subtitle, alignment=Qt.AlignmentFlag.AlignLeft)
        central_layout.addLayout(email_layout)
        central_layout.addSpacerItem(QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        central_layout.addWidget(password_subtitle, alignment=Qt.AlignmentFlag.AlignLeft)
        central_layout.addLayout(password_layout)
        central_layout.addSpacerItem(QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        central_layout.addWidget(logout_button, alignment=Qt.AlignmentFlag.AlignCenter)
        central_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Scroll area to contain central_widget
        scroll_area = QScrollArea()
        scroll_area.setWidget(central_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        scroll_area.setWidgetResizable(True)  # Allow resizing to fit content
        scroll_area.setFixedWidth(central_width + 20)  # Fix width to prevent horizontal expansion

        # Horizontal layout for centering the scroll area
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addStretch(1)
        horizontal_layout.addWidget(scroll_area)
        horizontal_layout.addStretch(1)

        # Add 100px fixed spacers for top and bottom margins
        self.main_layout.addSpacerItem(QSpacerItem(0, 100, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        self.main_layout.addLayout(horizontal_layout)
        self.main_layout.addSpacerItem(QSpacerItem(0, 200, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

    def update_user_data(self):
        user = self.parent.get_current_user()
        if user:
            self.username_label.setText(user.get('displayName', user['email']))
            self.email_input.setText(user['email'])
            scores = self.parent.fdb.get_user_records(user['localId'])
            if scores:
                scores_text = ""
                for key, value in scores.items():
                    if key.endswith("_highscore"):
                        formatted_key = key.replace("_highscore", "").replace("_", " ").title()
                        scores_text += f"{formatted_key}: {value}\n"
            else:
                scores_text = "No scores available."
            self.scores_label.setWordWrap(True)
            self.scores_label.setMinimumHeight(200)
            self.scores_label.setText(scores_text)
        else:
            self.username_label.setText("Not logged in")
            self.email_input.setText("Not logged in")
            self.scores_label.setText("Not logged in")

    def change_email(self):
        new_email, ok = QInputDialog.getText(self, "Change Email", "Enter new email:", QLineEdit.EchoMode.Normal)
        if ok and new_email:
            user = self.parent.get_current_user()
            if user and 'idToken' in user:
                # First check if current email is already verified
                is_verified = self.parent.fdb.check_email_verification_status(user['idToken'])
                
                if is_verified:
                    # Email is verified, try to update directly
                    result = self.parent.fdb.update_user_email(user['idToken'], new_email)
                    if result:
                        user['email'] = new_email
                        if 'idToken' in result:
                            user['idToken'] = result['idToken']
                        if 'refreshToken' in result:
                            user['refreshToken'] = result['refreshToken']
                        
                        self.email_input.setText(new_email)
                        show_notification("Success", "Email updated successfully.")
                    else:
                        show_notification("Error", "Failed to update email.")
                else:
                    # Email not verified, need to send verification
                    verification_result = self.parent.fdb.send_email_verification(user['idToken'])
                    
                    if verification_result == True:
                        show_notification("Verification Required", 
                                        "A verification email has been sent to your current email. Please verify it and try again.")
                    elif verification_result == "RATE_LIMITED":
                        show_notification("Rate Limited", 
                                        "Too many verification attempts. Please wait 15-30 minutes before trying again, or check your email for existing verification messages.")
                    else:
                        show_notification("Error", "Failed to send verification email.")
            else:
                show_notification("Error", "Not logged in.")
    def change_password(self):
        # First, ask for current password for re-authentication
        current_password, ok1 = QInputDialog.getText(self, "Current Password", "Enter your current password:", QLineEdit.EchoMode.Password)
        if not (ok1 and current_password):
            return
        
        new_password, ok2 = QInputDialog.getText(self, "Change Password", "Enter new password:", QLineEdit.EchoMode.Password)
        if ok2 and new_password:
            user = self.parent.get_current_user()
            if user and 'email' in user:
                # Re-authenticate user first
                reauth_result = self.parent.fdb.reauthenticate_user(user['email'], current_password)
                if reauth_result:
                    # Use the fresh token from re-authentication
                    result = self.parent.fdb.update_user_password(reauth_result['idToken'], new_password)
                    if result:
                        # Update user data with new tokens
                        if 'idToken' in result:
                            user['idToken'] = result['idToken']
                        if 'refreshToken' in result:
                            user['refreshToken'] = result['refreshToken']
                        
                        # Save updated user data
                        # self.parent.save_current_user(user)
                        
                        show_notification("Success", "Password updated successfully.")
                    else:
                        show_notification("Error", "Failed to update password.")
                else:
                    show_notification("Error", "Current password is incorrect.")
            else:
                show_notification("Error", "Not logged in.")
    def logout(self):
        self.parent.logout()

    def back(self):
        self.parent.exit_widget()