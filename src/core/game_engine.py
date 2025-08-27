"""
Engine principal do jogo usando Facade Pattern
"""
import pygame
import sys
import random
from .constants import *
from .game_states import *
from ..entities.player import Player
from ..entities.bullet import Bullet
from ..entities.asteroid import Asteroid
from ..entities.enemy import Enemy
from ..entities.powerup import PowerUp
from ..entities.star import Star
from ..effects.explosions import ExplosionEffect
from ..systems.sound_manager import SoundManager
from ..systems.screen_shake import ScreenShake
from ..ui.hud import HUD
from ..utils.vector2 import Vector2


class GameEngine:
    """Engine principal do jogo (Facade Pattern)"""
    
    def __init__(self):
        # Inicialização do Pygame
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Configurações da tela
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("StellarClash")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Sistemas
        self.sound_manager = SoundManager()
        self.screen_shake = ScreenShake()
        
        # Fontes
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        # UI
        self.hud = HUD(self.font_large, self.font_medium, self.font_small)
        
        # Estados do jogo
        self.current_state = GameState.MENU
        self.states = {
            GameState.MENU: MenuState(),
            GameState.PLAYING: PlayingState(),
            GameState.GAME_OVER: GameOverState(),
            GameState.PAUSED: PausedState()
        }
        
        # Estrelas do fundo
        self.stars = [Star() for _ in range(200)]
        
        # Inicializar jogo
        self.reset_game()
    
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
        self.wave_timer = 0
        self.next_wave_delay = WAVE_DELAY
        
        # Spawning
        self.asteroid_spawn_timer = 0
        self.asteroid_spawn_rate = ASTEROID_SPAWN_RATE
        self.enemy_spawn_timer = 0
        self.enemy_spawn_rate = ENEMY_SPAWN_RATE
        
        # Reset screen shake
        self.screen_shake.reset()
    
    def change_state(self, new_state):
        """Muda o estado do jogo"""
        if new_state == GameState.PLAYING:
            if self.current_state != GameState.PAUSED:
                self.reset_game()
        elif new_state == GameState.GAME_OVER:
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            self.states[GameState.GAME_OVER].timer = 0
        
        self.current_state = new_state
    
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
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
        
        # Delegar eventos para o estado atual
        self.states[self.current_state].handle_events(self, events)
    
    def update(self, dt):
        """Atualiza o jogo"""
        # Atualizar screen shake
        self.screen_shake.update(dt)
        
        # Delegar atualização para o estado atual
        self.states[self.current_state].update(self, dt)
    
    def update_game_logic(self, dt):
        """Atualiza a lógica do jogo (chamado pelo PlayingState)"""
        keys_pressed = pygame.key.get_pressed()
        
        # Atualizar jogador
        self.player.update(dt, keys_pressed)
        
        # Atualizar projéteis
        self.bullets = [b for b in self.bullets if b.alive]
        self.enemy_bullets = [b for b in self.enemy_bullets if b.alive]
        
        for bullet in self.bullets:
            bullet.update(dt)
        for bullet in self.enemy_bullets:
            bullet.update(dt)
        
        # Atualizar e processar colisões
        self._update_asteroids(dt)
        self._update_enemies(dt)
        self._update_powerups(dt)
        self._check_player_collisions()
        
        # Atualizar explosões
        self.explosions = [e for e in self.explosions if not e.update(dt)]
        
        # Atualizar estrelas
        for star in self.stars:
            star.update(dt)
        
        # Spawning
        self._handle_spawning(dt)
        
        # Aumentar dificuldade
        self._handle_wave_progression(dt)
    
    def _update_asteroids(self, dt):
        """Atualiza asteroides e suas colisões"""
        new_asteroids = []
        
        for asteroid in self.asteroids[:]:
            if not asteroid.alive or asteroid.is_off_screen():
                if asteroid in self.asteroids:
                    self.asteroids.remove(asteroid)
                continue
            
            asteroid.update(dt)
            
            # Verificar colisão com balas do jogador
            for bullet in self.bullets[:]:
                if bullet.owner == "player" and asteroid.check_collision(bullet):
                    self.bullets.remove(bullet)
                    bullet.alive = False
                    
                    children = asteroid.take_damage()
                    if not asteroid.alive:
                        self.asteroids.remove(asteroid)
                        self.score += asteroid.size * 10
                        self.sound_manager.play_sound('explosion')
                        self.explosions.append(ExplosionEffect(asteroid.pos.x, asteroid.pos.y, asteroid.size * 0.5))
                        self.screen_shake.add_shake(asteroid.size * 2, 0.2)
                        
                        # Chance de dropar power-up
                        if random.random() < POWERUP_DROP_CHANCE_ASTEROID:
                            powerup_type = random.choice(["triple_shot", "shield", "neutron_bomb"])
                            self.powerups.append(PowerUp(asteroid.pos.x, asteroid.pos.y, powerup_type))
                        
                        # Adicionar asteroides filhos se houver
                        if children:
                            new_asteroids.extend(children)
                    break
        
        self.asteroids.extend(new_asteroids)
    
    def _update_enemies(self, dt):
        """Atualiza inimigos e suas colisões"""
        for enemy in self.enemies[:]:
            if not enemy.alive or enemy.is_off_screen():
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
                continue
            
            enemy.update(dt, self.player.pos)
            
            # Inimigo atira
            enemy_bullets = enemy.shoot(self.player.pos)
            self.enemy_bullets.extend(enemy_bullets)
            
            # Verificar colisão com balas do jogador
            for bullet in self.bullets[:]:
                if bullet.owner == "player" and enemy.check_collision(bullet):
                    self.bullets.remove(bullet)
                    bullet.alive = False
                    
                    if enemy.take_damage():
                        self.enemies.remove(enemy)
                        self.score += 50
                        self.sound_manager.play_sound('explosion')
                        self.explosions.append(ExplosionEffect(enemy.pos.x, enemy.pos.y))
                        self.screen_shake.add_shake(3, 0.15)
                        
                        # Chance de dropar power-up
                        if random.random() < POWERUP_DROP_CHANCE_ENEMY:
                            powerup_type = random.choice(["triple_shot", "shield", "neutron_bomb"])
                            self.powerups.append(PowerUp(enemy.pos.x, enemy.pos.y, powerup_type))
                    break
    
    def _update_powerups(self, dt):
        """Atualiza power-ups e suas colisões"""
        for powerup in self.powerups[:]:
            if not powerup.alive or powerup.is_off_screen():
                if powerup in self.powerups:
                    self.powerups.remove(powerup)
                continue
            
            powerup.update(dt)
            
            # Verificar colisão com jogador
            if powerup.check_collision(self.player):
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
                    self.screen_shake.add_shake(15, 0.8)
                else:
                    self.player.collect_powerup(powerup.type)
                
                self.sound_manager.play_sound('powerup')
    
    def _check_player_collisions(self):
        """Verifica colisões do jogador"""
        # Colisão com asteroides
        for asteroid in self.asteroids:
            if self.player.check_collision(asteroid):
                if self.player.take_damage():
                    self.sound_manager.play_sound('hit')
                    self.screen_shake.add_shake(5, 0.3)
                if not self.player.alive:
                    self.change_state(GameState.GAME_OVER)
                break
        
        # Colisão com inimigos
        for enemy in self.enemies:
            if self.player.check_collision(enemy):
                if self.player.take_damage():
                    self.sound_manager.play_sound('hit')
                    self.screen_shake.add_shake(5, 0.3)
                if not self.player.alive:
                    self.change_state(GameState.GAME_OVER)
                break
        
        # Colisão com balas inimigas
        for bullet in self.enemy_bullets[:]:
            if self.player.check_collision(bullet):
                self.enemy_bullets.remove(bullet)
                if self.player.take_damage():
                    self.sound_manager.play_sound('hit')
                    self.screen_shake.add_shake(3, 0.2)
                if not self.player.alive:
                    self.change_state(GameState.GAME_OVER)
                break
    
    def _handle_spawning(self, dt):
        """Gerencia o spawn de entidades"""
        # Spawn de asteroides
        self.asteroid_spawn_timer += dt
        if self.asteroid_spawn_timer >= self.asteroid_spawn_rate:
            self.asteroid_spawn_timer = 0
            self._spawn_asteroid()
        
        # Spawn de inimigos
        self.enemy_spawn_timer += dt
        if self.enemy_spawn_timer >= self.enemy_spawn_rate:
            self.enemy_spawn_timer = 0
            self._spawn_enemy()
    
    def _handle_wave_progression(self, dt):
        """Gerencia a progressão das ondas"""
        self.wave_timer += dt
        if self.wave_timer >= self.next_wave_delay:
            self.wave += 1
            self.wave_timer = 0
            self.asteroid_spawn_rate = max(0.5, self.asteroid_spawn_rate - 0.1)
            self.enemy_spawn_rate = max(1.0, self.enemy_spawn_rate - 0.1)
    
    def _spawn_asteroid(self):
        """Spawna um asteroide"""
        x = random.randint(0, SCREEN_WIDTH)
        y = -50
        size = random.choices([1, 2, 3], weights=[50, 30, 20])[0]
        self.asteroids.append(Asteroid(x, y, size))
    
    def _spawn_enemy(self):
        """Spawna um inimigo"""
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = -50
        enemy_type = random.choices(["basic", "advanced"], weights=[70, 30])[0]
        self.enemies.append(Enemy(x, y, enemy_type))
    
    def draw(self):
        """Desenha o jogo"""
        # Delegar desenho para o estado atual
        self.states[self.current_state].draw(self)
    
    def draw_game_scene(self):
        """Desenha a cena do jogo (chamado pelos estados)"""
        self.screen.fill(BLACK)
        
        # Create a surface for screen shake effect
        game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        game_surface.fill(BLACK)
        
        # Desenhar no surface do jogo
        for star in self.stars:
            star.draw(game_surface)
        
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
        offset = self.screen_shake.get_offset()
        shake_x = int(offset.x)
        shake_y = int(offset.y)
        self.screen.blit(game_surface, (shake_x, shake_y))
        
        # HUD (drawn on main screen, not affected by shake)
        self.hud.draw_game_hud(self.screen, self.player, self.score, self.high_score, self.wave)
    
    def run(self):
        """Loop principal do jogo"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time em segundos
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
