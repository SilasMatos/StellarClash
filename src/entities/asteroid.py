"""
Classe para asteroides
"""
import pygame
import random
import math
from .entity import Entity
from ..utils.vector2 import Vector2
from ..core.constants import *


class Asteroid(Entity):
    """Classe para asteroides"""
    
    def __init__(self, x, y, size=3):
        radius = size * 8 + 10
        super().__init__(x, y, radius)
        self.size = size  # 1=pequeno, 2=médio, 3=grande
        self.velocity = Vector2(
            random.uniform(-100, 100),
            random.uniform(50, 150)
        )
        self.rotation = 0
        self.rotation_speed = random.uniform(-180, 180)
        self.health = size
        self.max_health = size
        
        # Gerar pontos do asteroide (forma irregular)
        self.points = self._generate_asteroid_shape()
    
    def _generate_asteroid_shape(self):
        """Gera uma forma irregular para o asteroide"""
        points = []
        num_points = 8
        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi
            # Varia o raio para criar forma irregular
            radius_variation = random.uniform(0.7, 1.3)
            radius = self.radius * radius_variation
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            points.append((x, y))
        return points
    
    def update(self, dt):
        self.pos = self.pos + self.velocity * dt
        self.rotation += self.rotation_speed * dt
        
        # Wrap around screen horizontally
        if self.pos.x < -self.radius:
            self.pos.x = SCREEN_WIDTH + self.radius
        elif self.pos.x > SCREEN_WIDTH + self.radius:
            self.pos.x = -self.radius
        
        # Check if off screen vertically
        if self.is_off_screen():
            self.alive = False
    
    def take_damage(self, damage=1):
        """Recebe dano e retorna lista de asteroides filhos se quebrar"""
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            if self.size > 1:
                # Quebra em asteroides menores
                children = []
                for _ in range(2):
                    child = Asteroid(self.pos.x, self.pos.y, self.size - 1)
                    # Velocidade aleatória para os filhos
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(100, 200)
                    child.velocity = Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
                    children.append(child)
                return children
            return []
        return None
    
    def draw(self, screen):
        # Rotacionar pontos
        cos_rot = math.cos(math.radians(self.rotation))
        sin_rot = math.sin(math.radians(self.rotation))
        
        rotated_points = []
        for x, y in self.points:
            rotated_x = x * cos_rot - y * sin_rot
            rotated_y = x * sin_rot + y * cos_rot
            rotated_points.append((
                self.pos.x + rotated_x,
                self.pos.y + rotated_y
            ))
        
        color = GRAY if self.health == self.max_health else RED
        pygame.draw.polygon(screen, color, rotated_points)
        pygame.draw.polygon(screen, WHITE, rotated_points, 2)
