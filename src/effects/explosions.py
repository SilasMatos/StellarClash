"""
Sistema de explosões e efeitos visuais avançados
"""
import pygame
from ..utils.vector2 import Vector2
from .particles import ParticleSystem


class ExplosionEffect:
    """Classe para efeitos de explosão melhorada"""
    
    def __init__(self, x, y, size=1, explosion_type="normal"):
        self.pos = Vector2(x, y)
        self.particle_system = ParticleSystem()
        self.lifetime = 1.5
        self.max_lifetime = 1.5
        self.explosion_type = explosion_type
        self.shockwave_radius = 0
        self.shockwave_max_radius = 50 * size
        
        # Criar explosão usando o sistema de partículas
        self.particle_system.create_explosion(x, y, size, explosion_type)
    
    def update(self, dt):
        self.lifetime -= dt
        
        # Update shockwave
        self.shockwave_radius += 200 * dt
        
        # Update particle system
        self.particle_system.update(dt)
        
        return self.lifetime <= 0 and len(self.particle_system.particles) == 0
    
    def draw(self, screen):
        from ..core.constants import WHITE
        
        # Draw shockwave ring
        if self.shockwave_radius < self.shockwave_max_radius:
            alpha = max(0, 1 - (self.shockwave_radius / self.shockwave_max_radius))
            if self.shockwave_radius > 5:
                pygame.draw.circle(screen, WHITE, 
                                 (int(self.pos.x), int(self.pos.y)), 
                                 int(self.shockwave_radius), 2)
        
        # Draw particles
        self.particle_system.draw(screen)
