# main application file
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QButtonGroup
from gui.menu_window import Menu

def main():
    app = QApplication(sys.argv)

    window = Menu()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
    