"""
Classe do jogador
"""
import pygame
import math
from .entity import Entity
from .bullet import Bullet
from .ship_types import ShipType, ShipConfig
from ..utils.vector2 import Vector2
from ..core.constants import *
from ..effects.particles import ParticleSystem


class Player(Entity):
    """Classe do jogador"""
    
    def __init__(self, x, y, ship_type=ShipType.CLASSIC):
        super().__init__(x, y, radius=12)
        
        # Configurar nave baseado no tipo
        self.ship_type = ship_type
        self.ship_config = ShipConfig.SHIPS[ship_type]
        
        # Atributos baseados na configuração da nave
        self.speed = self.ship_config["speed"]
        self.health = self.ship_config["health"]
        self.max_health = self.ship_config["health"]
        self.shot_cooldown = self.ship_config["shot_cooldown"]
        self.last_shot = 0
        
        # Cores da nave
        self.color_primary = self.ship_config["color_primary"]
        self.color_secondary = self.ship_config["color_secondary"]
        self.color_accent = self.ship_config["color_accent"]
        self.engine_color = self.ship_config["engine_color"]
        
        # Power-ups
        self.triple_shot_timer = 0
        self.shield_active = False
        self.shield_hits = 0
        self.shield_max_hits = 1
        
        # Invulnerabilidade temporária após ser atingido
        self.invulnerable_timer = 0
        self.invulnerable_duration = PLAYER_INVULNERABLE_DURATION
        
        # Habilidades especiais por tipo de nave
        self.stealth_timer = 0
        self.heavy_double_shot = (ship_type == ShipType.HEAVY)
        self.phoenix_regen_timer = 0
        self.phoenix_regen_interval = 5.0  # Regenera a cada 5 segundos
        
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
        if self.stealth_timer > 0:
            self.stealth_timer -= dt
        
        # Habilidade especial da Phoenix - regeneração
        if self.ship_type == ShipType.PHOENIX and self.health < self.max_health:
            self.phoenix_regen_timer += dt
            if self.phoenix_regen_timer >= self.phoenix_regen_interval:
                self.health = min(self.max_health, self.health + 1)
                self.phoenix_regen_timer = 0
        
        # Partículas do motor com cor da nave
        if self.velocity.length() > 0:
            self.particle_system.create_engine_particles(self.pos.x, self.pos.y, color=self.engine_color)
        
        # Atualizar sistema de partículas
        self.particle_system.update(dt)
    
    def update_preview(self, dt):
        """Atualiza o player para preview (sem input de teclado)"""
        # Atualizar apenas timers e partículas
        self.last_shot += dt
        if self.triple_shot_timer > 0:
            self.triple_shot_timer -= dt
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        if self.stealth_timer > 0:
            self.stealth_timer -= dt
        
        # Habilidade especial da Phoenix - regeneração
        if self.ship_type == ShipType.PHOENIX and self.health < self.max_health:
            self.phoenix_regen_timer += dt
            if self.phoenix_regen_timer >= self.phoenix_regen_interval:
                self.health = min(self.max_health, self.health + 1)
                self.phoenix_regen_timer = 0
        
        # Partículas do motor com cor da nave (sempre ativas no preview)
        self.particle_system.create_engine_particles(self.pos.x, self.pos.y, color=self.engine_color)
        
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
            elif self.ship_type == ShipType.HEAVY:
                # Nave pesada atira duplo
                bullets.append(Bullet(self.pos.x - 8, self.pos.y - 15, -math.pi/2))
                bullets.append(Bullet(self.pos.x + 8, self.pos.y - 15, -math.pi/2))
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
        
        # Habilidade especial da Stealth - invisibilidade temporária
        if self.ship_type == ShipType.STEALTH:
            self.stealth_timer = 2.0  # 2 segundos de invisibilidade
        
        # Criar partículas de dano
        self.particle_system.create_damage_particles(self.pos.x, self.pos.y, color=self.color_primary)
        
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
        
        # Efeito de invisibilidade da nave Stealth
        if self.stealth_timer > 0:
            # Nave semi-transparente durante invisibilidade
            alpha = int(100 + 50 * math.sin(pygame.time.get_ticks() * 0.02))
        else:
            alpha = 255
        
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
                    pygame.draw.circle(shield_surf, (*self.color_accent[:3], layer_alpha), 
                                     (layer_radius, layer_radius), layer_radius, 2)
                    screen.blit(shield_surf, (self.pos.x - layer_radius, self.pos.y - layer_radius))
        
        # Desenhar nave baseada no tipo
        self._draw_ship_by_type(screen, alpha)
    
    def _draw_ship_by_type(self, screen, alpha=255):
        """Desenha a nave baseada no tipo selecionado"""
        ship_surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        
        if self.ship_type == ShipType.CLASSIC:
            self._draw_classic_ship(ship_surf, alpha)
        elif self.ship_type == ShipType.VIPER:
            self._draw_viper_ship(ship_surf, alpha)
        elif self.ship_type == ShipType.PHOENIX:
            self._draw_phoenix_ship(ship_surf, alpha)
        elif self.ship_type == ShipType.STEALTH:
            self._draw_stealth_ship(ship_surf, alpha)
        elif self.ship_type == ShipType.HEAVY:
            self._draw_heavy_ship(ship_surf, alpha)
        
        screen.blit(ship_surf, (self.pos.x - self.radius * 2, self.pos.y - self.radius * 2))
    
    def _draw_classic_ship(self, surface, alpha):
        """Desenha a nave clássica"""
        center = (self.radius * 2, self.radius * 2)
        
        # Corpo principal - triângulo
        points = [
            (center[0], center[1] - self.radius),
            (center[0] - self.radius, center[1] + self.radius),
            (center[0] + self.radius, center[1] + self.radius)
        ]
        
        # Shadow/depth effect
        shadow_points = [(x + 2, y + 2) for x, y in points]
        pygame.draw.polygon(surface, (*self.color_secondary, alpha//2), shadow_points)
        
        # Main ship body
        pygame.draw.polygon(surface, (*self.color_primary, alpha), points)
        pygame.draw.polygon(surface, (*self.color_accent, alpha), points, 2)
        
        # Cockpit
        cockpit_y = center[1] - self.radius * 0.3
        pygame.draw.circle(surface, (*self.color_accent, alpha), (center[0], int(cockpit_y)), 3)
        
        # Wing details
        wing_y = center[1] + self.radius * 0.5
        pygame.draw.line(surface, (*self.color_accent, alpha), 
                        (center[0] - self.radius * 0.7, wing_y), 
                        (center[0] - self.radius * 0.3, wing_y), 2)
        pygame.draw.line(surface, (*self.color_accent, alpha), 
                        (center[0] + self.radius * 0.3, wing_y), 
                        (center[0] + self.radius * 0.7, wing_y), 2)
    
    def _draw_viper_ship(self, surface, alpha):
        """Desenha a nave Víbora - formato mais aerodinâmico"""
        center = (self.radius * 2, self.radius * 2)
        
        # Corpo principal - formato de diamante alongado
        points = [
            (center[0], center[1] - self.radius * 1.2),
            (center[0] - self.radius * 0.6, center[1]),
            (center[0], center[1] + self.radius),
            (center[0] + self.radius * 0.6, center[1])
        ]
        
        pygame.draw.polygon(surface, (*self.color_primary, alpha), points)
        pygame.draw.polygon(surface, (*self.color_secondary, alpha), points, 2)
        
        # Asas laterais pequenas
        wing_points_left = [
            (center[0] - self.radius * 0.6, center[1] - self.radius * 0.2),
            (center[0] - self.radius * 1.2, center[1]),
            (center[0] - self.radius * 0.6, center[1] + self.radius * 0.2)
        ]
        wing_points_right = [
            (center[0] + self.radius * 0.6, center[1] - self.radius * 0.2),
            (center[0] + self.radius * 1.2, center[1]),
            (center[0] + self.radius * 0.6, center[1] + self.radius * 0.2)
        ]
        
        pygame.draw.polygon(surface, (*self.color_secondary, alpha), wing_points_left)
        pygame.draw.polygon(surface, (*self.color_secondary, alpha), wing_points_right)
        
        # Cockpit central
        pygame.draw.circle(surface, (*self.color_accent, alpha), center, 4)
    
    def _draw_phoenix_ship(self, surface, alpha):
        """Desenha a nave Fênix - formato de ave"""
        center = (self.radius * 2, self.radius * 2)
        
        # Corpo principal
        body_points = [
            (center[0], center[1] - self.radius),
            (center[0] - self.radius * 0.4, center[1] + self.radius),
            (center[0] + self.radius * 0.4, center[1] + self.radius)
        ]
        pygame.draw.polygon(surface, (*self.color_primary, alpha), body_points)
        
        # Asas como chamas
        wing_left = [
            (center[0] - self.radius * 0.4, center[1] - self.radius * 0.2),
            (center[0] - self.radius * 1.3, center[1] + self.radius * 0.3),
            (center[0] - self.radius * 0.8, center[1] + self.radius * 0.8),
            (center[0] - self.radius * 0.4, center[1] + self.radius * 0.5)
        ]
        wing_right = [
            (center[0] + self.radius * 0.4, center[1] - self.radius * 0.2),
            (center[0] + self.radius * 1.3, center[1] + self.radius * 0.3),
            (center[0] + self.radius * 0.8, center[1] + self.radius * 0.8),
            (center[0] + self.radius * 0.4, center[1] + self.radius * 0.5)
        ]
        
        pygame.draw.polygon(surface, (*self.color_secondary, alpha), wing_left)
        pygame.draw.polygon(surface, (*self.color_secondary, alpha), wing_right)
        pygame.draw.polygon(surface, (*self.color_accent, alpha), wing_left, 1)
        pygame.draw.polygon(surface, (*self.color_accent, alpha), wing_right, 1)
        
        # Detalhes do corpo
        pygame.draw.polygon(surface, (*self.color_accent, alpha), body_points, 2)
        pygame.draw.circle(surface, (*self.color_accent, alpha), center, 3)
    
    def _draw_stealth_ship(self, surface, alpha):
        """Desenha a nave Sombra - formato angular"""
        center = (self.radius * 2, self.radius * 2)
        
        # Corpo principal - formato stealth angular
        points = [
            (center[0], center[1] - self.radius),
            (center[0] - self.radius * 0.8, center[1] - self.radius * 0.2),
            (center[0] - self.radius * 0.5, center[1] + self.radius),
            (center[0] + self.radius * 0.5, center[1] + self.radius),
            (center[0] + self.radius * 0.8, center[1] - self.radius * 0.2)
        ]
        
        pygame.draw.polygon(surface, (*self.color_primary, alpha), points)
        pygame.draw.polygon(surface, (*self.color_secondary, alpha), points, 1)
        
        # Detalhes angulares
        detail_points = [
            (center[0] - self.radius * 0.3, center[1] - self.radius * 0.5),
            (center[0], center[1] - self.radius * 0.3),
            (center[0] + self.radius * 0.3, center[1] - self.radius * 0.5)
        ]
        pygame.draw.polygon(surface, (*self.color_accent, alpha), detail_points)
        
        # Pequenos LEDs
        led_positions = [
            (center[0] - self.radius * 0.4, center[1]),
            (center[0] + self.radius * 0.4, center[1])
        ]
        for pos in led_positions:
            pygame.draw.circle(surface, (*self.color_accent, alpha), pos, 2)
    
    def _draw_heavy_ship(self, surface, alpha):
        """Desenha a nave Tanque - formato robusto"""
        center = (self.radius * 2, self.radius * 2)
        
        # Corpo principal - formato retangular robusto
        main_rect = pygame.Rect(center[0] - self.radius * 0.7, center[1] - self.radius,
                               self.radius * 1.4, self.radius * 2)
        pygame.draw.rect(surface, (*self.color_primary, alpha), main_rect)
        pygame.draw.rect(surface, (*self.color_secondary, alpha), main_rect, 2)
        
        # Proa pontuda
        nose_points = [
            (center[0] - self.radius * 0.7, center[1] - self.radius),
            (center[0], center[1] - self.radius * 1.3),
            (center[0] + self.radius * 0.7, center[1] - self.radius)
        ]
        pygame.draw.polygon(surface, (*self.color_primary, alpha), nose_points)
        pygame.draw.polygon(surface, (*self.color_secondary, alpha), nose_points, 2)
        
        # Canhões duplos
        cannon_left_rect = pygame.Rect(center[0] - self.radius * 1.1, center[1] - self.radius * 0.3,
                                      self.radius * 0.4, self.radius * 0.6)
        cannon_right_rect = pygame.Rect(center[0] + self.radius * 0.7, center[1] - self.radius * 0.3,
                                       self.radius * 0.4, self.radius * 0.6)
        
        pygame.draw.rect(surface, (*self.color_secondary, alpha), cannon_left_rect)
        pygame.draw.rect(surface, (*self.color_secondary, alpha), cannon_right_rect)
        
        # Detalhes do cockpit
        cockpit_rect = pygame.Rect(center[0] - self.radius * 0.3, center[1] - self.radius * 0.5,
                                  self.radius * 0.6, self.radius * 0.8)
        pygame.draw.rect(surface, (*self.color_accent, alpha), cockpit_rect, 2)
        
        # Luzes de status
        pygame.draw.circle(surface, (*self.color_accent, alpha), 
                          (center[0] - self.radius * 0.2, center[1]), 2)
        pygame.draw.circle(surface, (*self.color_accent, alpha), 
                          (center[0] + self.radius * 0.2, center[1]), 2)
