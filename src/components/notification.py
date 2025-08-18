from PyQt6.QtWidgets import QApplication, QMessageBox
import sys
from PyQt6.QtCore import QTimer

from src.core.logic.sound_manager import SoundManager

def show_notification(title, message):
    msg = QMessageBox()  # Create a QMessageBox instance
    sound_manager = SoundManager.get_instance()

    msg.setIcon(QMessageBox.Icon.Information)  # Set the icon
    msg.setText(message)  # Set the message text
    msg.setWindowTitle(title)  # Set the title
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)  # Add an OK button
    msg.buttonClicked.connect(lambda button: 
        QTimer.singleShot(0, lambda: sound_manager.play_effect(sound_manager.button_click)) if button.text() == "OK" else None)

    if sound_manager:
        if title == "Error":
            QTimer.singleShot(0, lambda: sound_manager.play_effect(sound_manager.error_notify))
        elif title == "Success":
            QTimer.singleShot(0, lambda: sound_manager.play_effect(sound_manager.success_notify))
    else:
        print("Warning: No SoundManager, cannot play notification sound")

    msg.exec()  # Show the message box

