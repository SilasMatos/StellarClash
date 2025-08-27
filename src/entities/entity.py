"""
Classe base para todas as entidades do jogo
"""
from abc import ABC, abstractmethod
import pygame
from ..utils.vector2 import Vector2


class Entity(ABC):
    """Classe base para todas as entidades do jogo"""
    
    def __init__(self, x, y, radius=10):
        self.pos = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.radius = radius
        self.health = 1
        self.max_health = 1
        self.alive = True
    
    @abstractmethod
    def update(self, dt, *args):
        """Atualiza a entidade"""
        pass
    
    @abstractmethod
    def draw(self, screen):
        """Desenha a entidade"""
        pass
    
    def get_rect(self):
        """Retorna o retângulo de colisão"""
        return pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius,
                          self.radius * 2, self.radius * 2)
    
    def check_collision(self, other):
        """Verifica colisão com outra entidade"""
        distance = (self.pos - other.pos).length()
        return distance < (self.radius + other.radius)
    
    def take_damage(self, damage=1):
        """Recebe dano"""
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            return True
        return False
    
    def is_off_screen(self, margin=50):
        """Verifica se a entidade saiu da tela"""
        from ..core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
        return (self.pos.x < -margin or self.pos.x > SCREEN_WIDTH + margin or
                self.pos.y < -margin or self.pos.y > SCREEN_HEIGHT + margin)
