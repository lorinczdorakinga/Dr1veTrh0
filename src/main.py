import sys
import os

# Add project root to sys.path *before* any src imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now safe to import from src
from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app, db
from src.core.logic.sound_manager import SoundManager
from PyQt6.QtWidgets import QApplication
import logging


def main():
    # Increase FFmpeg tolerance for MP3s
    os.environ['FFMPEG_ANALYZEDURATION'] = '10000000'
    os.environ['FFMPEG_PROBESIZE'] = '10000000'
    os.environ['QT_LOGGING_RULES'] = 'qt.multimedia*=false'
   
    logging.getLogger('absl').setLevel(logging.ERROR)
    logging.getLogger().setLevel(logging.ERROR)

    app = QApplication(sys.argv)
    load_dotenv()
    cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    db_url = os.getenv('FIREBASE_DATABASE_URL')
    if not cred_path or not db_url:
        raise ValueError("Environment variables FIREBASE_CREDENTIALS_PATH and FIREBASE_DATABASE_URL must be set.")
    cred = credentials.Certificate(cred_path)
    initialize_app(cred, {'databaseURL': db_url})
    sound_manager = SoundManager.get_instance(None)
    from src.scenes.menu.menu_window import Menu
    window = Menu(sound_manager=sound_manager, parent=None)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()