
import pygame
import random
import math
import sys
import os
import numpy as np
from typing import List, Tuple
from enum import Enum

# Inicialização do Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Constantes da tela
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (255, 0, 255)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)

# Estados do jogo
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    PAUSED = 4

# Classes do jogo
class Vector2:
    """Classe para representar vetores 2D"""
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def normalize(self):
        length = self.length()
        if length > 0:
            return Vector2(self.x / length, self.y / length)
        return Vector2(0, 0)

class Particle:

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

class Bullet:
    """Classe para os projéteis melhorada"""
    def __init__(self, x, y, direction, speed=500, owner="player"):
        self.pos = Vector2(x, y)
        self.velocity = Vector2(math.cos(direction), math.sin(direction)) * speed
        self.owner = owner
        self.radius = 4 if owner == "player" else 3
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
        
        # Remove bullet if it goes off screen or lifetime expires
        return (self.pos.x < -50 or self.pos.x > SCREEN_WIDTH + 50 or
                self.pos.y < -50 or self.pos.y > SCREEN_HEIGHT + 50 or
                self.lifetime <= 0)
    
    def draw(self, screen):
        # Draw trail first
        for particle in self.trail_particles:
            particle.draw(screen)
        
        # Pulsing glow effect
        pulse = 0.8 + 0.2 * math.sin(self.pulse_timer * 15)
        glow_size = int(self.glow_radius * pulse)
        
        # Outer glow
        glow_color = (*self.color, 30)
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
    
    def get_rect(self):
        return pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, 
                          self.radius * 2, self.radius * 2)

class PowerUp:
    """Classe para power-ups melhorada"""
    def __init__(self, x, y, type_name):
        self.pos = Vector2(x, y)
        self.type = type_name
        self.velocity = Vector2(0, 50)  # Cai lentamente
        self.radius = 15
        self.lifetime = 10.0  # 10 segundos na tela
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
        
        # Remove se sair da tela ou acabar o tempo
        return (self.pos.y > SCREEN_HEIGHT + 50 or self.lifetime <= 0)
    
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
    
    def get_rect(self):
        return pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius,
                          self.radius * 2, self.radius * 2)

class Player:
    """Classe do jogador"""
    def __init__(self, x, y):
        self.pos = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.radius = 12
        self.speed = 300
        self.health = 3
        self.max_health = 3
        self.last_shot = 0
        self.shot_cooldown = 0.15  # 150ms entre tiros
        
        # Power-ups
        self.triple_shot_timer = 0
        self.shield_active = False
        self.shield_hits = 0
        self.shield_max_hits = 1
        
        # Invulnerabilidade temporária após ser atingido
        self.invulnerable_timer = 0
        self.invulnerable_duration = 2.0
        
        # Animação da nave
        self.engine_particles = []
    
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
            # Criar partículas do motor com mais variedade
            for _ in range(3):
                particle_x = self.pos.x + random.uniform(-8, 8)
                particle_y = self.pos.y + 15
                particle_vel = Vector2(
                    random.uniform(-80, 80), 
                    random.uniform(80, 150)
                )
                
                # Diferentes tipos de partículas do motor
                if random.random() < 0.7:
                    particle = Particle(particle_x, particle_y, particle_vel, ORANGE, 0.6)
                else:
                    particle = Particle(particle_x, particle_y, particle_vel, CYAN, 0.4, "spark")
                self.engine_particles.append(particle)
        
        # Atualizar partículas do motor
        self.engine_particles = [p for p in self.engine_particles if p.lifetime > 0]
        for particle in self.engine_particles:
            particle.update(dt)
    
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
    
    def take_damage(self):
        """Recebe dano"""
        if self.invulnerable_timer > 0:
            return False
        
        if self.shield_active:
            self.shield_hits += 1
            if self.shield_hits >= self.shield_max_hits:
                self.shield_active = False
                self.shield_hits = 0
            return False
        
        self.health -= 1
        self.invulnerable_timer = self.invulnerable_duration
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
        for particle in self.engine_particles:
            particle.draw(screen)
        
        # Efeito de piscar quando invulnerável
        if self.invulnerable_timer > 0:
            if int(self.invulnerable_timer * 10) % 2 == 0:
                return
        
        # Escudo com efeito pulsante
        if self.shield_active:
            pulse = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.01)
            shield_radius = int((self.radius + 8) * pulse)
            shield_color = (*BLUE[:3], int(100 * pulse))
            
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
    
    def get_rect(self):
        return pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius,
                          self.radius * 2, self.radius * 2)

