"""
Classe do jogador
"""
import pygame
import math
from .entity import Entity
from .bullet import Bullet
from ..utils.vector2 import Vector2
from ..core.constants import *
from ..effects.particles import ParticleSystem


class Player(Entity):
    """Classe do jogador"""
    
    def __init__(self, x, y):
        super().__init__(x, y, radius=12)
        self.speed = PLAYER_SPEED
        self.health = 3
        self.max_health = 3
        self.last_shot = 0
        self.shot_cooldown = PLAYER_SHOT_COOLDOWN
        
        # Power-ups
        self.triple_shot_timer = 0
        self.shield_active = False
        self.shield_hits = 0
        self.shield_max_hits = 1
        
        # Invulnerabilidade temporária após ser atingido
        self.invulnerable_timer = 0
        self.invulnerable_duration = PLAYER_INVULNERABLE_DURATION
        
        # Sistema de partículas para o motor
        self.particle_system = ParticleSystem()
    
    def update(self, dt, keys_pressed):
        # Movimento
        self.velocity = Vector2(0, 0)
        
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            self.velocity.x = -self.speed
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            self.velocity.x = self.speed
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            self.velocity.y = -self.speed
        if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            self.velocity.y = self.speed
        
        # Normalizar velocidade diagonal
        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize() * self.speed
        
        self.pos = self.pos + self.velocity * dt
        
        # Manter dentro da tela
        self.pos.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.pos.y))
        
        # Atualizar timers
        self.last_shot += dt
        if self.triple_shot_timer > 0:
            self.triple_shot_timer -= dt
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        
        # Partículas do motor
        if self.velocity.length() > 0:
            self.particle_system.create_engine_particles(self.pos.x, self.pos.y)
        
        # Atualizar sistema de partículas
        self.particle_system.update(dt)
    
    def shoot(self):
        """Atira projéteis"""
        if self.last_shot >= self.shot_cooldown:
            bullets = []
            
            if self.triple_shot_timer > 0:
                # Tiro triplo
                angles = [-0.3, 0, 0.3]  # Ângulos em radianos
                for angle in angles:
                    bullets.append(Bullet(self.pos.x, self.pos.y - 15, -math.pi/2 + angle))
            else:
                # Tiro simples
                bullets.append(Bullet(self.pos.x, self.pos.y - 15, -math.pi/2))
            
            self.last_shot = 0
            return bullets
        return []
    
    def take_damage(self, damage=1):
        """Recebe dano"""
        if self.invulnerable_timer > 0:
            return False
        
        if self.shield_active:
            self.shield_hits += 1
            if self.shield_hits >= self.shield_max_hits:
                self.shield_active = False
                self.shield_hits = 0
            return False
        
        self.health -= damage
        self.invulnerable_timer = self.invulnerable_duration
        if self.health <= 0:
            self.alive = False
        return True
    
    def collect_powerup(self, powerup_type):
        """Coleta um power-up"""
        if powerup_type == "triple_shot":
            self.triple_shot_timer = 10.0
        elif powerup_type == "shield":
            self.shield_active = True
            self.shield_hits = 0
        elif powerup_type == "neutron_bomb":
            return True  # Retorna True para indicar que deve explodir tudo
        return False
    
    def draw(self, screen):
        # Desenhar partículas do motor primeiro
        self.particle_system.draw(screen)
        
        # Efeito de piscar quando invulnerável
        if self.invulnerable_timer > 0:
            if int(self.invulnerable_timer * 10) % 2 == 0:
                return
        
        # Escudo com efeito pulsante
        if self.shield_active:
            pulse = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.01)
            shield_radius = int((self.radius + 8) * pulse)
            
            # Multiple shield layers for better effect
            for i in range(3):
                layer_radius = shield_radius - i * 2
                layer_alpha = int((100 - i * 30) * pulse)
                if layer_radius > 0:
                    shield_surf = pygame.Surface((layer_radius * 2, layer_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(shield_surf, (*BLUE[:3], layer_alpha), 
                                     (layer_radius, layer_radius), layer_radius, 2)
                    screen.blit(shield_surf, (self.pos.x - layer_radius, self.pos.y - layer_radius))
        
        # Nave (triângulo apontando para cima) com mais detalhes
        points = [
            (self.pos.x, self.pos.y - self.radius),
            (self.pos.x - self.radius, self.pos.y + self.radius),
            (self.pos.x + self.radius, self.pos.y + self.radius)
        ]
        
        # Shadow/depth effect
        shadow_points = [(x + 2, y + 2) for x, y in points]
        pygame.draw.polygon(screen, (50, 50, 50), shadow_points)
        
        # Main ship body
        pygame.draw.polygon(screen, WHITE, points)
        pygame.draw.polygon(screen, CYAN, points, 2)
        
        # Ship details
        # Cockpit
        cockpit_y = self.pos.y - self.radius * 0.3
        pygame.draw.circle(screen, CYAN, (int(self.pos.x), int(cockpit_y)), 3)
        
        # Wing details
        wing_y = self.pos.y + self.radius * 0.5
        pygame.draw.line(screen, YELLOW, 
                        (self.pos.x - self.radius * 0.7, wing_y), 
                        (self.pos.x - self.radius * 0.3, wing_y), 2)
        pygame.draw.line(screen, YELLOW, 
                        (self.pos.x + self.radius * 0.3, wing_y), 
                        (self.pos.x + self.radius * 0.7, wing_y), 2)
