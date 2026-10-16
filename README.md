# Starlight Rocket

Starlight Rocket é um projeto simples desenvolvido em Python com Pygame para um trabalho da disciplina de Física.

O objetivo principal do projeto é demonstrar, de forma visual e interativa, alguns conceitos básicos de movimento e dinâmica aplicados a um foguete.

## Como o jogo funciona

O foguete começa já no ar e sofre continuamente a ação da gravidade.

O jogador pode ligar a propulsão do foguete e incliná-lo para a esquerda ou para a direita. A movimentação é calculada a partir das forças aplicadas ao foguete, considerando gravidade, empuxo, massa e consumo de combustível.

O jogo possui dois níveis.

### Nível 1

O objetivo é manter o foguete no ar por 5 segundos.

Durante esse tempo, o jogador precisa controlar a propulsão e a inclinação do foguete para evitar que ele atinja o chão.

### Nível 2

O foguete continua usando a mesma física do primeiro nível.

O objetivo é coletar 3 estrelas espalhadas pelo cenário. Ao coletar as três estrelas, a missão é concluída.

## Física utilizada

A simulação utiliza:

- gravidade de 9,8 m/s²;
- massa seca do foguete de 100.000 kg;
- combustível inicial de 100.000 kg;
- massa total variável conforme o combustível é consumido;
- consumo de 0,1% do combustível inicial por frame enquanto o motor está ligado;
- força de propulsão;
- movimento horizontal e vertical;
- inclinação de 30 graus para a esquerda ou para a direita;
- passo de tempo fixo de 1/60 de segundo;
- Segunda Lei de Newton para calcular a aceleração.

A posição do foguete é atualizada a partir da aceleração e da velocidade calculadas durante a simulação.

## Controles

- `SPACE` ou `W`: ligar a propulsão;
- `A` ou seta para a esquerda: inclinar o foguete 30 graus para a esquerda;
- `D` ou seta para a direita: inclinar o foguete 30 graus para a direita;
- `R`: reiniciar o jogo;
- `ESC`: sair.

## Tecnologias utilizadas

- Python
- Pygame Community Edition (`pygame-ce`)

## Como executar

Instale a dependência:

```bash
pip install pygame-ce
```

Depois execute:

```bash
python main.py
```

## Observação

Este projeto foi desenvolvido como atividade acadêmica e tem como foco principal a aplicação dos conceitos de Física em uma simulação simples e interativa.
