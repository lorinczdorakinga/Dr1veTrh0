from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QTimer

def show_notification(title, message, sound_manager=None):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setText(message)
    msg.setWindowTitle(title)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    
    if sound_manager:
        msg.buttonClicked.connect(lambda button: 
            QTimer.singleShot(0, lambda: sound_manager.play_effect(sound_manager.button_click)) if button.text() == "OK" else None)
        
        if title == "Error":
            QTimer.singleShot(0, lambda: sound_manager.play_effect(sound_manager.error_notify))
        elif title == "Success":
            QTimer.singleShot(0, lambda: sound_manager.play_effect(sound_manager.success_notify))
    else:
        print("Warning: No SoundManager, cannot play notification sound")

    msg.exec()