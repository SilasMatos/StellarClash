#!/usr/bin/env python3
"""
StellarClash - Jogo de Tiro Espacial
Arquivo principal de inicialização do jogo
"""

from src.core.game_engine import GameEngine


def main():
    """Função principal do jogo"""
    try:
        game = GameEngine()
        game.run()
    except Exception as e:
        print(f"Erro ao executar o jogo: {e}")
        input("Pressione Enter para sair...")


if __name__ == "__main__":
    main()
