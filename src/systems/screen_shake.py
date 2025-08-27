"""
Sistema de Screen Shake para efeitos de impacto
"""
import random
from ..utils.vector2 import Vector2


class ScreenShake:
    """Sistema de tremida da tela"""
    
    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.offset = Vector2(0, 0)
    
    def add_shake(self, intensity, duration):
        """Adiciona efeito de tremida da tela"""
        self.intensity = max(self.intensity, intensity)
        self.duration = max(self.duration, duration)
    
    def update(self, dt):
        """Atualiza o efeito de tremida da tela"""
        if self.duration > 0:
            self.duration -= dt
            
            # Calculate shake offset
            shake_x = random.uniform(-self.intensity, self.intensity)
            shake_y = random.uniform(-self.intensity, self.intensity)
            self.offset = Vector2(shake_x, shake_y)
            
            # Reduce intensity over time
            self.intensity *= 0.95
        else:
            self.offset = Vector2(0, 0)
            self.intensity = 0
    
    def get_offset(self):
        """Retorna o offset atual da tremida"""
        return self.offset
    
    def reset(self):
        """Reseta o sistema de tremida"""
        self.intensity = 0
        self.duration = 0
        self.offset = Vector2(0, 0)
