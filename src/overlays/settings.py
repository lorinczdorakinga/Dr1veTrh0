# Modified src/overlays/settings.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QSlider, QSpinBox, QMessageBox
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt, QSettings

from src.components.overlay_label import OverlayLabel
from src.components.overlay_button import OverlayButton
from src.components.notification import show_notification
from src.core.logic.sound_manager import SoundManager

class SettingsPage(QWidget):
    def __init__(self, parent=None, sound_manager=None):
        super().__init__(parent)
        self.parent = parent
        self.sound_manager = sound_manager or SoundManager.get_instance()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 200))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.settings = QSettings("Th1nkItThr0", "Dr1veThr0")
        self._setup_ui()
        self._initialize_elements()
        self._load_settings()
        self.initial_settings = {
            "music_enabled": self.music_checkbox.isChecked(),
            "music_volume": self.music_slider.value(),
            "sfx_enabled": self.sfx_checkbox.isChecked(),
            "sfx_volume": self.sfx_slider.value(),
            "custom_time": self.custom_spinbox.value()
        }

    def _setup_ui(self):
        self.main_widget = QWidget(self)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        main_container_layout = QVBoxLayout(self)
        main_container_layout.setContentsMargins(0, 0, 0, 0)
        main_container_layout.addWidget(self.main_widget)
        self.setLayout(main_container_layout)

    def _initialize_elements(self):
        central_width = 500
        central_widget = QWidget()
        central_widget.setFixedWidth(central_width)
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #222222;
                border-radius: 15px;
                border: none;
            }
        """)

        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(20, 20, 20, 20)
        central_layout.setSpacing(20)

        self.title_label = OverlayLabel("Settings")
        font = QFont("Comic Sans MS", 24, QFont.Weight.Bold)
        self.title_label.setFont(font)
        self.title_label.setTextColor("white")
        central_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        audio_subtitle = OverlayLabel("Audio Settings")
        font = QFont("Comic Sans MS", 14, QFont.Weight.Bold)
        audio_subtitle.setFont(font)
        audio_subtitle.setTextColor("white")
        central_layout.addWidget(audio_subtitle, alignment=Qt.AlignmentFlag.AlignCenter)

        music_layout = QHBoxLayout()
        self.music_checkbox = QCheckBox("Enable Music")
        self.music_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-family: "Comic Sans MS";
                font-size: 14pt;
            }
        """)
        music_layout.addWidget(self.music_checkbox)
        self.music_slider = QSlider(Qt.Orientation.Horizontal)
        self.music_slider.setRange(0, 100)
        self.music_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #555;
                height: 4px;
                background: #333;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #FFD700;
                border: 1px solid #555;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
        music_layout.addWidget(self.music_slider)
        central_layout.addLayout(music_layout)

        sfx_layout = QHBoxLayout()
        self.sfx_checkbox = QCheckBox("Enable SFX")
        self.sfx_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-family: "Comic Sans MS";
                font-size: 14pt;
            }
        """)
        sfx_layout.addWidget(self.sfx_checkbox)
        self.sfx_slider = QSlider(Qt.Orientation.Horizontal)
        self.sfx_slider.setRange(0, 100)
        self.sfx_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #555;
                height: 4px;
                background: #333;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #FFD700;
                border: 1px solid #555;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
        sfx_layout.addWidget(self.sfx_slider)
        central_layout.addLayout(sfx_layout)

        custom_layout = QVBoxLayout()
        custom_label = OverlayLabel("Custom Mode Time (seconds):")
        font = QFont("Comic Sans MS", 14)
        custom_label.setFont(font)
        custom_label.setTextColor("white")
        custom_layout.addWidget(custom_label)
        self.custom_spinbox = QSpinBox()
        self.custom_spinbox.setRange(5, 600)
        self.custom_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 10px;
                padding: 5px;
                font-family: "Comic Sans MS";
                font-size: 14pt;
            }
        """)
        custom_layout.addWidget(self.custom_spinbox)
        central_layout.addLayout(custom_layout)

        save_button = OverlayButton("Save Changes", sound_manager=self.sound_manager)
        save_button.clicked.connect(self.save_changes)
        central_layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignCenter)

        back_button = OverlayButton("Back", sound_manager=self.sound_manager)
        back_button.clicked.connect(self.back)
        central_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addStretch(1)
        horizontal_layout.addWidget(central_widget)
        horizontal_layout.addStretch(1)

        self.main_layout.addStretch(1)
        self.main_layout.addLayout(horizontal_layout)
        self.main_layout.addStretch(1)

    def _load_settings(self):
        self.music_checkbox.setChecked(self.sound_manager.music_enabled)
        self.music_slider.setValue(int(self.sound_manager.music_volume * 100))
        self.sfx_checkbox.setChecked(self.sound_manager.sfx_enabled)
        self.sfx_slider.setValue(int(self.sound_manager.sfx_volume * 100))
        self.custom_spinbox.setValue(self.settings.value("custom_time", 60, type=int))

    def has_changes(self):
        current_settings = {
            "music_enabled": self.music_checkbox.isChecked(),
            "music_volume": self.music_slider.value(),
            "sfx_enabled": self.sfx_checkbox.isChecked(),
            "sfx_volume": self.sfx_slider.value(),
            "custom_time": self.custom_spinbox.value()
        }
        return current_settings != self.initial_settings

    def save_changes(self):
        self.sound_manager.music_enabled = self.music_checkbox.isChecked()
        self.sound_manager.sfx_enabled = self.sfx_checkbox.isChecked()
        self.sound_manager.music_volume = self.music_slider.value() / 100.0
        self.sound_manager.sfx_volume = self.sfx_slider.value() / 100.0
        self.settings.setValue("custom_time", self.custom_spinbox.value())
        self._apply_settings()
        show_notification("Success", "Settings saved successfully.")
        self.initial_settings = {
            "music_enabled": self.music_checkbox.isChecked(),
            "music_volume": self.music_slider.value(),
            "sfx_enabled": self.sfx_checkbox.isChecked(),
            "sfx_volume": self.sfx_slider.value(),
            "custom_time": self.custom_spinbox.value()
        }
        self.hide()

    def _apply_settings(self):
        if self.sound_manager.music_enabled:
            parent_class_name = self.parent.__class__.__name__ if self.parent else None
            if parent_class_name == "Menu":
                self.sound_manager.play_music(self.sound_manager.lobby_music)
            else:
                self.sound_manager.play_music(self.sound_manager.in_game_music)
        else:
            self.sound_manager.stop_all()
        if self.parent:
            self.parent.custom_time = self.custom_spinbox.value()

    def back(self):
        if self.has_changes():
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Question)
            msg.setText("You have unsaved changes. Do you want to save them?")
            msg.setWindowTitle("Unsaved Changes")
            msg.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if self.sound_manager:
                msg.buttonClicked.connect(lambda button: self.sound_manager.play_effect(self.sound_manager.button_click))
            ret = msg.exec()
            if ret == QMessageBox.StandardButton.Save:
                self.save_changes()
            elif ret == QMessageBox.StandardButton.Discard:
                self.hide()
            # Cancel does nothing
        else:
            self.hide()

    def showEvent(self, event):
        if self.parent:
            self.setGeometry(self.parent.geometry())
        super().showEvent(event)

    def mousePressEvent(self, event):
        self.sound_manager.button_click.play()
        self.hide()