from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from src.core.logic.abstract_functions import get_resource_path
from src.components.notification import show_notification
from src.core.logic.firebase_crud import FirebaseCRUD
from src.components.overlay_button import OverlayButton
from src.components.overlay_label import OverlayLabel

class ChangeEmail(QWidget):
    def __init__(self, parent=None, sound_manager=None):
        super().__init__(parent)
        self.parent = parent
        self.sound_manager = sound_manager
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

        self.title_label = OverlayLabel("Change Email")
        font = QFont("Comic Sans MS", 24, QFont.Weight.Bold)
        self.title_label.setFont(font)
        self.title_label.setTextColor("white")
        central_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        email_layout = QHBoxLayout()
        email_icon = QLabel()
        path = get_resource_path("img/email.svg")
        email_icon.setPixmap(QPixmap(path).scaled(24, 24))
        email_layout.addWidget(email_icon, stretch=0)
        self.new_email_input = QLineEdit()
        self.new_email_input.setPlaceholderText("New Email")
        self.new_email_input.setStyleSheet("""
            QLineEdit {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 10px;
                padding: 5px;
                font-family: "Comic Sans MS";
            }
        """)
        email_layout.addWidget(self.new_email_input, stretch=1)
        dummy_label = QLabel()
        dummy_label.setFixedWidth(24)
        email_layout.addWidget(dummy_label, stretch=0)
        central_layout.addLayout(email_layout)

        change_button = OverlayButton("Change Email", sound_manager=self.sound_manager)
        change_button.clicked.connect(self.change_email_fn)
        central_layout.addWidget(change_button, alignment=Qt.AlignmentFlag.AlignCenter)
        central_layout.addStretch()

        back_button = OverlayButton("Back", sound_manager=self.sound_manager)
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

    def change_email_fn(self):
        new_email = self.new_email_input.text().strip()
        if not new_email:
            show_notification("Error", "Please enter a new email address.")
            return

        user = self.parent.get_current_user()
        if user and 'idToken' in user:
            is_verified = self.fdb.check_email_verification_status(user['idToken'])
            
            if is_verified:
                result = self.fdb.update_user_email(user['idToken'], new_email)
                if result:
                    user['email'] = new_email
                    if 'idToken' in result:
                        user['idToken'] = result['idToken']
                    if 'refreshToken' in result:
                        user['refreshToken'] = result['refreshToken']
                    
                    show_notification("Success", "Email updated successfully.")
                    self.back()
                else:
                    show_notification("Error", "Failed to update email.")
            else:
                verification_result = self.fdb.send_email_verification(user['idToken'])
                
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

    def back(self):
        self.parent.switch_to_user_page()

    def mousePressEvent(self, event):
        self.parent.hide()