"""
Tipos de naves disponíveis para o jogador
"""
from enum import Enum


class ShipType(Enum):
    CLASSIC = "classic"
    VIPER = "viper"
    PHOENIX = "phoenix"
    STEALTH = "stealth"
    HEAVY = "heavy"


class ShipConfig:
    """Configurações das diferentes naves"""
    
    SHIPS = {
        ShipType.CLASSIC: {
            "name": "Clássica",
            "description": "Nave equilibrada e confiável",
            "speed": 300,
            "health": 3,
            "shot_cooldown": 0.15,
            "color_primary": (255, 255, 255),  # WHITE
            "color_secondary": (0, 255, 255),  # CYAN
            "color_accent": (255, 255, 0),     # YELLOW
            "engine_color": (255, 165, 0),     # ORANGE
            "special": "Nave padrão equilibrada"
        },
        ShipType.VIPER: {
            "name": "Víbora",
            "description": "Nave rápida e ágil",
            "speed": 400,
            "health": 2,
            "shot_cooldown": 0.12,
            "color_primary": (0, 255, 0),      # GREEN
            "color_secondary": (0, 200, 0),    # DARK GREEN
            "color_accent": (255, 255, 255),   # WHITE
            "engine_color": (0, 255, 0),       # GREEN
            "special": "Velocidade e tiro rápido"
        },
        ShipType.PHOENIX: {
            "name": "Fênix",
            "description": "Nave com escudo regenerativo",
            "speed": 250,
            "health": 4,
            "shot_cooldown": 0.18,
            "color_primary": (255, 100, 0),    # ORANGE-RED
            "color_secondary": (255, 0, 0),    # RED
            "color_accent": (255, 255, 0),     # YELLOW
            "engine_color": (255, 0, 0),       # RED
            "special": "Escudo regenera automaticamente"
        },
        ShipType.STEALTH: {
            "name": "Sombra",
            "description": "Nave furtiva com invisibilidade",
            "speed": 320,
            "health": 2,
            "shot_cooldown": 0.14,
            "color_primary": (128, 128, 128),  # GRAY
            "color_secondary": (64, 64, 64),   # DARK GRAY
            "color_accent": (0, 255, 255),     # CYAN
            "engine_color": (128, 0, 255),     # PURPLE
            "special": "Invisibilidade temporária ao tomar dano"
        },
        ShipType.HEAVY: {
            "name": "Tanque",
            "description": "Nave pesada e resistente",
            "speed": 200,
            "health": 5,
            "shot_cooldown": 0.20,
            "color_primary": (100, 100, 255),  # LIGHT BLUE
            "color_secondary": (0, 0, 255),    # BLUE
            "color_accent": (255, 255, 255),   # WHITE
            "engine_color": (0, 0, 255),       # BLUE
            "special": "Máxima resistência e tiros duplos"
        }
    }
