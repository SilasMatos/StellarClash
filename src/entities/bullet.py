"""
Classe para projéteis
"""
import pygame
import math
from .entity import Entity
from ..utils.vector2 import Vector2
from ..core.constants import *
from ..effects.particles import Particle


class Bullet(Entity):
    """Classe para os projéteis melhorada"""
    
    def __init__(self, x, y, direction, speed=500, owner="player"):
        super().__init__(x, y, radius=4 if owner == "player" else 3)
        self.velocity = Vector2(math.cos(direction), math.sin(direction)) * speed
        self.owner = owner
        self.color = YELLOW if owner == "player" else RED
        self.lifetime = 3.0  # 3 segundos
        self.trail_particles = []
        self.glow_radius = self.radius * 3
        
        # Animação do projétil
        self.pulse_timer = 0
        self.trail_timer = 0
    
    def update(self, dt):
        self.pos = self.pos + self.velocity * dt
        self.lifetime -= dt
        self.pulse_timer += dt
        self.trail_timer += dt
        
        # Create trail particles
        if self.trail_timer >= 0.02:  # Every 20ms
            trail_color = (*self.color, 150)
            trail_vel = Vector2(-self.velocity.x * 0.1, -self.velocity.y * 0.1)
            particle = Particle(self.pos.x, self.pos.y, trail_vel, trail_color, 0.3)
            self.trail_particles.append(particle)
            self.trail_timer = 0
        
        # Update trail particles
        self.trail_particles = [p for p in self.trail_particles if p.lifetime > 0]
        for particle in self.trail_particles:
            particle.update(dt)
        
        # Check if should be removed
        if self.is_off_screen() or self.lifetime <= 0:
            self.alive = False
    
    def draw(self, screen):
        # Draw trail first
        for particle in self.trail_particles:
            particle.draw(screen)
        
        # Pulsing glow effect
        pulse = 0.8 + 0.2 * math.sin(self.pulse_timer * 15)
        glow_size = int(self.glow_radius * pulse)
        
        # Outer glow
        for i in range(3):
            size = glow_size - i * 2
            if size > 0:
                alpha = 30 - i * 10
                glow_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*self.color, alpha), (size, size), size)
                screen.blit(glow_surf, (self.pos.x - size, self.pos.y - size))
        
        # Main bullet
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        # Inner bright core
        core_color = tuple(min(255, c + 100) for c in self.color)
        pygame.draw.circle(screen, core_color, (int(self.pos.x), int(self.pos.y)), max(1, self.radius - 1))
