from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QInputDialog, QLineEdit, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QFont, QPixmap, QColor
from PyQt6.QtCore import Qt, QTimer

from src.components.overlay_label import OverlayLabel
from src.components.overlay_button import OverlayButton
from src.components.notification import show_notification
from src.core.logic.abstract_functions import get_resource_path

class UserPage(QWidget):
    def __init__(self, parent=None, sound_manager=None):
        super().__init__(parent)
        self.parent = parent
        self.sound_manager = sound_manager
        self._setup_ui()
        self._initialize_elements()

    def _setup_ui(self):
        self.main_widget = QWidget(self)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        main_container_layout = QVBoxLayout(self)
        main_container_layout.setContentsMargins(0, 0, 0, 0)
        main_container_layout.addWidget(self.main_widget)
        self.setLayout(main_container_layout)

    def _initialize_elements(self):
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

        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(20, 20, 20, 20)
        central_layout.setSpacing(20)

        self.title_label = OverlayLabel("User Profile")
        font = QFont("Comic Sans MS", 24, QFont.Weight.Bold)
        self.title_label.setFont(font)
        self.title_label.setTextColor("white")

        self.username_label = OverlayLabel("Loading...")
        font = QFont("Comic Sans MS", 22, QFont.Weight.Bold)
        self.username_label.setFont(font)
        self.username_label.setTextColor(QColor("#FFD700"))
        self.username_label.setStyleSheet("background-color: #333; padding: 10px; border-radius: 10px;")
        self.username_label.setWordWrap(True)

        highscores_subtitle = OverlayLabel("High Scores")
        font = QFont("Comic Sans MS", 14, QFont.Weight.Bold)
        highscores_subtitle.setFont(font)
        highscores_subtitle.setTextColor("white")

        self.scores_label = OverlayLabel("Loading...")
        font = QFont("Comic Sans MS", 26, QFont.Weight.Light)       
        self.scores_label.setFont(font)
        self.scores_label.setTextColor("white")
        self.scores_label.setStyleSheet("background-color: #333; padding: 10px; border-radius: 10px;")
        self.scores_label.setWordWrap(True)
        self.scores_label.setMinimumHeight(200)
        self.scores_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)  # Explicitly set both
        self.scores_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)  # Prevent vertical expansion
        
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
        
        change_email_button = OverlayButton("Change Email", sound_manager=self.sound_manager)
        change_email_button.clicked.connect(self.parent.switch_to_change_email)
        email_layout.addWidget(change_email_button, stretch=0)

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

        change_password_button = OverlayButton("Change Password", sound_manager=self.sound_manager)
        change_password_button.clicked.connect(self.parent.switch_to_change_password)
        password_layout.addWidget(change_password_button, stretch=0)

        logout_button = OverlayButton("Log Out", sound_manager=self.sound_manager)
        logout_button.clicked.connect(self.logout)
        logout_button.setFixedWidth(200)

        back_button = OverlayButton("Back", sound_manager=self.sound_manager)
        back_button.clicked.connect(self.back) 
        back_button.setFixedWidth(200)

        central_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        central_layout.addWidget(self.username_label, alignment=Qt.AlignmentFlag.AlignCenter)
        central_layout.addSpacerItem(QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        central_layout.addWidget(highscores_subtitle, alignment=Qt.AlignmentFlag.AlignHCenter)
        central_layout.addWidget(self.scores_label, alignment=Qt.AlignmentFlag.AlignCenter)
        central_layout.addSpacerItem(QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        central_layout.addWidget(email_subtitle, alignment=Qt.AlignmentFlag.AlignLeft)
        central_layout.addLayout(email_layout)
        central_layout.addSpacerItem(QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        central_layout.addWidget(password_subtitle, alignment=Qt.AlignmentFlag.AlignLeft)
        central_layout.addLayout(password_layout)
        central_layout.addSpacerItem(QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        central_layout.addWidget(logout_button, alignment=Qt.AlignmentFlag.AlignCenter)
        central_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        scroll_area = QScrollArea()
        scroll_area.setWidget(central_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedWidth(central_width + 20)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addStretch(1)
        horizontal_layout.addWidget(scroll_area)
        horizontal_layout.addStretch(1)

        self.main_layout.addSpacerItem(QSpacerItem(0, 100, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        self.main_layout.addLayout(horizontal_layout)
        self.main_layout.addSpacerItem(QSpacerItem(0, 200, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

    def update_user_data(self):
        user = self.parent.get_current_user()
        if user and self.parent.fdb:
            # Fetch the latest user records from Firebase
            scores = self.parent.fdb.get_user_records(user['localId'])
            if scores:
                user.update(scores)  # Merge Firebase records into current_user
                self.username_label.setText(user.get('displayName', user['email']))
                self.email_input.setText(user['email'])
                scores_text = ""
                for key, value in scores.items():
                    if key.endswith("_mode_highscore"):
                        formatted_key = key.replace("_mode_highscore", "").replace("_", " ").title()
                        scores_text += f"{formatted_key}: {value}\n"
                if not scores_text:
                    scores_text = "No highscores available."
            else:
                scores_text = "Unable to fetch highscores."
                print("Warning: Failed to fetch user records from Firebase.")
            self.scores_label.setText(scores_text)
        else:
            self.username_label.setText("Not logged in")
            self.email_input.setText("Not logged in")
            self.scores_label.setText("Not logged in")
            print("Warning: No user or FirebaseCRUD instance available.")
    
    def logout(self):
        self.parent.logout()
        self.scores_label.setText("Not logged in")  # Clear scores on logout

    def back(self):
        self.parent.exit_widget()

    def mousePressEvent(self, event):
        if self.sound_manager:
            self.sound_manager.play_effect(self.sound_manager.button_click)
        self.parent.hide()