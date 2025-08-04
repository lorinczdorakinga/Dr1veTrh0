from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt, QSettings, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
import pyrebase

from src.core.logic.firebase_crud import FirebaseCRUD
from src.components.login import UserAuth
from src.components.user_page import UserPage
from src.components.register import Register
from src.components.forgot_password import ForgotPassword

class AuthHandler(QMainWindow):
    user_logged_in = pyqtSignal()
    user_logged_out = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_user = None
        self.fdb = FirebaseCRUD()
        self.settings = QSettings("Th1nkItThr0", "Dr1veThr0")
        self.setup_ui()
        self.stacked_layout_initialization()
        self.load_session()
        self.hide()

    def setup_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 200))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        parent_rect = self.parent.geometry() if self.parent else self.geometry()
        self.resize(parent_rect.width(), parent_rect.height())
        self.move(0, 0)

    def stacked_layout_initialization(self):
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)

        self.login_page = UserAuth(self)
        self.register_page = Register(self)
        self.user_page = UserPage(self)
        self.forgot_password_page = ForgotPassword(self)

        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.forgot_password_page)
        self.stacked_widget.addWidget(self.register_page)
        self.stacked_widget.addWidget(self.user_page)

    def showEvent(self, event):
        if self.parent:
            self.setGeometry(self.parent.geometry())
        super().showEvent(event)

    def load_session(self):
        refresh_token = self.settings.value("refresh_token", defaultValue=None)
        if refresh_token:
            refreshed = self.fdb.refresh_user(refresh_token)
            if refreshed and 'idToken' in refreshed:
                id_token = refreshed['idToken']
                account_info = self.fdb.get_account_info(id_token)
                if account_info and 'users' in account_info and len(account_info['users']) > 0:
                    user_details = account_info['users'][0]
                    user = {
                        'idToken': id_token,
                        'refreshToken': refreshed['refreshToken'],
                        'localId': user_details['localId'],
                        'email': user_details['email'],
                        'displayName': user_details.get('displayName', '')
                    }
                    self.set_current_user(user)
                    self.user_page.update_user_data()  # Ensure data is updated on session load
                    self.switch_to_user_page()
                    self.user_logged_in.emit()
                else:
                    print("No user info found or invalid account info")
                    self.settings.remove("refresh_token")
                    self.switch_to_login()
            else:
                print("Token refresh failed or invalid refresh response")
                self.settings.remove("refresh_token")
                self.switch_to_login()
        else:
            self.switch_to_login()

    def set_current_user(self, user):
        self.current_user = user
        self.settings.setValue("refresh_token", user['refreshToken'])

    def get_current_user(self):
        return self.current_user

    def logout(self):
        self.current_user = None
        self.settings.remove("refresh_token")
        self.switch_to_login()
    def is_user_logged_in(self):
        return self.current_user is not None and 'idToken' in self.current_user

    def switch_to_login(self):
        self.stacked_widget.setCurrentWidget(self.login_page)

    def switch_to_register(self):
        self.stacked_widget.setCurrentWidget(self.register_page)
    
    def switch_to_forgot_password(self):
        self.stacked_widget.setCurrentWidget(self.forgot_password_page)

    def switch_to_user_page(self):
        self.stacked_widget.setCurrentWidget(self.user_page)

    def exit_widget(self):
        self.close()