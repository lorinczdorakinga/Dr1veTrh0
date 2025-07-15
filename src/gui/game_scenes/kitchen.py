import pygame
import sys

class Kitchen:
    def __init__(self, width=1280, height=960):
        self.win = pygame.Surface((width, height))
        self.width = max(width, 1280)
        self.height = max(height,960)

        try:
            self.background_image = pygame.image.load("/Users/lorinczdora/Documents/Development/GestureAI/img/kitchen.jpg")
            self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
        except:
            # Create a fallback background if image can't be loaded
            self.background_image = pygame.Surface((self.width, self.height))
            self.background_image.fill((100, 150, 200))  # Blue-ish background
        
    def process_events(self):
        for event in pygame.event.get():
            pass  # Handle kitchen-specific events here
            
    def update(self):
         # Fill the main window with the background
        self.win.blit(self.background_image, (0, 0))        
        return self.win
        
    def get_surface(self):
        return self.win
        
    def render(self, surface):
        surface.blit(self.win, (0, 0))

    def get_remaining_time(self):
        if hasattr(self, 'remaining_time'):
            return self.remaining_time
        return 0
    def reset_timer(self):
        self.remaining_time = 0
        self.order_window.reset_timer()

    def set_order_time(self, time):
        if hasattr(self, 'remaining_time'):
            self.seconds_to_order = time