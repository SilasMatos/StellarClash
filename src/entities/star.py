"""
Classe para as estrelas do fundo
"""
import pygame
import random
import math
from ..core.constants import *


class Star:
    """Classe para as estrelas do fundo melhorada"""
    
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.5, 4.0)
        self.brightness = random.randint(100, 255)
        self.size = random.randint(1, 4)
        self.twinkle_speed = random.uniform(2, 6)
        self.twinkle_offset = random.uniform(0, math.pi * 2)
        self.star_type = random.choice(["normal", "bright", "distant"])
        
        if self.star_type == "bright":
            self.brightness = random.randint(180, 255)
            self.size = random.randint(2, 4)
        elif self.star_type == "distant":
            self.brightness = random.randint(60, 120)
            self.size = 1
    
    def update(self, dt):
        self.y += self.speed * dt * 30
        if self.y > SCREEN_HEIGHT:
            self.y = -10
            self.x = random.randint(0, SCREEN_WIDTH)
    
    def draw(self, screen):
        # Twinkle effect
        time_factor = pygame.time.get_ticks() * 0.001
        twinkle = 0.8 + 0.2 * math.sin(self.twinkle_speed * time_factor + self.twinkle_offset)
        current_brightness = int(self.brightness * twinkle)
        
        color = (current_brightness, current_brightness, current_brightness)
        
        if self.star_type == "bright" and self.size > 2:
            # Draw cross pattern for bright stars
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
            # Add sparkle effect
            sparkle_size = max(1, self.size - 1)
            pygame.draw.line(screen, color, 
                           (self.x - sparkle_size * 2, self.y), 
                           (self.x + sparkle_size * 2, self.y), 1)
            pygame.draw.line(screen, color, 
                           (self.x, self.y - sparkle_size * 2), 
                           (self.x, self.y + sparkle_size * 2), 1)
        else:
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