class Asteroid:
    """Classe para asteroides"""
    def __init__(self, x, y, size=3):
        self.pos = Vector2(x, y)
        self.size = size  # 1=pequeno, 2=médio, 3=grande
        self.radius = size * 8 + 10
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
        
        # Wrap around screen
        if self.pos.x < -self.radius:
            self.pos.x = SCREEN_WIDTH + self.radius
        elif self.pos.x > SCREEN_WIDTH + self.radius:
            self.pos.x = -self.radius
        
        # Remove se sair muito da tela na vertical
        return self.pos.y > SCREEN_HEIGHT + self.radius
    
    def take_damage(self):
        """Recebe dano e retorna lista de asteroides filhos se quebrar"""
        self.health -= 1
        if self.health <= 0:
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
    
    def get_rect(self):
        return pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius,
                          self.radius * 2, self.radius * 2)

class Enemy:
    """Classe para naves inimigas"""
    def __init__(self, x, y, enemy_type="basic"):
        self.pos = Vector2(x, y)
        self.type = enemy_type
        self.radius = 10
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
        
        # Remove se sair da tela
        return self.pos.y > SCREEN_HEIGHT + self.radius
    
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
    
    def take_damage(self):
        """Recebe dano"""
        self.health -= 1
        return self.health <= 0
    
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
            glow_color = (*PURPLE, 100)
            pygame.draw.circle(screen, PURPLE, (int(self.pos.x), int(engine_y)), 3)
        else:
            # Basic enemy engine
            engine_y = self.pos.y - self.radius * 0.5
            pygame.draw.circle(screen, RED, (int(self.pos.x), int(engine_y)), 2)
    
    def get_rect(self):
        return pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius,
                          self.radius * 2, self.radius * 2)

class ExplosionEffect:
    """Classe para efeitos de explosão melhorada"""
    def __init__(self, x, y, size=1, explosion_type="normal"):
        self.pos = Vector2(x, y)
        self.particles = []
        self.shockwave_particles = []
        self.lifetime = 1.5
        self.max_lifetime = 1.5
        self.explosion_type = explosion_type
        self.shockwave_radius = 0
        self.shockwave_max_radius = 50 * size
        
        # Criar partículas da explosão principal
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
            self.particles.append(particle)
        
        # Partículas de fumaça para explosões maiores
        if size > 1:
            for _ in range(int(10 * size)):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(30, 100) * size
                velocity = Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
                smoke_particle = Particle(x, y, velocity, GRAY, 
                                        random.uniform(1.0, 2.0), "smoke")
                self.particles.append(smoke_particle)
        
        # Onda de choque para explosões grandes
        if explosion_type == "big" or size > 2:
            for _ in range(20):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(200, 400)
                velocity = Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
                shockwave_particle = Particle(x, y, velocity, CYAN, 0.3)
                self.shockwave_particles.append(shockwave_particle)
    
    def update(self, dt):
        self.lifetime -= dt
        
        # Update shockwave
        self.shockwave_radius += 200 * dt
        
        # Update all particles
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update(dt)
            
        self.shockwave_particles = [p for p in self.shockwave_particles if p.lifetime > 0]
        for particle in self.shockwave_particles:
            particle.update(dt)
        
        return self.lifetime <= 0 and len(self.particles) == 0
    
    def draw(self, screen):
        # Draw shockwave ring
        if self.shockwave_radius < self.shockwave_max_radius:
            alpha = max(0, 1 - (self.shockwave_radius / self.shockwave_max_radius))
            ring_color = (*WHITE, int(100 * alpha))
            if self.shockwave_radius > 5:
                pygame.draw.circle(screen, WHITE, 
                                 (int(self.pos.x), int(self.pos.y)), 
                                 int(self.shockwave_radius), 2)
        
        # Draw shockwave particles
        for particle in self.shockwave_particles:
            particle.draw(screen)
            
        # Draw main explosion particles
        for particle in self.particles:
            particle.draw(screen)

