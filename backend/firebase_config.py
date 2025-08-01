import sys
import os
from dotenv import load_dotenv

# Add the parent directory of 'src' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QButtonGroup
from src.scenes.menu.menu_window import Menu

# Import firebase_config to initialize Firebase (this will handle initialization)
from backend.firebase_config import firebase_config

def main() -> None:
    app = QApplication(sys.argv)
    
    # Load environment variables (firebase_config will handle Firebase initialization)
    load_dotenv()
    
    # Firebase is already initialized by importing firebase_config
    # No need to initialize again here
    
    window = Menu()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

# ============================================================================
# UPDATED firebase_config.py - Better error handling and singleton pattern
# ============================================================================

import firebase_admin
from firebase_admin import credentials, db
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FirebaseConfig:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.initialize_firebase()
            self._initialized = True

    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            if firebase_admin._apps:
                print("Firebase already initialized, using existing app")
                return
            
            # Get environment variables
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            database_url = os.getenv('FIREBASE_DATABASE_URL')
            
            print(f"Looking for credentials at: {cred_path}")
            print(f"Database URL: {database_url}")
            
            if not cred_path or not database_url:
                raise ValueError("Firebase credentials or database URL not found in environment variables")
            
            # Check if credentials file exists
            if not os.path.exists(cred_path):
                raise FileNotFoundError(f"Credentials file not found at: {cred_path}")
            
            # Initialize the app only if it hasn't been initialized
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            
            print("Firebase initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            raise e

    def get_database_reference(self, path=''):
        """Get database reference for a specific path"""
        return db.reference(path)

# Initialize Firebase when module is imported
firebase_config = FirebaseConfig()

# ============================================================================
# UPDATED firebase_crud.py - Remove duplicate initialization
# ============================================================================

from firebase_admin import db, auth
from backend.firebase_config import firebase_config
from typing import Dict, List, Optional, Any
from backend.firebase_listeners import FirebaseListener
from backend.firebase_exceptions import handle_firebase_error
import time
import os
import uuid
from dotenv import load_dotenv

class FirebaseCRUD:
    def __init__(self):
        # No need to load dotenv or initialize Firebase here
        # firebase_config already handles this
        self.ref = db.reference("/users")

    def create_user(self, email, password, username):
        try:
            # Create user in Firebase Authentication
            user = auth.create_user(
                email=email,
                password=password,
                display_name=username  # Optional: Store username in Firebase Auth
            )
            # Store user data in Realtime Database
            user_ref = db.reference(f'users/{user.uid}')
            user_ref.set({
                'username': username,
                'email': email,
                'password': password,  # Note: Storing passwords in plain text is not secure
                'default_mode_highscore': 0,
                'reverse_mode_highscore': 0,
                'speedrun_mode_highscore': 0,
                'double_trouble_mode_highscore': 0
            })
            print(f"User created with UID: {user.uid}")
            return user
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
        
    def register_user(self, email, password, username):
        # Remove hardcoded values - use the parameters instead
        if not username:
            print("Registration Failed", "Username is required.")
            return
        user = self.create_user(email, password, username)
        return user

    def login_user(self, email, password):
        try:
            # Verify user by email (simplified; use client-side SDK for secure login)
            user = auth.get_user_by_email(email)
            user_ref = db.reference(f'users/{user.uid}')
            user_data = user_ref.get()
            return user, user_data
        except Exception as e:
            print(f"Error logging in: {e}")
            return None, None

    def update_highscore(self, uid, game_mode, score, email):
        try:
            user = auth.get_user_by_email(email)
            user_ref = db.reference(f'users/{user.uid}')
            current_data = user_ref.get()
            current_score = current_data.get(f'{game_mode}_highscore', 0)
            if score > current_score:
                user_ref.update({f'{game_mode}_highscore': score})
                print(f"Updated {game_mode} highscore for user {uid}: {score}")
        except Exception as e:
            print(f"Error updating highscore: {e}")

    # CREATE Operations
    def create(self, data: Dict[str, Any], custom_id: Optional[str] = None) -> str:
        """
        Create a new record in Firebase
        
        Args:
            data: Dictionary containing the data to store
            custom_id: Optional custom ID, if not provided Firebase generates one
            
        Returns:
            The ID of the created record
        """
        try:
            if custom_id:
                self.ref.child(custom_id).set(data)
                return custom_id
            else:
                new_ref = self.ref.push(data)
                return new_ref.key
                
        except Exception as e:
            print(f"Error creating record: {e}")
            raise e
    
    def create_multiple(self, data_list: List[Dict[str, Any]]) -> List[str]:
        """
        Create multiple records at once
        
        Args:
            data_list: List of dictionaries to store
            
        Returns:
            List of created record IDs
        """
        created_ids = []
        try:
            for data in data_list:
                record_id = self.create(data)
                created_ids.append(record_id)
            return created_ids
            
        except Exception as e:
            print(f"Error creating multiple records: {e}")
            raise e
    
    # READ Operations
    def read(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a single record by ID
        
        Args:
            record_id: ID of the record to retrieve
            
        Returns:
            Dictionary containing the record data or None if not found
        """
        try:
            data = self.ref.child(record_id).get()
            return data
            
        except Exception as e:
            print(f"Error reading record {record_id}: {e}")
            return None
    
    def read_all(self) -> Dict[str, Any]:
        """
        Read all records in the collection
        
        Returns:
            Dictionary with all records (key: record_id, value: record_data)
        """
        try:
            data = self.ref.get()
            return data if data else {}
            
        except Exception as e:
            print(f"Error reading all records: {e}")
            return {}
    
    def read_filtered(self, field: str, value: Any, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Read records filtered by field value
        
        Args:
            field: Field name to filter by
            value: Value to filter for
            limit: Optional limit on number of results
            
        Returns:
            Dictionary with filtered records
        """
        try:
            query = self.ref.order_by_child(field).equal_to(value)
            if limit:
                query = query.limit_to_first(limit)
            
            data = query.get()
            return data if data else {}
            
        except Exception as e:
            print(f"Error reading filtered records: {e}")
            return {}
    
    # UPDATE Operations
    def update(self, record_id: str, data: Dict[str, Any]) -> bool:
        """
        Update a record by ID
        
        Args:
            record_id: ID of the record to update
            data: Dictionary containing fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.ref.child(record_id).update(data)
            return True
            
        except Exception as e:
            print(f"Error updating record {record_id}: {e}")
            return False
    
    def update_field(self, record_id: str, field: str, value: Any) -> bool:
        """
        Update a single field in a record
        
        Args:
            record_id: ID of the record to update
            field: Field name to update
            value: New value for the field
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.ref.child(record_id).child(field).set(value)
            return True
            
        except Exception as e:
            print(f"Error updating field {field} in record {record_id}: {e}")
            return False
    
    # DELETE Operations
    def delete(self, record_id: str) -> bool:
        """
        Delete a record by ID
        
        Args:
            record_id: ID of the record to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.ref.child(record_id).delete()
            return True
            
        except Exception as e:
            print(f"Error deleting record {record_id}: {e}")
            return False
    
    def delete_all(self) -> bool:
        """
        Delete all records in the collection
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.ref.delete()
            return True
            
        except Exception as e:
            print(f"Error deleting all records: {e}")
            return False
    
    def delete_filtered(self, field: str, value: Any) -> int:
        """
        Delete records that match a filter condition
        
        Args:
            field: Field name to filter by
            value: Value to filter for
            
        Returns:
            Number of records deleted
        """
        try:
            # First, get the records to delete
            records_to_delete = self.read_filtered(field, value)
            
            if not records_to_delete:
                return 0
            
            # Delete each record
            deleted_count = 0
            for record_id in records_to_delete.keys():
                if self.delete(record_id):
                    deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            print(f"Error deleting filtered records: {e}")
            return 0

# ============================================================================
# UPDATED user_auth.py - Remove hardcoded test registration
# ============================================================================

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QStyle, QPushButton, QHBoxLayout, QLineEdit, QSizePolicy, QFrame
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QFont, QPalette, QBrush, QColor
import sys

from src.core.logic.abstract_functions import get_resource_path
from src.core.logic.firebase_crud import FirebaseCRUD

from src.components.overlay_button import OverlayButton
from src.components.overlay_label import OverlayLabel

from src.components.login import Login
from src.components.forgot_password import ForgotPassword
from src.components.register import Register

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QStackedWidget, QLabel
import sys

class UserAuth(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._setup_ui()
        self._initialize_elements()
        
        # Remove the hardcoded test registration
        # fdb = FirebaseCRUD()
        # fdb.register_user("doralorincz98@gmail.com", "Lokaka", "nagysas")

    def _setup_ui(self):
        """Initialize the basic UI components"""
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 230))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Use self.width() and self.height() to get the dimensions
        parent_rect = self.parent.geometry() if self.parent else self.geometry()
        self.resize(parent_rect.width(), parent_rect.height())

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setSpacing(int(self.height() * 0.02))  # 2% of height
        self.main_layout.setContentsMargins(
            int(self.width() * 0.03), int(self.height() * 0.05),
            int(self.width() * 0.03), int(self.height() * 0.05)
        )  # Responsive margins

        # Only set layout if not already set
        if self.layout() is None:
            main_container_layout = QVBoxLayout(self)
            main_container_layout.addWidget(self.main_widget)
            main_container_layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(main_container_layout)

    def login_fn(self):
        # Get the actual input values
        email = self.username_input.text()  # Assuming this is actually email
        password = self.password_input.text()
        
        if not email or not password:
            print("Please enter both email and password")
            return
            
        fdb = FirebaseCRUD()
        user, user_data = fdb.login_user(email, password)
        
        if user:
            print(f"Login successful for user: {user.email}")
            # Handle successful login (close dialog, navigate to main app, etc.)
            self.close()
        else:
            print("Login failed")
    
    def register_fn(self):
        # Get the actual input values
        email = self.username_input.text()  # Assuming this is actually email
        password = self.password_input.text()
        username = "DefaultUsername"  # You might want to add a username field
        
        if not email or not password:
            print("Please enter both email and password")
            return
            
        fdb = FirebaseCRUD()
        user = fdb.register_user(email, password, username)
        
        if user:
            print(f"Registration successful for user: {user.email}")
            # Handle successful registration
        else:
            print("Registration failed")

    def forgot_password_fn(self):
        self.forgot_password = ForgotPassword()
        self.forgot_password.showFullScreen()

    def back(self):
        self.close()

    # ... rest of the methods remain the same ...