from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QSize
from PyQt6.QtGui import QPalette, QColor
from src.components.overlay_button import OverlayButton
from src.core.logic.sound_manager import SoundManager
from src.core.logic.abstract_functions import did_user_pay
from src.components.paywall_notification import show_paywall_notification

class GameModes(QWidget):
    mode_selected = pyqtSignal(str)

    def __init__(self, parent=None, sound_manager=None):
        super().__init__(parent)
        self.parent = parent
        self.sound_manager = sound_manager or SoundManager.get_instance(parent)
        self.active_mode = None
        self.payed_user = did_user_pay()
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
        if self.parent:    
            parent_rect = self.parent.geometry()
            self.resize(parent_rect.width(), parent_rect.height())
            self.move(0, 0)

        self.mode_buttons = {
            "default": OverlayButton("Default", parent=self, sound_manager=self.sound_manager),
            "reverse": OverlayButton("Reverse", parent=self, sound_manager=self.sound_manager),
            "double_trouble": OverlayButton("Double trouble", parent=self, sound_manager=self.sound_manager),
            "speedrun": OverlayButton("Speedrun", parent=self, sound_manager=self.sound_manager)
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
        if mode in ["reverse", "double_trouble", "speedrun"] and not self.payed_user:
            result = show_paywall_notification(
                "Error",
                "You need to purchase this feature to access it.",
                parent=self.parent
            )
            print("User chose:", result)
            if result == 'imin':
                self.payed_user = True; self.reset_button_styles()
            return
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
        if not self.payed_user:
            self.mode_buttons["default"].setDefaultStyle()
            for mode in ["reverse", "double_trouble", "speedrun"]:
                self.mode_buttons[mode].setDisabledStyle()
        else:
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