class SoundManager:
    """Gerenciador de sons"""
    def __init__(self):
        self.sounds = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        
        # Criar sons sintéticos simples
        self._create_synthetic_sounds()
    
    def _create_synthetic_sounds(self):
        """Cria sons sintéticos usando pygame"""
        # Som de laser
        self._create_laser_sound()
        self._create_explosion_sound()
        self._create_powerup_sound()
        self._create_hit_sound()
    
    def _create_laser_sound(self):
        """Cria som de laser sintético"""
        duration = 0.1
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        arr = []
        for i in range(frames):
            time = float(i) / sample_rate
            frequency = 800 - (time * 400)  # Frequência decrescente
            value = int(4096 * math.sin(frequency * 2 * math.pi * time))
            arr.append([value, value])
        
        sound_array = np.array(arr, dtype=np.int16)
        sound = pygame.sndarray.make_sound(sound_array)
        sound.set_volume(self.sfx_volume * 0.3)
        self.sounds['laser'] = sound
    
    def _create_explosion_sound(self):
        """Cria som de explosão sintético"""
        duration = 0.5
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        arr = []
        for i in range(frames):
            time = float(i) / sample_rate
            # Ruído com frequência decrescente
            noise = random.uniform(-1, 1)
            envelope = (1 - time / duration) ** 2
            value = int(4096 * noise * envelope * 0.5)
            arr.append([value, value])
        
        sound_array = np.array(arr, dtype=np.int16)
        sound = pygame.sndarray.make_sound(sound_array)
        sound.set_volume(self.sfx_volume * 0.4)
        self.sounds['explosion'] = sound
    
    def _create_powerup_sound(self):
        """Cria som de power-up sintético"""
        duration = 0.3
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        arr = []
        for i in range(frames):
            time = float(i) / sample_rate
            frequency = 400 + (time * 800)  # Frequência crescente
            value = int(4096 * math.sin(frequency * 2 * math.pi * time) * (1 - time / duration))
            arr.append([value, value])
        
        sound_array = np.array(arr, dtype=np.int16)
        sound = pygame.sndarray.make_sound(sound_array)
        sound.set_volume(self.sfx_volume * 0.4)
        self.sounds['powerup'] = sound
    
    def _create_hit_sound(self):
        """Cria som de hit sintético"""
        duration = 0.2
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        arr = []
        for i in range(frames):
            time = float(i) / sample_rate
            frequency = 200
            noise = random.uniform(-0.3, 0.3)
            envelope = (1 - time / duration) ** 3
            value = int(4096 * (math.sin(frequency * 2 * math.pi * time) + noise) * envelope)
            arr.append([value, value])
        
        sound_array = np.array(arr, dtype=np.int16)
        sound = pygame.sndarray.make_sound(sound_array)
        sound.set_volume(self.sfx_volume * 0.5)
        self.sounds['hit'] = sound
    
    def play_sound(self, sound_name):
        """Toca um efeito sonoro"""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except pygame.error:
                pass  # Ignora erros de áudio

