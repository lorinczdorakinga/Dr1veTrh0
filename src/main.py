import sys
import os
from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app, db

# Add the parent directory of 'src' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QButtonGroup



def main() -> None:
    app = QApplication(sys.argv)

    load_dotenv()
    cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    db_url = os.getenv('FIREBASE_DATABASE_URL')
    if not cred_path or not db_url:
        raise ValueError("Environment variables FIREBASE_CREDENTIALS_PATH and FIREBASE_DATABASE_URL must be set.")
    cred = credentials.Certificate(cred_path)
    initialize_app(cred, {'databaseURL': db_url})
    
    from src.scenes.menu.menu_window import Menu
    window = Menu()

    window.show()

    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()