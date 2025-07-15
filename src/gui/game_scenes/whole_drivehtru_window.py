import pygame
import sys

from .drivethru import DriveThruGame

class WholeDriveThruWindow:
    def __init__(self, width=1280, height=960):
        pygame.init()
        self.width = max(width, 1280)
        self.height = max(height,960)
        self.win = pygame.Surface((self.width, self.height))
        self.running = True
        self.clock = pygame.time.Clock()        
        
        # Initialize DriveThruGame
        self.order_window = DriveThruGame()
        self.seconds_to_order = 20

        # Load the background image
        try:
            self.background_image = pygame.image.load("/Users/lorinczdora/Documents/Development/GestureAI/img/drivetrhu.jpg")
            self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
            self.foreground_image = pygame.image.load("/Users/lorinczdora/Documents/Development/GestureAI/img/drivethru_ablak.png")
            self.foreground_image = pygame.transform.scale(self.foreground_image, (self.order_window.width, self.order_window.height))
        except:
            # Create a fallback background if image can't be loaded
            self.background_image = pygame.Surface((self.width, self.height))
            self.background_image.fill((100, 150, 200))  # Blue-ish background
        

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        
    def update(self):
        # Fill the main window with the background
        self.win.blit(self.background_image, (0, 0))

        # Update the game and get the updated surface
        game_result = self.order_window.update(self.seconds_to_order)
        if isinstance(game_result, tuple) and len(game_result) > 1:
            self.seconds_to_order = game_result[1]
            
            # Draw the game surface onto the main window
            self.win.blit(game_result[0], (292, 395))
            # Draw the foreground image on top of the order window
            self.foreground_image = pygame.transform.scale(self.foreground_image, (self.order_window.width - 114, self.order_window.height + self.order_window.height/2 + 90))
            self.win.blit(self.foreground_image, (-30, -190))
    

            self.remaining_time = self.order_window.get_remaining_time()
        
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