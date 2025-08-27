"""
Sistema de partículas para efeitos visuais
"""
import random
import math
import pygame
from ..utils.vector2 import Vector2


class Particle:
    """Classe para partículas individuais"""
    
    def __init__(self, x, y, velocity, color, lifetime, particle_type="normal"):
        self.pos = Vector2(x, y)
        self.velocity = velocity
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(2, 6)
        self.type = particle_type
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-180, 180)
        self.scale = 1.0
        self.gravity = Vector2(0, 0)
        
        # Diferentes tipos de partículas
        if particle_type == "spark":
            self.size = random.randint(1, 3)
            self.gravity = Vector2(0, 200)
        elif particle_type == "smoke":
            self.size = random.randint(4, 8)
            self.gravity = Vector2(0, -50)
        elif particle_type == "star":
            self.size = random.randint(2, 4)
            self.rotation_speed = random.uniform(90, 270)
    
    def update(self, dt):
        self.pos = self.pos + self.velocity * dt
        self.velocity = self.velocity + self.gravity * dt
        self.lifetime -= dt
        self.rotation += self.rotation_speed * dt
        
        # Fade out effect com diferentes curvas
        progress = 1 - (self.lifetime / self.max_lifetime)
        if self.type == "smoke":
            alpha = max(0, (self.lifetime / self.max_lifetime) * 0.6)
            self.scale = 1 + progress * 2  # Smoke expands
        else:
            alpha = max(0, self.lifetime / self.max_lifetime)
            self.scale = 1 - progress * 0.3  # Slight shrinking
            
        # Update color with alpha
        if len(self.color) == 3:
            self.color = (*self.color, int(255 * alpha))
        else:
            self.color = (*self.color[:3], int(255 * alpha))
    
    def draw(self, screen):
        if self.lifetime > 0:
            size = max(1, int(self.size * self.scale))
            
            if self.type == "star":
                # Draw a rotating star
                points = []
                for i in range(8):
                    angle = math.radians(self.rotation + i * 45)
                    if i % 2 == 0:
                        radius = size * 2
                    else:
                        radius = size
                    x = self.pos.x + math.cos(angle) * radius
                    y = self.pos.y + math.sin(angle) * radius
                    points.append((x, y))
                
                if len(points) > 2:
                    pygame.draw.polygon(screen, self.color[:3], points)
            else:
                pygame.draw.circle(screen, self.color[:3], (int(self.pos.x), int(self.pos.y)), size)


class ParticleSystem:
    """Sistema de gerenciamento de partículas"""
    
    def __init__(self):
        self.particles = []
    
    def add_particle(self, particle):
        """Adiciona uma partícula ao sistema"""
        self.particles.append(particle)
    
    def create_explosion(self, x, y, size=1, explosion_type="normal"):
        """Cria uma explosão de partículas"""
        from ..core.constants import RED, ORANGE, YELLOW, WHITE, GRAY, CYAN
        
        # Partículas principais da explosão
        num_particles = int(30 * size)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80, 300) * size
            velocity = Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            
            # Diferentes tipos de partículas na explosão
            if random.random() < 0.4:
                color = random.choice([RED, ORANGE])
                particle_type = "normal"
                lifetime = random.uniform(0.8, 1.5)
            elif random.random() < 0.7:
                color = YELLOW
                particle_type = "spark"
                lifetime = random.uniform(0.5, 1.0)
            else:
                color = WHITE
                particle_type = "star"
                lifetime = random.uniform(1.0, 1.8)
                
            particle = Particle(x, y, velocity, color, lifetime, particle_type)
            self.add_particle(particle)
        
        # Partículas de fumaça para explosões maiores
        if size > 1:
            for _ in range(int(10 * size)):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(30, 100) * size
                velocity = Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
                smoke_particle = Particle(x, y, velocity, GRAY, 
                                        random.uniform(1.0, 2.0), "smoke")
                self.add_particle(smoke_particle)
        
        # Onda de choque para explosões grandes
        if explosion_type == "big" or size > 2:
            for _ in range(20):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(200, 400)
                velocity = Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
                shockwave_particle = Particle(x, y, velocity, CYAN, 0.3)
                self.add_particle(shockwave_particle)
    
    def create_engine_particles(self, x, y, velocity_offset=None):
        """Cria partículas do motor da nave"""
        from ..core.constants import ORANGE, CYAN
        
        for _ in range(3):
            particle_x = x + random.uniform(-8, 8)
            particle_y = y + 15
            particle_vel = Vector2(
                random.uniform(-80, 80), 
                random.uniform(80, 150)
            )
            
            if velocity_offset:
                particle_vel = particle_vel + velocity_offset
            
            # Diferentes tipos de partículas do motor
            if random.random() < 0.7:
                particle = Particle(particle_x, particle_y, particle_vel, ORANGE, 0.6)
            else:
                particle = Particle(particle_x, particle_y, particle_vel, CYAN, 0.4, "spark")
            self.add_particle(particle)
    
    def update(self, dt):
        """Atualiza todas as partículas"""
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update(dt)
    
    def draw(self, screen):
        """Desenha todas as partículas"""
        for particle in self.particles:
            particle.draw(screen)
    
    def clear(self):
        """Remove todas as partículas"""
        self.particles.clear()
