from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QSize
from PyQt6.QtGui import QPalette, QColor
from src.components.overlay_button import OverlayButton

class GameModes(QWidget):
    mode_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.active_mode = None
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAutoFillBackground(True)
        self.setPalette(QPalette(QColor(0, 0, 0, 0)))
        self.resize(parent.geometry().size() if parent else QSize(1280, 960))
        self.move(0, 0)
        self.setupUI()
        self.installEventFilter(self)

    def setupUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.addWidget(QWidget(), stretch=1)
        buttons_column = QWidget()
        buttons_column_layout = QVBoxLayout(buttons_column)
        buttons_column_layout.setSpacing(20)

        self.mode_buttons = {
            "default": OverlayButton("Default", self),
            "reverse": OverlayButton("Reverse", self),
            "double_trouble": OverlayButton("Double trouble", self),
            "speedrun": OverlayButton("Speedrun", self)
        }

        for mode, button in self.mode_buttons.items():
            button.clicked.connect(lambda checked, m=mode: self._handle_mode_click(m))
            buttons_column_layout.addWidget(button)

        buttons_layout.addWidget(buttons_column)
        buttons_layout.addStretch()
        layout.addStretch(1)
        layout.addWidget(buttons_container)
        layout.addStretch(1)
        self.set_active_mode("default")

    def _handle_mode_click(self, mode):
        if self.active_mode != mode:
            self._apply_mode(mode)
            self.mode_selected.emit(mode)

    def set_active_mode(self, mode):
        if mode in self.mode_buttons:
            self._apply_mode(mode)

    def _apply_mode(self, mode):
        self.reset_button_styles()
        self.mode_buttons[mode].setChosenStyle()
        self.active_mode = mode

    def reset_button_styles(self):
        for button in self.mode_buttons.values():
            button.setDefaultStyle()

    def eventFilter(self, obj, event):
        if obj == self and event.type() == QEvent.Type.MouseButtonPress:
            mouse_pos = event.position().toPoint()
            for button in self.mode_buttons.values():
                if button.geometry().contains(mouse_pos):
                    return False
            self.hide()
            return True
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        if self.parent:
            self.resize(self.parent.geometry().size())
        super().showEvent(event)