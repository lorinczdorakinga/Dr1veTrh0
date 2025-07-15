from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtGui import QPainter, QColor, QPalette
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QHBoxLayout, QStackedLayout, QFrame
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import QPoint, QTimer, QEvent
from gui.game_elements.overlay_button import OverlayButton

class GameModes(QWidget):
    
    default_mode_selected = pyqtSignal()
    reverse_mode_selected = pyqtSignal()
    double_trouble_mode_selected = pyqtSignal()
    speedrun_mode_selected = pyqtSignal()
    
    def __init__(self, parent=None):
        # Setup
        super().__init__(parent)
        self.parent = parent
        
        # Configure the widget to appear as an overlay
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # No window frame
        self.active_mode = None
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 0))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        # Get parent size safely - handle both attribute and method cases
        if parent:
            # Use a more reliable method to get parent dimensions
            parent_rect = self.parent.geometry()
            self.resize(parent_rect.width(), parent_rect.height())
        else:
            self.resize(1280, 960)
            
        # Move to top-left corner to cover the entire parent widget
        self.move(0, 0)
        
        self.setupUI()
        self.connectSignals()
        
        # Install event filter on self to handle clicks outside buttons
        self.installEventFilter(self)
        
    def setupUI(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)  # Add some margins
        
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        
        # Left spacer to push buttons right
        spacer_widget = QWidget()
        spacer_widget.setFixedWidth(400)  # This sets the left margin you wanted
        buttons_layout.addWidget(spacer_widget)
        
        # Buttons Column Container
        buttons_column = QWidget()
        buttons_column_layout = QVBoxLayout(buttons_column)
        buttons_column_layout.setSpacing(20)  # Space between buttons
        
        # Create mode buttons
        self.default_mode_button = OverlayButton("Default", self)
        self.reverse_mode_button = OverlayButton("Reverse", self)
        self.double_trouble_mode_button = OverlayButton("Double trouble", self)
        self.speedrun_mode_button = OverlayButton("Speedrun", self)
        
        # Add buttons to the column layout
        buttons_column_layout.addStretch()  # Push buttons to top of column
        buttons_column_layout.addWidget(self.default_mode_button)
        buttons_column_layout.addWidget(self.reverse_mode_button)
        buttons_column_layout.addWidget(self.double_trouble_mode_button)
        buttons_column_layout.addWidget(self.speedrun_mode_button)
        
        # Add the buttons column to the buttons container
        buttons_layout.addWidget(buttons_column, alignment=Qt.AlignmentFlag.AlignLeft)
        buttons_layout.addStretch()  # Push buttons to left of container
        
        layout.addStretch(1)
        layout.addWidget(buttons_container)
        layout.addStretch(1)
        # Initialize default mode active
        self._apply_default_mode()

        # Store references to buttons for event filtering
        self.buttons = [
            self.default_mode_button,
            self.reverse_mode_button,
            self.double_trouble_mode_button,
            self.speedrun_mode_button
        ]
    
    def connectSignals(self):
        "Connect button clicked events to handlers"
        self.default_mode_button.clicked.connect(self._handle_default_mode_click)
        self.reverse_mode_button.clicked.connect(self._handle_reverse_mode_click)
        self.double_trouble_mode_button.clicked.connect(self._handle_double_trouble_mode_click)
        self.speedrun_mode_button.clicked.connect(self._handle_speedrun_mode_click)
    
    def _handle_default_mode_click(self):
        if self.active_mode != "default":
            self._apply_default_mode()
            self.default_mode_selected.emit()

    def _handle_reverse_mode_click(self):
        if self.active_mode != "reverse":
            self._apply_reverse_mode()
            self.reverse_mode_selected.emit()

    def _handle_double_trouble_mode_click(self):
        if self.active_mode != "double_trouble":
            self._apply_double_trouble_mode()
            self.double_trouble_mode_selected.emit()

    def _handle_speedrun_mode_click(self):
        if self.active_mode != "speedrun":
            self._apply_speedrun_mode()
            self.speedrun_mode_selected.emit()
            
    def showEvent(self, event):
        """Ensure the overlay is properly sized when shown"""
        if self.parent:
            # Use reliable method to get parent dimensions
            parent_rect = self.parent.geometry()
            self.resize(parent_rect.width(), parent_rect.height())
        super().showEvent(event)
    
    def eventFilter(self, obj, event):
        """Filter events to detect clicks outside buttons"""
        if obj == self and event.type() == QEvent.Type.MouseButtonPress:
            # Get mouse position
            mouse_pos = event.position().toPoint()
            
            # Check if click is on any button
            for button in self.buttons:
                button_rect = button.geometry()
                if button_rect.contains(mouse_pos):
                    # Click is on a button, let the normal event handling proceed
                    return False
            
            # Click is outside buttons, hide the overlay
            if hasattr(self.parent, 'game_modes_button') and self.parent.game_modes_button:
                self.parent.game_modes_button.setDefaultStyle()
            self.hide()
            return True  # Event handled
            
        # Let other events pass through
        return super().eventFilter(obj, event)

    def activate_default_mode(self):
        """Activate default mode for external callers"""
        if self.active_mode != "default":
            self._apply_default_mode()
    
    def activate_reverse_mode(self):
        """Activate reverse mode for external callers"""
        if self.active_mode != "reverse":
            self._apply_reverse_mode()
    
    def activate_double_trouble_mode(self):
        """Activate double trouble mode for external callers"""
        if self.active_mode != "double_trouble":
            self._apply_double_trouble_mode()
    
    def activate_speedrun_mode(self):
        """Activate speedrun mode for external callers"""
        if self.active_mode != "speedrun":
            self._apply_speedrun_mode()

    def _apply_default_mode(self):
        """Apply default mode styling"""
        self.reset_button_styles()
        self.default_mode_button.setChosenStyle()
        self.active_mode = "default"
        print("Default mode activated")
    
    def _apply_reverse_mode(self):
        """Apply reverse mode styling"""
        self.reset_button_styles()
        self.reverse_mode_button.setChosenStyle()
        self.active_mode = "reverse"
        print("Reverse mode activated")
    
    def _apply_double_trouble_mode(self):
        """Apply double trouble mode styling"""
        self.reset_button_styles()
        self.double_trouble_mode_button.setChosenStyle()
        self.active_mode = "double_trouble"
        print("Double trouble mode activated")
    
    def _apply_speedrun_mode(self):
        """Apply speedrun mode styling"""
        self.reset_button_styles()
        self.speedrun_mode_button.setChosenStyle()
        self.active_mode = "speedrun"
        print("Speedrun mode activated")
    
    def reset_button_styles(self):
        """Reset all button styles to default"""
        self.default_mode_button.setDefaultStyle()
        self.reverse_mode_button.setDefaultStyle()
        self.double_trouble_mode_button.setDefaultStyle()
        self.speedrun_mode_button.setDefaultStyle()