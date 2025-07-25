from PyQt6.QtWidgets import QApplication, QMessageBox
import sys
def show_notification(title, message):
    msg = QMessageBox()  # Create a QMessageBox instance
    msg.setIcon(QMessageBox.Icon.Information)  # Set the icon
    msg.setText(message)  # Set the message text
    msg.setWindowTitle(title)  # Set the title
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)  # Add an OK button
    msg.exec()  # Show the message box

