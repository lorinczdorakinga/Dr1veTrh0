import sys
import os

# Add the parent directory of 'src' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QButtonGroup

from src.scenes.menu.menu_window import Menu

def main() -> None:
    app = QApplication(sys.argv)

    window = Menu()

    window.show()

    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()