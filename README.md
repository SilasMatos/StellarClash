# StellarClash 🚀

Um jogo de tiro espacial de cima para baixo (top-down shooter) inspirado em clássicos como Asteroids e Space Invaders.

## Como Jogar

### Controles

- **WASD** ou **Setas do teclado**: Mover a nave
- **ESPAÇO**: Atirar lasers
- **ESC**: Pausar/voltar ao menu
- **R**: Reiniciar (na tela de Game Over)

### Objetivo

Sobreviva o maior tempo possível destruindo asteroides e naves inimigas para acumular a maior pontuação!

### Inimigos

- **Asteroides**: Quebram em pedaços menores quando atingidos
- **Naves Inimigas Básicas**: Movimento simples e tiros ocasionais
- **Naves Inimigas Avançadas**: Movimento em zigzag e mais resistentes

### Power-ups

Destruir inimigos pode dropar power-ups especiais:

- **Tiro Triplo** (Azul claro): Sua nave dispara três lasers em cone por 10 segundos
- **Escudo de Energia** (Azul): Cria um campo de força que absorve um impacto
- **Bomba de Nêutrons** (Roxo): Destrói todos os inimigos visíveis na tela

### Pontuação

- Asteroide pequeno: 10 pontos
- Asteroide médio: 20 pontos
- Asteroide grande: 30 pontos
- Nave inimiga: 50 pontos

### Dificuldade

A cada onda, mais inimigos aparecem e com maior frequência!

## Instalação e Execução

### Pré-requisitos

- Python 3.7 ou superior
- Pygame

### Instalar dependências

```bash
pip install pygame numpy
```

### Executar o jogo

```bash
python main.py
```

## Características

### Visuais

- Fundo estrelado com efeito parallax
- Partículas e efeitos de explosão
- Interface limpa e informativa
- Efeitos visuais para power-ups

### Áudio

- Sons sintéticos gerados pelo próprio jogo
- Efeitos sonoros para laser, explosão, power-up e impacto
- Não requer arquivos de áudio externos

### Recursos

- Sistema de ondas com dificuldade crescente
- Salvamento automático da pontuação máxima
- Múltiplos tipos de inimigos e power-ups
- Sistema de vidas e invulnerabilidade temporária
- Pausa e reinício do jogo

## Desenvolvido com

- **Python 3**
- **Pygame** - Engine de jogos
- **NumPy** - Cálculos matemáticos

---

Divirta-se explorando o espaço e destruindo asteroides! 🌟
