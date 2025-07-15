import pygame
class DriveThruGame:
    def __init__(self):
        self.win = pygame.Surface((605, 400), pygame.SRCALPHA)
        self.width = 1600
        self.height = 800
        self.x = float(self.win.get_width()) # Use float for smoother movement
        self.y = 50
        self.speed = 10
        self.middle_reached = False
        self.order_start_time = 0
        self.remaining_time = 0 # Initialize remaining time
        self.paused = False # Add paused state
        self.seconds_to_order = 20
        
        # Load the car image
        car_image_path = "/Users/lorinczdora/Documents/Development/GestureAI/img/car2.png"
        self.car_image = pygame.image.load(car_image_path)
        self.car_image = pygame.transform.scale(self.car_image, (self.width, self.height))
    
    def set_paused(self, paused):
        """Set the paused state"""
        self.paused = paused
    
    def update(self, seconds_to_order):
        self.seconds_to_order = seconds_to_order
        
        if self.paused:
            # When paused, just return the current state without updating
            return self.win, self.seconds_to_order, self.middle_reached
            
        middle_x = self.win.get_width() / 2 - self.width / 2
        self.win.fill((0, 0, 0, 0)) # Clear with transparent background
        
        if not self.middle_reached and middle_x - self.speed < self.x <= middle_x:
            self.middle_reached = True
            self.order_start_time = pygame.time.get_ticks()
        
        if self.middle_reached:
            self.process_events(self.seconds_to_order)
            
        if not self.middle_reached and self.x > -self.width:
            self.x -= self.speed
        elif not self.middle_reached and self.x <= 0:
            self.x = float(self.win.get_width())
            
        # Draw the car image
        self.win.blit(self.car_image, (int(self.x), self.y))
        
        return self.win, self.seconds_to_order, self.middle_reached
    
    def process_events(self, seconds_to_order):
        if self.paused:
            return
            
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.order_start_time
        remaining_time = seconds_to_order * 1000 - elapsed_time
        
        self.remaining_time = max(0, remaining_time)
        
        if remaining_time <= 0:
            self.middle_reached = False
            self.x -= self.speed
    
    def get_surface(self):
        return self.win
        
    def get_remaining_time(self):
        """Get the current remaining time in milliseconds"""
        if hasattr(self, 'remaining_time'):
            return self.remaining_time
        return 0
    
    def reset_timer(self):
        """Completely reset the timer and state"""
        self.remaining_time = 0
        self.middle_reached = False
        self.order_start_time = pygame.time.get_ticks()
        
    def set_order_time(self, time):
        """Set the order time in seconds"""
        if hasattr(self, 'remaining_time'):
            self.seconds_to_order = time
