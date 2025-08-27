"""
Sistema de interface de usuário
"""
import pygame
from ..core.constants import *


class HUD:
    """Sistema de interface do usuário"""
    
    def __init__(self, font_large, font_medium, font_small):
        self.font_large = font_large
        self.font_medium = font_medium
        self.font_small = font_small
    
    def draw_game_hud(self, screen, player, score, high_score, wave):
        """Desenha a interface durante o jogo"""
        # Pontuação
        score_text = self.font_medium.render(f"Pontuação: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # High Score
        high_score_text = self.font_small.render(f"Máxima: {high_score}", True, YELLOW)
        screen.blit(high_score_text, (10, 50))
        
        # Wave
        wave_text = self.font_small.render(f"Onda: {wave}", True, CYAN)
        screen.blit(wave_text, (10, 80))
        
        # Vida
        for i in range(player.health):
            heart_x = SCREEN_WIDTH - 40 - (i * 30)
            pygame.draw.circle(screen, RED, (heart_x, 30), 10)
        
        # Power-ups ativos
        y_offset = 120
        if player.triple_shot_timer > 0:
            triple_text = self.font_small.render(f"Tiro Triplo: {player.triple_shot_timer:.1f}s", True, CYAN)
            screen.blit(triple_text, (10, y_offset))
            y_offset += 30
        
        if player.shield_active:
            shield_text = self.font_small.render("Escudo Ativo", True, BLUE)
            screen.blit(shield_text, (10, y_offset))
    
    def draw_menu_title(self, screen):
        """Desenha o título do menu"""
        title_text = self.font_large.render("STELLARCLASH", True, CYAN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(title_text, title_rect)
    
    def draw_game_over_screen(self, screen, score, high_score, timer):
        """Desenha a tela de game over"""
        # Game Over
        game_over_text = self.font_large.render("FIM DE JOGO", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(game_over_text, game_over_rect)
        
        # Pontuação final
        final_score_text = self.font_medium.render(f"Pontuação Final: {score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(final_score_text, final_score_rect)
        
        # High Score
        if score == high_score:
            new_record_text = self.font_medium.render("NOVO RECORDE!", True, YELLOW)
            new_record_rect = new_record_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            screen.blit(new_record_text, new_record_rect)
        else:
            high_score_text = self.font_small.render(f"Pontuação Máxima: {high_score}", True, YELLOW)
            high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            screen.blit(high_score_text, high_score_rect)
        
        # Instruções
        if timer > 2.0:
            restart_text = self.font_medium.render("Pressione R para reiniciar", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3))
            screen.blit(restart_text, restart_rect)
            
            menu_text = self.font_small.render("Pressione ESC para voltar ao menu", True, GRAY)
            menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3 + 50))
            screen.blit(menu_text, menu_rect)
    
    def draw_pause_overlay(self, screen):
        """Desenha o overlay de pausa"""
        # Overlay de pausa
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Texto de pausa
        paused_text = self.font_large.render("PAUSADO", True, WHITE)
        paused_rect = paused_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(paused_text, paused_rect)
        
        resume_text = self.font_medium.render("Pressione ESC para continuar", True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(resume_text, resume_rect)
