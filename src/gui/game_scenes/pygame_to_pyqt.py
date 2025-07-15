import sys
import pygame
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt
from PyQt6 import QtGui

class PygameWidget(QWidget):
    """
    A QWidget that embeds a Pygame surface
    """
    def __init__(self, parent=None, width=640, height=480):
        super().__init__(parent)
        
        self.setFixedSize(width, height)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        
        if not pygame.get_init():
            pygame.init()
        
        self.surface = pygame.Surface((width, height))
        self.surface.fill((0, 0, 0))
        
        self.rect = self.surface.get_rect()
        
        # Create an update timer (60 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_pygame)
        self.timer.start(16)  # ~60 FPS
        
        self.is_running = True
        self.is_paused = False
        
        # Event handlers and game loop will be implemented by subclasses
        
    def update_pygame(self):
        """Called by the timer to update the Pygame surface and repaint the widget"""
        if self.is_running:
            self.process_pygame_events()
            if not self.is_paused:  # Only update game logic if not paused
                self.update_game_logic()
            self.render_game()
            self.update()
    
    def process_pygame_events(self):
        """Handle Pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
    
    def update_game_logic(self):
        """Update game state - to be overridden by subclasses"""
        pass
    
    def render_game(self):
        """Render game graphics - to be overridden by subclasses"""
        pass
    
    def paintEvent(self, event):
        """Qt paint event - converts Pygame surface to Qt image and draws it"""
        # Convert Pygame surface to a byte array
        surface_data = pygame.image.tostring(self.surface, 'RGB')
        
        # Create QImage from the byte array
        image = QtGui.QImage(surface_data, self.rect.width, self.rect.height, 
                             self.rect.width * 3, QtGui.QImage.Format.Format_RGB888)
        
        # Create a painter to draw the image
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, image)
        painter.end()
    
    def set_paused(self, paused):
        """Set the pause state of the game"""
        self.is_paused = paused
    
    def keyPressEvent(self, event):
        """Handle Qt key press events"""
        key_code = event.key()
        # Map Qt key codes to Pygame key codes
        pygame_event = pygame.event.Event(pygame.KEYDOWN, {'key': key_code})
        pygame.event.post(pygame_event)
    
    def keyReleaseEvent(self, event):
        """Handle Qt key release events"""
        key_code = event.key()
        pygame_event = pygame.event.Event(pygame.KEYUP, {'key': key_code})
        pygame.event.post(pygame_event)
    
    def mousePressEvent(self, event):
        """Handle Qt mouse press events"""
        pos = (event.position().x(), event.position().y())
        button = event.button()
        # Map Qt mouse buttons to Pygame buttons
        button_map = {
            Qt.MouseButton.LeftButton: 1,
            Qt.MouseButton.MiddleButton: 2,
            Qt.MouseButton.RightButton: 3,
        }
        pygame_button = button_map.get(button, 0)
        pygame_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': pos, 'button': pygame_button})
        pygame.event.post(pygame_event)
    
    def mouseReleaseEvent(self, event):
        """Handle Qt mouse release events"""
        pos = (event.position().x(), event.position().y())
        button = event.button()
        button_map = {
            Qt.MouseButton.LeftButton: 1,
            Qt.MouseButton.MiddleButton: 2,
            Qt.MouseButton.RightButton: 3,
        }
        pygame_button = button_map.get(button, 0)
        pygame_event = pygame.event.Event(pygame.MOUSEBUTTONUP, {'pos': pos, 'button': pygame_button})
        pygame.event.post(pygame_event)
    
    def mouseMoveEvent(self, event):
        """Handle Qt mouse move events"""
        pos = (event.position().x(), event.position().y())
        pygame_event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': pos})
        pygame.event.post(pygame_event)
    
    def closeEvent(self, event):
        """Handle widget close event"""
        self.is_running = False
        self.timer.stop()
        super().closeEvent(event)

def pygame_to_qwidget(pygame_app_class):
    class WrappedPygameWidget(PygameWidget):
        def __init__(self, parent=None, width=640, height=480, *args, **kwargs):
            super().__init__(parent, width, height)
            
            # Modify initialization to handle different constructor patterns
            if hasattr(pygame_app_class, '__init__'):
                if pygame_app_class.__init__.__code__.co_argcount > 1:
                    # Class accepts parameters
                    self.pygame_app = pygame_app_class(width=width, height=height)
                else:
                    # Try with width and height if available
                    try:
                        self.pygame_app = pygame_app_class(width, height)
                    except:
                        # Fall back to no parameters
                        self.pygame_app = pygame_app_class()
            
            self.surface = pygame.Surface((width, height))
            
            # Store last frame for freezing during pause
            self.last_frame = None

        def get_remaining_time(self):
            if hasattr(self.pygame_app, 'get_remaining_time'):
                return self.pygame_app.get_remaining_time()
            # Check if the attribute might be at a deeper level
            elif (hasattr(self.pygame_app, 'order_window') and 
                  hasattr(self.pygame_app.order_window, 'get_remaining_time')):
                return self.pygame_app.order_window.get_remaining_time()
            return 0
        
        def reset_timer(self):
            if hasattr(self.pygame_app, 'reset_timer'):
                self.pygame_app.reset_timer()
            # Check if the attribute might be at a deeper level
            elif (hasattr(self.pygame_app, 'order_window') and 
                  hasattr(self.pygame_app.order_window, 'reset_timer')):
                self.pygame_app.order_window.reset_timer()
            return
            
        def process_pygame_events(self):
            if hasattr(self.pygame_app, 'process_events'):
                self.pygame_app.process_events()
        
        def update_game_logic(self):
            if self.is_paused:
                return  # Skip game logic updates when paused
                
            if hasattr(self.pygame_app, 'update'):
                result = None
                if callable(getattr(self.pygame_app, 'update')):
                    params = self.pygame_app.update.__code__.co_argcount
                    if params > 1:
                        result = self.pygame_app.update(3)  # Default value
                    else:
                        result = self.pygame_app.update()
                    
                    # Handle returned surface if any
                    if isinstance(result, tuple) and len(result) > 0:
                        if isinstance(result[0], pygame.Surface):
                            self.surface = result[0]
                            self.last_frame = result[0].copy()  # Store last frame for pause
        
        def render_game(self):
            # If paused and we have a last frame, use that
            if self.is_paused and self.last_frame is not None:
                self.surface = self.last_frame
                return
            
            if hasattr(self.pygame_app, 'render') and callable(getattr(self.pygame_app, 'render')):
                self.pygame_app.render(self.surface)
                self.last_frame = self.surface.copy()  # Store last frame
            elif hasattr(self.pygame_app, 'get_surface') and callable(getattr(self.pygame_app, 'get_surface')):
                new_surface = self.pygame_app.get_surface()
                if new_surface:
                    self.surface = new_surface
                    self.last_frame = new_surface.copy()  # Store last frame
    
    return WrappedPygameWidget