class Game:
    """Classe principal do jogo"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("StellarClash")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        
        # Gerenciador de sons
        self.sound_manager = SoundManager()
        
        # Fonte para texto
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        # Estrelas do fundo
        self.stars = [Star() for _ in range(200)]
        
        # Variáveis do jogo
        self.reset_game()
        
        # Menu
        self.menu_blink_timer = 0
        
        # Game Over
        self.game_over_timer = 0
    
    def reset_game(self):
        """Reinicia o jogo"""
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.bullets = []
        self.enemy_bullets = []
        self.asteroids = []
        self.enemies = []
        self.powerups = []
        self.explosions = []
        
        self.score = 0
        self.high_score = self.load_high_score()
        self.wave = 1
        self.enemies_spawned = 0
        self.wave_timer = 0
        self.next_wave_delay = 3.0
        
        # Spawning
        self.asteroid_spawn_timer = 0
        self.asteroid_spawn_rate = 2.0
        self.enemy_spawn_timer = 0
        self.enemy_spawn_rate = 3.0
        
        # Screen shake system
        self.screen_shake_intensity = 0
        self.screen_shake_duration = 0
        self.screen_offset = Vector2(0, 0)
    
    def add_screen_shake(self, intensity, duration):
        """Adiciona efeito de tremida da tela"""
        self.screen_shake_intensity = max(self.screen_shake_intensity, intensity)
        self.screen_shake_duration = max(self.screen_shake_duration, duration)
    
    def update_screen_shake(self, dt):
        """Atualiza o efeito de tremida da tela"""
        if self.screen_shake_duration > 0:
            self.screen_shake_duration -= dt
            
            # Calculate shake offset
            shake_x = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
            shake_y = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
            self.screen_offset = Vector2(shake_x, shake_y)
            
            # Reduce intensity over time
            self.screen_shake_intensity *= 0.95
        else:
            self.screen_offset = Vector2(0, 0)
            self.screen_shake_intensity = 0
    
    def load_high_score(self):
        """Carrega a pontuação máxima"""
        try:
            with open("high_score.txt", "r") as f:
                return int(f.read().strip())
        except:
            return 0
    
    def save_high_score(self):
        """Salva a pontuação máxima"""
        try:
            with open("high_score.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            pass
    
    def handle_events(self):
        """Processa eventos"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.PLAYING
                        self.reset_game()
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_SPACE:
                        bullets = self.player.shoot()
                        self.bullets.extend(bullets)
                        if bullets:
                            self.sound_manager.play_sound('laser')
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED
                
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.state = GameState.PLAYING
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
    
    def update_menu(self, dt):
        """Atualiza tela do menu"""
        self.menu_blink_timer += dt
        
        # Atualizar estrelas
        for star in self.stars:
            star.update(dt)
    
    def update_game(self, dt):
        """Atualiza lógica do jogo"""
        keys_pressed = pygame.key.get_pressed()
        
        # Atualizar jogador
        self.player.update(dt, keys_pressed)
        
        # Atualizar balas
        self.bullets = [b for b in self.bullets if not b.update(dt)]
        self.enemy_bullets = [b for b in self.enemy_bullets if not b.update(dt)]
        
        # Atualizar asteroides
        new_asteroids = []
        for asteroid in self.asteroids[:]:
            if asteroid.update(dt):
                self.asteroids.remove(asteroid)
            else:
                # Verificar colisão com balas do jogador
                asteroid_rect = asteroid.get_rect()
                for bullet in self.bullets[:]:
                    if bullet.owner == "player" and asteroid_rect.colliderect(bullet.get_rect()):
                        self.bullets.remove(bullet)
                        children = asteroid.take_damage()
                        if children is not None:
                            if children:  # Se quebrou em pedaços
                                new_asteroids.extend(children)
                            self.asteroids.remove(asteroid)
                            self.score += asteroid.size * 10
                            self.sound_manager.play_sound('explosion')
                            self.explosions.append(ExplosionEffect(asteroid.pos.x, asteroid.pos.y, asteroid.size * 0.5))
                            self.add_screen_shake(asteroid.size * 2, 0.2)
                            
                            # Chance de dropar power-up
                            if random.random() < 0.15:  # 15% de chance
                                powerup_type = random.choice(["triple_shot", "shield", "neutron_bomb"])
                                self.powerups.append(PowerUp(asteroid.pos.x, asteroid.pos.y, powerup_type))
                        break
        
        self.asteroids.extend(new_asteroids)
        
        # Atualizar inimigos
        for enemy in self.enemies[:]:
            if enemy.update(dt, self.player.pos):
                self.enemies.remove(enemy)
            else:
                # Inimigo atira
                enemy_bullets = enemy.shoot(self.player.pos)
                self.enemy_bullets.extend(enemy_bullets)
                
                # Verificar colisão com balas do jogador
                enemy_rect = enemy.get_rect()
                for bullet in self.bullets[:]:
                    if bullet.owner == "player" and enemy_rect.colliderect(bullet.get_rect()):
                        self.bullets.remove(bullet)
                        if enemy.take_damage():
                            self.enemies.remove(enemy)
                            self.score += 50
                            self.sound_manager.play_sound('explosion')
                            self.explosions.append(ExplosionEffect(enemy.pos.x, enemy.pos.y))
                            self.add_screen_shake(3, 0.15)
                            
                            # Chance de dropar power-up
                            if random.random() < 0.2:  # 20% de chance
                                powerup_type = random.choice(["triple_shot", "shield", "neutron_bomb"])
                                self.powerups.append(PowerUp(enemy.pos.x, enemy.pos.y, powerup_type))
                        break
        
        # Atualizar power-ups
        for powerup in self.powerups[:]:
            if powerup.update(dt):
                self.powerups.remove(powerup)
            else:
                # Verificar colisão com jogador
                if powerup.get_rect().colliderect(self.player.get_rect()):
                    self.powerups.remove(powerup)
                    if powerup.type == "neutron_bomb":
                        # Bomba de nêutrons - destrói tudo
                        for asteroid in self.asteroids:
                            self.score += asteroid.size * 10
                            self.explosions.append(ExplosionEffect(asteroid.pos.x, asteroid.pos.y, asteroid.size * 0.5))
                        for enemy in self.enemies:
                            self.score += 50
                            self.explosions.append(ExplosionEffect(enemy.pos.x, enemy.pos.y))
                        self.asteroids.clear()
                        self.enemies.clear()
                        self.enemy_bullets.clear()
                        # Grande explosão
                        self.explosions.append(ExplosionEffect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 3, "big"))
                        self.add_screen_shake(15, 0.8)
                    else:
                        self.player.collect_powerup(powerup.type)
                    
                    self.sound_manager.play_sound('powerup')
        
        # Verificar colisões do jogador
        player_rect = self.player.get_rect()
        
        # Colisão com asteroides
        for asteroid in self.asteroids:
            if player_rect.colliderect(asteroid.get_rect()):
                if self.player.take_damage():
                    self.sound_manager.play_sound('hit')
                    self.add_screen_shake(5, 0.3)
                if self.player.health <= 0:
                    self.state = GameState.GAME_OVER
                    self.game_over_timer = 0
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
                break
        
        # Colisão com inimigos
        for enemy in self.enemies:
            if player_rect.colliderect(enemy.get_rect()):
                if self.player.take_damage():
                    self.sound_manager.play_sound('hit')
                    self.add_screen_shake(5, 0.3)
                if self.player.health <= 0:
                    self.state = GameState.GAME_OVER
                    self.game_over_timer = 0
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
                break
        
        # Colisão com balas inimigas
        for bullet in self.enemy_bullets:
            if player_rect.colliderect(bullet.get_rect()):
                self.enemy_bullets.remove(bullet)
                if self.player.take_damage():
                    self.sound_manager.play_sound('hit')
                    self.add_screen_shake(3, 0.2)
                if self.player.health <= 0:
                    self.state = GameState.GAME_OVER
                    self.game_over_timer = 0
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
                break
        
        # Atualizar explosões
        self.explosions = [e for e in self.explosions if not e.update(dt)]
        
        # Atualizar screen shake
        self.update_screen_shake(dt)
        
        # Atualizar estrelas
        for star in self.stars:
            star.update(dt)
        
        # Spawn de asteroides
        self.asteroid_spawn_timer += dt
        if self.asteroid_spawn_timer >= self.asteroid_spawn_rate:
            self.asteroid_spawn_timer = 0
            self.spawn_asteroid()
        
        # Spawn de inimigos
        self.enemy_spawn_timer += dt
        if self.enemy_spawn_timer >= self.enemy_spawn_rate:
            self.enemy_spawn_timer = 0
            self.spawn_enemy()
        
        # Aumentar dificuldade
        self.wave_timer += dt
        if self.wave_timer >= self.next_wave_delay:
            self.wave += 1
            self.wave_timer = 0
            self.asteroid_spawn_rate = max(0.5, self.asteroid_spawn_rate - 0.1)
            self.enemy_spawn_rate = max(1.0, self.enemy_spawn_rate - 0.1)
    
    def spawn_asteroid(self):
        """Spawna um asteroide"""
        x = random.randint(0, SCREEN_WIDTH)
        y = -50
        size = random.choices([1, 2, 3], weights=[50, 30, 20])[0]
        self.asteroids.append(Asteroid(x, y, size))
    
    def spawn_enemy(self):
        """Spawna um inimigo"""
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = -50
        enemy_type = random.choices(["basic", "advanced"], weights=[70, 30])[0]
        self.enemies.append(Enemy(x, y, enemy_type))
    
    def update_game_over(self, dt):
        """Atualiza tela de game over"""
        self.game_over_timer += dt
        
        # Atualizar estrelas
        for star in self.stars:
            star.update(dt)
    
    def draw_menu(self):
        """Desenha tela do menu"""
        self.screen.fill(BLACK)
        
        # Desenhar estrelas
        for star in self.stars:
            star.draw(self.screen)
        
        # Título
        title_text = self.font_large.render("STELLARCLASH", True, CYAN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title_text, title_rect)
        
        # Nave do jogador (demonstração)
        demo_player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        demo_player.draw(self.screen)
        
        # Instruções
        if int(self.menu_blink_timer * 2) % 2 == 0:
            start_text = self.font_medium.render("Pressione ESPAÇO para iniciar", True, WHITE)
            start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3))
            self.screen.blit(start_text, start_rect)
        
        # Controles
        controls = [
            "Controles:",
            "WASD ou Setas - Mover",
            "ESPAÇO - Atirar",
            "ESC - Pausar"
        ]
        
        y_offset = SCREEN_HEIGHT * 3 // 4
        for i, text in enumerate(controls):
            color = YELLOW if i == 0 else WHITE
            control_text = self.font_small.render(text, True, color)
            control_rect = control_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 30))
            self.screen.blit(control_text, control_rect)
    
    def draw_game(self):
        """Desenha o jogo"""
        self.screen.fill(BLACK)
        
        # Create a surface for screen shake effect
        game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        game_surface.fill(BLACK)
        
        # Desenhar estrelas
        for star in self.stars:
            star.draw(game_surface)
        
        # Desenhar objetos do jogo
        for explosion in self.explosions:
            explosion.draw(game_surface)
        
        for bullet in self.bullets:
            bullet.draw(game_surface)
        
        for bullet in self.enemy_bullets:
            bullet.draw(game_surface)
        
        for asteroid in self.asteroids:
            asteroid.draw(game_surface)
        
        for enemy in self.enemies:
            enemy.draw(game_surface)
        
        for powerup in self.powerups:
            powerup.draw(game_surface)
        
        self.player.draw(game_surface)
        
        # Apply screen shake offset
        shake_x = int(self.screen_offset.x)
        shake_y = int(self.screen_offset.y)
        self.screen.blit(game_surface, (shake_x, shake_y))
        
        # HUD (drawn on main screen, not affected by shake)
        self.draw_hud()
    
    def draw_hud(self):
        """Desenha interface do usuário"""
        # Pontuação
        score_text = self.font_medium.render(f"Pontuação: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # High Score
        high_score_text = self.font_small.render(f"Máxima: {self.high_score}", True, YELLOW)
        self.screen.blit(high_score_text, (10, 50))
        
        # Wave
        wave_text = self.font_small.render(f"Onda: {self.wave}", True, CYAN)
        self.screen.blit(wave_text, (10, 80))
        
        # Vida
        for i in range(self.player.health):
            heart_x = SCREEN_WIDTH - 40 - (i * 30)
            pygame.draw.circle(self.screen, RED, (heart_x, 30), 10)
        
        # Power-ups ativos
        y_offset = 120
        if self.player.triple_shot_timer > 0:
            triple_text = self.font_small.render(f"Tiro Triplo: {self.player.triple_shot_timer:.1f}s", True, CYAN)
            self.screen.blit(triple_text, (10, y_offset))
            y_offset += 30
        
        if self.player.shield_active:
            shield_text = self.font_small.render("Escudo Ativo", True, BLUE)
            self.screen.blit(shield_text, (10, y_offset))
    
    def draw_game_over(self):
        """Desenha tela de game over"""
        self.screen.fill(BLACK)
        
        # Desenhar estrelas
        for star in self.stars:
            star.draw(self.screen)
        
        # Game Over
        game_over_text = self.font_large.render("FIM DE JOGO", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Pontuação final
        final_score_text = self.font_medium.render(f"Pontuação Final: {self.score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(final_score_text, final_score_rect)
        
        # High Score
        if self.score == self.high_score:
            new_record_text = self.font_medium.render("NOVO RECORDE!", True, YELLOW)
            new_record_rect = new_record_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(new_record_text, new_record_rect)
        else:
            high_score_text = self.font_small.render(f"Pontuação Máxima: {self.high_score}", True, YELLOW)
            high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(high_score_text, high_score_rect)
        
        # Instruções
        if self.game_over_timer > 2.0:  # Espera 2 segundos antes de mostrar
            restart_text = self.font_medium.render("Pressione R para reiniciar", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3))
            self.screen.blit(restart_text, restart_rect)
            
            menu_text = self.font_small.render("Pressione ESC para voltar ao menu", True, GRAY)
            menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3 + 50))
            self.screen.blit(menu_text, menu_rect)
    
    def draw_paused(self):
        """Desenha tela de pausa"""
        # Desenha o jogo em cinza
        self.draw_game()
        
        # Overlay de pausa
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Texto de pausa
        paused_text = self.font_large.render("PAUSADO", True, WHITE)
        paused_rect = paused_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(paused_text, paused_rect)
        
        resume_text = self.font_medium.render("Pressione ESC para continuar", True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(resume_text, resume_rect)
    
    def run(self):
        """Loop principal do jogo"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time em segundos
            
            self.handle_events()
            
            # Atualizar baseado no estado
            if self.state == GameState.MENU:
                self.update_menu(dt)
                self.draw_menu()
            elif self.state == GameState.PLAYING:
                self.update_game(dt)
                self.draw_game()
            elif self.state == GameState.GAME_OVER:
                self.update_game_over(dt)
                self.draw_game_over()
            elif self.state == GameState.PAUSED:
                self.draw_paused()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
