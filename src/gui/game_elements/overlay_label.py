from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QSize

class OverlayLabel(QLabel):
    def __init__(self, text, parent=None, path=None):
        super().__init__(parent)
        self.setMinimumSize(200, 60)
        self.text = text
        self.textColor = QColor("white")  # Default text color
        self.background_img = QPixmap()

        # Set font properly
        font = QFont()
        font.setFamily("Comic Sans MS")
        font.setPointSize(28)
        font.setBold(True)
        self.setFont(font)

        if path:
            self.background_img.load(path)

        # Apply styling
        if path:
            self.setStyleSheet("""
                QLabel {
                    background-color: white;
                    color: white;
                    border: 3px solid white;
                    border-radius: 15px;
                    padding: 10px;
                    font-family: "Comic Sans MS";
                    font-weight: bold;
                    font-size: 28pt;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    color: white;
                    padding: 10px;
                    font-family: "Comic Sans MS";
                    font-weight: bold;
                    font-size: 28pt;
                }
            """)

        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Preferred
        )

    def setText(self, text):
        self.text = text
        self.adjustSize()
        self.updateGeometry()
        self.update()

    def setTextColor(self, color):
        self.textColor = QColor(color)
        self.update()

    def sizeHint(self):
        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(self.text) + 40  # extra padding
        text_height = fm.height() + 20
        return QSize(text_width, text_height)

    def minimumSizeHint(self):
        return self.sizeHint()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Draw background image if available
        if not self.background_img.isNull():
            painter.drawPixmap(
                self.rect(),
                self.background_img.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )

        # Draw text with current text color
        painter.setFont(self.font())
        painter.setPen(self.textColor)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text)