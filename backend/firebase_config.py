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
