"""
Documentação da Arquitetura do StellarClash
============================================

PADRÕES DE PROJETO IMPLEMENTADOS:

1. STATE PATTERN (src/core/game_states.py)
   ├── State (ABC) - Interface base para estados
   ├── MenuState - Estado do menu principal
   ├── PlayingState - Estado de jogo ativo
   ├── GameOverState - Estado de fim de jogo
   └── PausedState - Estado de pausa

2. SINGLETON PATTERN (src/systems/sound_manager.py)
   └── SoundManager - Única instância para gerenciar sons

3. ENTITY PATTERN (src/entities/)
   ├── Entity (ABC) - Classe base para todas as entidades
   ├── Player - Herda de Entity
   ├── Bullet - Herda de Entity
   ├── Asteroid - Herda de Entity
   ├── Enemy - Herda de Entity
   └── PowerUp - Herda de Entity

4. FACADE PATTERN (src/core/game_engine.py)
   └── GameEngine - Simplifica acesso a todos os subsistemas

5. TEMPLATE METHOD PATTERN (src/entities/entity.py)
   └── Entity define estrutura comum (update, draw, collision)

6. FACTORY METHOD PATTERN
   ├── Asteroid.take_damage() - Cria asteroides filhos
   ├── Enemy.**init**() - Diferentes tipos de inimigos
   └── PowerUp.**init**() - Diferentes tipos de power-ups

ESTRUTURA DE RESPONSABILIDADES:

Core/
├── constants.py - Configurações globais centralizadas
├── game_states.py - Máquina de estados do jogo
└── game_engine.py - Orquestrador principal (Facade)

Entities/
├── entity.py - Template para todas as entidades
├── player.py - Lógica específica do jogador
├── bullet.py - Comportamento dos projéteis
├── asteroid.py - Física e fragmentação dos asteroides
├── enemy.py - IA e padrões de movimento dos inimigos
├── powerup.py - Efeitos e visualização dos power-ups
└── star.py - Elementos visuais do fundo

Effects/
├── particles.py - Sistema de partículas reutilizável
└── explosions.py - Efeitos de explosão compostos

Systems/
├── sound_manager.py - Gerenciamento centralizado de áudio
└── screen_shake.py - Efeitos de impacto visual

UI/
└── hud.py - Interface de usuário e menus

Utils/
└── vector2.py - Operações matemáticas vetoriais

BENEFÍCIOS DA ARQUITETURA:

✅ MANUTENIBILIDADE

- Código organizado por responsabilidades
- Fácil localização de bugs
- Mudanças isoladas em módulos específicos

✅ EXTENSIBILIDADE

- Novos tipos de entidades facilmente adicionáveis
- Sistema de partículas reutilizável
- Estados de jogo modulares

✅ TESTABILIDADE

- Componentes isolados podem ser testados unitariamente
- Dependências claramente definidas
- Mocks podem ser criados facilmente

✅ REUTILIZAÇÃO

- Sistema de partículas usado por múltiplas entidades
- Classe Entity base reutilizada por todas as entidades
- SoundManager usado globalmente

✅ PERFORMANCE

- Singleton evita múltiplas instâncias de SoundManager
- Entity base otimiza operações comuns
- Sistema de partículas eficiente

FLUXO DE EXECUÇÃO:

1. stellar_clash.py inicializa GameEngine
2. GameEngine configura todos os subsistemas
3. Loop principal delega para o estado atual
4. Estados gerenciam eventos, atualização e renderização
5. Entidades se auto-gerenciam seguindo o padrão Entity
6. Sistemas proveem serviços centralizados
7. UI renderiza interface independentemente do jogo

PRINCÍPIOS SOLID APLICADOS:

S - Single Responsibility: Cada classe tem uma responsabilidade
O - Open/Closed: Extensível via herança e composição
L - Liskov Substitution: Entidades são intercambiáveis
I - Interface Segregation: Interfaces específicas e coesas
D - Dependency Inversion: Dependências abstratas, não concretas
"""
