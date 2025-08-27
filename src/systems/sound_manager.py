"""
Sistema de gerenciamento de sons usando Singleton Pattern
"""
import pygame
import numpy as np
import math
import random


class SoundManager:
    """Gerenciador de sons (Singleton)"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.sounds = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        
        # Criar sons sintéticos simples
        self._create_synthetic_sounds()
        self._initialized = True
    
    def _create_synthetic_sounds(self):
        """Cria sons sintéticos usando pygame"""
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
    
    def set_sfx_volume(self, volume):
        """Define o volume dos efeitos sonoros"""
        self.sfx_volume = max(0, min(1, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
    
    def set_music_volume(self, volume):
        """Define o volume da música"""
        self.music_volume = max(0, min(1, volume))
        pygame.mixer.music.set_volume(self.music_volume)
