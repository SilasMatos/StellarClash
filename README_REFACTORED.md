# StellarClash 🚀

Um jogo de tiro espacial top-down desenvolvido em Python com Pygame, usando padrões de projeto para uma arquitetura limpa e modular.

## 🎮 Sobre o Jogo

StellarClash é um jogo de nave espacial onde o jogador deve sobreviver ondas infinitas de asteroides e naves inimigas, coletando power-ups e tentando alcançar a maior pontuação possível.

## ✨ Características

- **Gráficos aprimorados** com sistema de partículas avançado
- **Efeitos visuais espetaculares** incluindo explosões, rastros e screen shake
- **Sistema de power-ups** com tiro triplo, escudo e bomba de nêutrons
- **Ondas progressivas** com dificuldade crescente
- **Sistema de pontuação** com high score persistente
- **Áudio sintético** gerado proceduralmente

## 🏗️ Arquitetura

O jogo foi desenvolvido seguindo padrões de projeto para manter código limpo e organizável:

### Estrutura de Pastas

```
src/
├── core/           # Núcleo do jogo
│   ├── constants.py      # Constantes globais
│   ├── game_states.py    # Estados do jogo (State Pattern)
│   └── game_engine.py    # Engine principal (Facade Pattern)
├── entities/       # Entidades do jogo
│   ├── entity.py         # Classe base (Template Method)
│   ├── player.py         # Jogador
│   ├── bullet.py         # Projéteis
│   ├── asteroid.py       # Asteroides
│   ├── enemy.py          # Inimigos
│   ├── powerup.py        # Power-ups
│   └── star.py           # Estrelas do fundo
├── effects/        # Efeitos visuais
│   ├── particles.py      # Sistema de partículas
│   └── explosions.py     # Efeitos de explosão
├── systems/        # Sistemas do jogo
│   ├── sound_manager.py  # Gerenciador de som (Singleton)
│   └── screen_shake.py   # Sistema de screen shake
├── ui/             # Interface de usuário
│   └── hud.py            # HUD e menus
└── utils/          # Utilitários
    └── vector2.py        # Matemática vetorial
```

### Padrões de Projeto Utilizados

1. **State Pattern** - Gerenciamento de estados do jogo (Menu, Playing, Game Over, Paused)
2. **Singleton Pattern** - Gerenciador de sons
3. **Entity Pattern** - Classe base para todas as entidades do jogo
4. **Facade Pattern** - GameEngine simplifica a complexidade dos subsistemas
5. **Template Method** - Classe Entity define estrutura comum
6. **Factory Method** - Criação de diferentes tipos de inimigos e power-ups

## 🎯 Controles

- **WASD** ou **Setas** - Mover a nave
- **Espaço** - Atirar
- **ESC** - Pausar/Voltar ao menu
- **R** - Reiniciar (na tela de game over)

## 🚀 Como Executar

### Requisitos

- Python 3.7+
- Pygame
- NumPy

### Instalação

1. Clone o repositório:

```bash
git clone https://github.com/SilasMatos/StellarClash.git
cd StellarClash
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Execute o jogo:

```bash
python stellar_clash.py
```

## 🎮 Gameplay

### Power-ups

- **Tiro Triplo** (Ciano) - Dispara três projéteis simultaneamente
- **Escudo** (Azul) - Protege contra um hit
- **Bomba de Nêutrons** (Roxo) - Destrói todos os inimigos na tela

### Inimigos

- **Básicos** (Vermelho) - Movimento linear, tiro lento
- **Avançados** (Roxo) - Movimento em zigzag, tiro rápido, mais resistentes

### Sistema de Pontuação

- Asteroides: 10 × tamanho pontos
- Inimigos: 50 pontos
- Bonus por sobrevivência a cada onda

## 🔧 Desenvolvimento

### Estrutura Modular

O código foi organizado em módulos independentes para facilitar:

- **Manutenção** - Cada responsabilidade em um arquivo específico
- **Testes** - Módulos podem ser testados isoladamente
- **Extensibilidade** - Fácil adição de novas funcionalidades
- **Reutilização** - Componentes podem ser reutilizados

### Princípios SOLID

- **S**ingle Responsibility - Cada classe tem uma responsabilidade específica
- **O**pen/Closed - Extensível sem modificar código existente
- **L**iskov Substitution - Subclasses podem substituir classes base
- **I**nterface Segregation - Interfaces específicas e coesas
- **D**ependency Inversion - Depende de abstrações, não implementações

## 📈 Roadmap

- [ ] Sistema de upgrades permanentes
- [ ] Diferentes tipos de naves
- [ ] Música de fundo procedural
- [ ] Multiplayer local
- [ ] Boss battles
- [ ] Sistema de achievements

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abrir um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🙏 Agradecimentos

- Pygame community pelos recursos e documentação
- Inspirado pelos clássicos jogos arcade de tiro espacial
- Padrões de projeto baseados no livro "Design Patterns" do Gang of Four

---

**Desenvolvido com ❤️ em Python**
