"""
Estados do jogo usando State Pattern
"""
from enum import Enum
from abc import ABC, abstractmethod


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    PAUSED = 4


class State(ABC):
    """Classe base para estados do jogo"""
    
    @abstractmethod
    def handle_events(self, game, events):
        """Processa eventos específicos do estado"""
        pass
    
    @abstractmethod
    def update(self, game, dt):
        """Atualiza lógica específica do estado"""
        pass
    
    @abstractmethod
    def draw(self, game):
        """Desenha elementos específicos do estado"""
        pass


class MenuState(State):
    """Estado do menu principal"""
    
    def __init__(self):
        self.blink_timer = 0
    
    def handle_events(self, game, events):
        import pygame
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.change_state(GameState.PLAYING)
    
    def update(self, game, dt):
        self.blink_timer += dt
        # Atualizar estrelas
        for star in game.stars:
            star.update(dt)
    
    def draw(self, game):
        from ..core.constants import BLACK, CYAN, WHITE, YELLOW, GRAY, SCREEN_WIDTH, SCREEN_HEIGHT
        from ..entities.player import Player
        
        game.screen.fill(BLACK)
        
        # Desenhar estrelas
        for star in game.stars:
            star.draw(game.screen)
        
        # Título
        title_text = game.font_large.render("STELLARCLASH", True, CYAN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        game.screen.blit(title_text, title_rect)
        
        # Nave demonstrativa
        demo_player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        demo_player.draw(game.screen)
        
        # Instruções piscantes
        if int(self.blink_timer * 2) % 2 == 0:
            start_text = game.font_medium.render("Pressione ESPAÇO para iniciar", True, WHITE)
            start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3))
            game.screen.blit(start_text, start_rect)
        
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
            control_text = game.font_small.render(text, True, color)
            control_rect = control_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 30))
            game.screen.blit(control_text, control_rect)


class PlayingState(State):
    """Estado de jogo ativo"""
    
    def handle_events(self, game, events):
        import pygame
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets = game.player.shoot()
                    game.bullets.extend(bullets)
                    if bullets:
                        game.sound_manager.play_sound('laser')
                elif event.key == pygame.K_ESCAPE:
                    game.change_state(GameState.PAUSED)
    
    def update(self, game, dt):
        game.update_game_logic(dt)
    
    def draw(self, game):
        game.draw_game_scene()


class GameOverState(State):
    """Estado de fim de jogo"""
    
    def __init__(self):
        self.timer = 0
    
    def handle_events(self, game, events):
        import pygame
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.change_state(GameState.PLAYING)
                elif event.key == pygame.K_ESCAPE:
                    game.change_state(GameState.MENU)
    
    def update(self, game, dt):
        self.timer += dt
        # Atualizar estrelas
        for star in game.stars:
            star.update(dt)
    
    def draw(self, game):
        from ..core.constants import BLACK, RED, WHITE, YELLOW, GRAY, SCREEN_WIDTH, SCREEN_HEIGHT
        
        game.screen.fill(BLACK)
        
        # Desenhar estrelas
        for star in game.stars:
            star.draw(game.screen)
        
        # Game Over
        game_over_text = game.font_large.render("FIM DE JOGO", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        game.screen.blit(game_over_text, game_over_rect)
        
        # Pontuação final
        final_score_text = game.font_medium.render(f"Pontuação Final: {game.score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        game.screen.blit(final_score_text, final_score_rect)
        
        # High Score
        if game.score == game.high_score:
            new_record_text = game.font_medium.render("NOVO RECORDE!", True, YELLOW)
            new_record_rect = new_record_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            game.screen.blit(new_record_text, new_record_rect)
        else:
            high_score_text = game.font_small.render(f"Pontuação Máxima: {game.high_score}", True, YELLOW)
            high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            game.screen.blit(high_score_text, high_score_rect)
        
        # Instruções
        if self.timer > 2.0:
            restart_text = game.font_medium.render("Pressione R para reiniciar", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3))
            game.screen.blit(restart_text, restart_rect)
            
            menu_text = game.font_small.render("Pressione ESC para voltar ao menu", True, GRAY)
            menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3 + 50))
            game.screen.blit(menu_text, menu_rect)


class PausedState(State):
    """Estado de pausa"""
    
    def handle_events(self, game, events):
        import pygame
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.change_state(GameState.PLAYING)
    
    def update(self, game, dt):
        pass  # Jogo pausado, não atualiza nada
    
    def draw(self, game):
        from ..core.constants import BLACK, WHITE, SCREEN_WIDTH, SCREEN_HEIGHT
        import pygame
        
        # Desenha o jogo em cinza
        game.draw_game_scene()
        
        # Overlay de pausa
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        game.screen.blit(overlay, (0, 0))
        
        # Texto de pausa
        paused_text = game.font_large.render("PAUSADO", True, WHITE)
        paused_rect = paused_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        game.screen.blit(paused_text, paused_rect)
        
        resume_text = game.font_medium.render("Pressione ESC para continuar", True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        game.screen.blit(resume_text, resume_rect)
