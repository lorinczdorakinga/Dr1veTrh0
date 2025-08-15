from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QScroller, QFrame
from PyQt6.QtGui import QPainter, QColor, QPalette, QFont
from PyQt6.QtCore import Qt
from src.components.overlay_button import OverlayButton
from src.components.overlay_label import OverlayLabel
from src.core.logic.abstract_functions import get_resource_path

class Help(QWidget):
    def __init__(self, parent=None, sound_manager=None):
        super().__init__(parent)
        self.parent = parent
        self.sound_manager = sound_manager
        self.path = get_resource_path("text")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 230))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        parent_rect = self.parent.geometry() if self.parent else self.geometry()
        self.resize(parent_rect.width(), parent_rect.height())
        self.move(0, 0)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)

        self.title_label = OverlayLabel("Instrukciók")
        font = self.title_label.font()
        font.setUnderline(True)
        self.title_label.setFont(font)
        self.title_label.setTextColor("white")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(self.title_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_palette = scroll_area.palette()
        scroll_palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 0))
        scroll_area.setPalette(scroll_palette)
        scroll_area.setAutoFillBackground(True)
        scroll_area.setStyleSheet("border: none;")
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        QScroller.grabGesture(scroll_area.viewport(), QScroller.ScrollerGestureType.LeftMouseButtonGesture)

        content_widget = QWidget()
        scroll_layout = QVBoxLayout(content_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)

        try:
            with open(self.path + "/instructionsHU.txt", "r", encoding="utf-8") as file:
                instructions_text = file.read()
        except Exception as e:
            instructions_text = "Could not load instructions.txt:\n" + str(e)

        self.instructions_label = OverlayLabel(instructions_text)
        self.instructions_label.setStyleSheet("font-size: 18pt;")
        self.instructions_label.setWordWrap(True)
        self.instructions_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        scroll_layout.addWidget(self.instructions_label)
        scroll_area.setWidget(content_widget)

        self.back_button = OverlayButton("Back", parent=self, sound_manager=self.sound_manager)
        self.back_button.setFixedSize(300, 80)
        self.back_button.clicked.connect(self.parent.help_fn)
        
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)