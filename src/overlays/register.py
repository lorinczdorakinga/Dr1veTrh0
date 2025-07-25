from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QScroller, QFrame
from PyQt6.QtGui import QPainter, QColor, QPalette, QFont
from PyQt6.QtCore import Qt

from src.components.overlay_button import OverlayButton
from src.components.overlay_label import OverlayLabel
from src.core.logic.abstract_functions import get_resource_path

class Register(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)