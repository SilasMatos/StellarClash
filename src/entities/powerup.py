"""
Classe para power-ups
"""
import pygame
import random
import math
from .entity import Entity
from ..utils.vector2 import Vector2
from ..core.constants import *
from ..effects.particles import Particle


class PowerUp(Entity):
    """Classe para power-ups melhorada"""
    
    def __init__(self, x, y, type_name):
        super().__init__(x, y, radius=15)
        self.type = type_name
        self.velocity = Vector2(0, 50)  # Cai lentamente
        self.lifetime = POWERUP_LIFETIME
        self.blink_timer = 0
        self.rotation = 0
        self.pulse_timer = 0
        self.sparkle_particles = []
        
        # Cores por tipo
        self.colors = {
            "triple_shot": CYAN,
            "shield": BLUE,
            "neutron_bomb": PURPLE
        }
        self.color = self.colors.get(type_name, WHITE)
    
    def update(self, dt):
        self.pos = self.pos + self.velocity * dt
        self.lifetime -= dt
        self.blink_timer += dt
        self.rotation += 90 * dt  # Rotate 90 degrees per second
        self.pulse_timer += dt
        
        # Create sparkle particles
        if random.random() < 0.1:  # 10% chance per frame
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(self.radius, self.radius * 1.5)
            particle_x = self.pos.x + math.cos(angle) * distance
            particle_y = self.pos.y + math.sin(angle) * distance
            particle_vel = Vector2(random.uniform(-20, 20), random.uniform(-20, 20))
            sparkle = Particle(particle_x, particle_y, particle_vel, self.color, 0.8, "star")
            self.sparkle_particles.append(sparkle)
        
        # Update sparkle particles
        self.sparkle_particles = [p for p in self.sparkle_particles if p.lifetime > 0]
        for particle in self.sparkle_particles:
            particle.update(dt)
        
        # Check if should be removed
        if self.is_off_screen() or self.lifetime <= 0:
            self.alive = False
    
    def draw(self, screen):
        # Draw sparkle particles first
        for particle in self.sparkle_particles:
            particle.draw(screen)
            
        # Efeito de piscar quando está acabando o tempo
        if self.lifetime < 3.0:
            if int(self.blink_timer * 10) % 2 == 0:
                return
        
        # Pulsing glow effect
        pulse_scale = 0.8 + 0.2 * math.sin(self.pulse_timer * 8)
        glow_radius = int(self.radius * 2 * pulse_scale)
        
        # Outer glow
        for i in range(4):
            glow_size = glow_radius - i * 3
            alpha = 40 - i * 10
            if glow_size > 0:
                glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*self.color, alpha), (glow_size, glow_size), glow_size)
                screen.blit(glow_surf, (self.pos.x - glow_size, self.pos.y - glow_size))
        
        # Main power-up circle
        main_radius = int(self.radius * pulse_scale)
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), main_radius)
        pygame.draw.circle(screen, WHITE, (int(self.pos.x), int(self.pos.y)), main_radius, 2)
        
        # Rotating outer ring
        ring_points = []
        for i in range(8):
            angle = math.radians(self.rotation + i * 45)
            ring_x = self.pos.x + math.cos(angle) * (self.radius + 5)
            ring_y = self.pos.y + math.sin(angle) * (self.radius + 5)
            ring_points.append((ring_x, ring_y))
        
        for i, point in enumerate(ring_points):
            if i % 2 == 0:  # Draw only every other point for a dotted effect
                pygame.draw.circle(screen, WHITE, (int(point[0]), int(point[1])), 2)
        
        # Desenha símbolo do power-up
        if self.type == "triple_shot":
            # Três linhas para tiro triplo com rotação
            for i in range(-1, 2):
                start_y = self.pos.y - 8
                end_y = self.pos.y + 8
                x = self.pos.x + i * 4
                pygame.draw.line(screen, WHITE, (x, start_y), (x, end_y), 2)
                # Add arrow heads
                if i == 0:  # Central arrow
                    pygame.draw.polygon(screen, WHITE, [
                        (x, start_y),
                        (x - 3, start_y + 5),
                        (x + 3, start_y + 5)
                    ])
        elif self.type == "shield":
            # Shield with rotating energy
            pygame.draw.circle(screen, WHITE, (int(self.pos.x), int(self.pos.y)), 8, 2)
            # Energy field lines
            for i in range(4):
                angle = math.radians(self.rotation + i * 90)
                inner_x = self.pos.x + math.cos(angle) * 6
                inner_y = self.pos.y + math.sin(angle) * 6
                outer_x = self.pos.x + math.cos(angle) * 10
                outer_y = self.pos.y + math.sin(angle) * 10
                pygame.draw.line(screen, BLUE, (inner_x, inner_y), (outer_x, outer_y), 2)
        elif self.type == "neutron_bomb":
            # Pulsing bomb with energy core
            core_size = int(6 * pulse_scale)
            pygame.draw.circle(screen, WHITE, (int(self.pos.x), int(self.pos.y)), core_size)
            # Energy sparks
            for i in range(6):
                angle = math.radians(self.rotation * 2 + i * 60)
                spark_x = self.pos.x + math.cos(angle) * 8
                spark_y = self.pos.y + math.sin(angle) * 8
                pygame.draw.circle(screen, PURPLE, (int(spark_x), int(spark_y)), 2)
