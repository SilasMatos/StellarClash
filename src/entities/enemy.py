"""
Classe para naves inimigas
"""
import pygame
import random
import math
from .entity import Entity
from .bullet import Bullet
from ..utils.vector2 import Vector2
from ..core.constants import *


class Enemy(Entity):
    """Classe para naves inimigas"""
    
    def __init__(self, x, y, enemy_type="basic"):
        super().__init__(x, y, radius=10)
        self.type = enemy_type
        self.health = 2 if enemy_type == "advanced" else 1
        self.max_health = self.health
        self.last_shot = 0
        self.shot_cooldown = 2.0 if enemy_type == "basic" else 1.5
        
        # Padrões de movimento
        if enemy_type == "basic":
            self.velocity = Vector2(0, 100)
        else:  # advanced
            self.velocity = Vector2(random.choice([-50, 50]), 80)
            self.side_speed = 100
            self.move_timer = 0
    
    def update(self, dt, player_pos):
        self.last_shot += dt
        
        if self.type == "basic":
            # Movimento simples para baixo
            self.pos = self.pos + self.velocity * dt
        else:  # advanced
            # Movimento em zigzag
            self.move_timer += dt
            self.pos.y += self.velocity.y * dt
            self.pos.x += math.sin(self.move_timer * 3) * self.side_speed * dt
        
        # Manter dentro da tela horizontalmente
        if self.pos.x < self.radius:
            self.pos.x = self.radius
            if hasattr(self, 'velocity'):
                self.velocity.x = abs(self.velocity.x)
        elif self.pos.x > SCREEN_WIDTH - self.radius:
            self.pos.x = SCREEN_WIDTH - self.radius
            if hasattr(self, 'velocity'):
                self.velocity.x = -abs(self.velocity.x)
        
        # Check if off screen
        if self.is_off_screen():
            self.alive = False
    
    def can_shoot(self, player_pos):
        """Verifica se pode atirar no jogador"""
        if self.last_shot < self.shot_cooldown:
            return False
        
        # Só atira se o jogador estiver na frente e próximo
        distance = (player_pos - self.pos).length()
        return distance < 300 and player_pos.y > self.pos.y
    
    def shoot(self, player_pos):
        """Atira no jogador"""
        if self.can_shoot(player_pos):
            # Calcular direção para o jogador
            direction = (player_pos - self.pos).normalize()
            angle = math.atan2(direction.y, direction.x)
            
            self.last_shot = 0
            return [Bullet(self.pos.x, self.pos.y, angle, 300, "enemy")]
        return []
    
    def draw(self, screen):
        # Cor baseada na vida com efeito pulsante
        time_factor = pygame.time.get_ticks() * 0.005
        pulse = 0.8 + 0.2 * math.sin(time_factor)
        
        if self.health < self.max_health:
            color = tuple(int(c * pulse) for c in RED)
        else:
            color = PURPLE if self.type == "advanced" else RED
        
        # Shadow effect
        shadow_points = [
            (self.pos.x + 2, self.pos.y + self.radius + 2),
            (self.pos.x - self.radius + 2, self.pos.y - self.radius + 2),
            (self.pos.x + self.radius + 2, self.pos.y - self.radius + 2)
        ]
        pygame.draw.polygon(screen, (30, 30, 30), shadow_points)
        
        # Nave inimiga (triângulo apontando para baixo)
        points = [
            (self.pos.x, self.pos.y + self.radius),
            (self.pos.x - self.radius, self.pos.y - self.radius),
            (self.pos.x + self.radius, self.pos.y - self.radius)
        ]
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, WHITE, points, 2)
        
        # Enemy ship details
        if self.type == "advanced":
            # Advanced enemy has extra details
            # Side weapons
            weapon_y = self.pos.y - self.radius * 0.3
            pygame.draw.circle(screen, ORANGE, 
                             (int(self.pos.x - self.radius * 0.6), int(weapon_y)), 2)
            pygame.draw.circle(screen, ORANGE, 
                             (int(self.pos.x + self.radius * 0.6), int(weapon_y)), 2)
            
            # Engine glow
            engine_y = self.pos.y - self.radius * 0.8
            pygame.draw.circle(screen, PURPLE, (int(self.pos.x), int(engine_y)), 3)
        else:
            # Basic enemy engine
            engine_y = self.pos.y - self.radius * 0.5
            pygame.draw.circle(screen, RED, (int(self.pos.x), int(engine_y)), 2)
